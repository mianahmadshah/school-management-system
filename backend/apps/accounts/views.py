"""
Views for the accounts app.

Handles both:
1. Template-based Full Stack Views (Login, Logout, Dashboards, Profile, Password Reset)
2. API Views (from DRF, kept for completeness)
"""
from django.contrib.auth import get_user_model, logout as auth_logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, UpdateView, RedirectView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .forms import UserProfileForm
from apps.activity_logs.models import ActivityLog

# Keep DRF imports for backward compatibility
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdminUser

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED AUTHENTICATION VIEWS
# ─────────────────────────────────────────────────────────────

class UserLoginView(LoginView):
    """
    Standard Django login view using email as the login field.
    Redirects to dashboard based on role.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        # Log successful login
        ActivityLog.log(
            user=user,
            action=ActivityLog.ActionType.LOGIN,
            model_name='CustomUser',
            object_id=user.id,
            description=f"User {user.email} logged in via Web UI.",
            request=self.request
        )
        # Redirect based on user role
        if user.role == User.Role.ADMIN:
            return reverse_lazy('admin_dashboard')
        elif user.role == User.Role.TEACHER:
            return reverse_lazy('teacher_dashboard')
        elif user.role == User.Role.STUDENT:
            return reverse_lazy('student_dashboard')
        return reverse_lazy('login')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """
    Logs out the user and redirects to login with a success message.
    """
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            ActivityLog.log(
                user=request.user,
                action=ActivityLog.ActionType.LOGOUT,
                model_name='CustomUser',
                object_id=request.user.id,
                description=f"User {request.user.email} logged out via Web UI.",
                request=request
            )
        messages.success(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# DASHBOARDS
# ─────────────────────────────────────────────────────────────

class DashboardRedirectView(LoginRequiredMixin, RedirectView):
    """
    Redirects the root '/' or '/dashboard/' to the correct dashboard based on role.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return reverse_lazy('admin_dashboard')
        elif user.role == User.Role.TEACHER:
            return reverse_lazy('teacher_dashboard')
        elif user.role == User.Role.STUDENT:
            return reverse_lazy('student_dashboard')
        return reverse_lazy('login')


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Renders the Administrator Dashboard.
    """
    template_name = 'admin_dashboard.html'

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('unauthorized')
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch actual statistics (safe imports to prevent circular dependency issues)
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        from apps.classes.models import Class
        
        context['students_count'] = Student.objects.count()
        context['teachers_count'] = Teacher.objects.count()
        context['classes_count'] = Class.objects.count()
        
        # Latest activities
        context['activity_logs'] = ActivityLog.objects.select_related('user').order_by('-timestamp')[:5]
        
        # Latest announcements
        from apps.announcements.models import Announcement
        context['announcements'] = Announcement.objects.select_related('published_by').order_by('-published_at')[:5]
        
        return context


class TeacherDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Renders the Teacher Dashboard.
    """
    template_name = 'teacher_dashboard.html'

    def test_func(self):
        return self.request.user.role == User.Role.TEACHER

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('unauthorized')
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get teacher-specific schedule & stats
        teacher = getattr(self.request.user, 'teacher_profile', None)
        if teacher:
            from apps.timetable.models import Timetable
            from apps.assignments.models import Assignment
            from apps.classes.models import Section
            
            context['classes_count'] = Section.objects.filter(section_teacher=teacher).count()
            # Fetch assigned student count
            from apps.students.models import Student
            context['students_count'] = Student.objects.filter(current_class__sections__section_teacher=teacher).distinct().count()
            context['assignments_count'] = Assignment.objects.filter(teacher=teacher).count()
            
            # Fetch schedule
            context['schedule'] = Timetable.objects.filter(teacher=teacher).select_related('class_name', 'subject')
        
        from apps.announcements.models import Announcement
        context['announcements'] = Announcement.objects.select_related('published_by').order_by('-published_at')[:5]
        return context


class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Renders the Student Dashboard.
    """
    template_name = 'student_dashboard.html'

    def test_func(self):
        return self.request.user.role == User.Role.STUDENT

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('unauthorized')
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = getattr(self.request.user, 'student_profile', None)
        if student:
            from apps.timetable.models import Timetable
            from apps.assignments.models import Assignment
            from apps.attendance.models import Attendance
            
            # Calculate attendance percentage
            total_days = Attendance.objects.filter(student=student).count()
            present_days = Attendance.objects.filter(student=student, status='PRESENT').count()
            context['attendance_percentage'] = f"{int((present_days / total_days) * 100)}%" if total_days > 0 else "N/A"
            
            # Pending assignments
            context['pending_assignments'] = Assignment.objects.filter(class_name=student.current_class).count()
            
            # Today's schedule
            context['schedule'] = Timetable.objects.filter(class_name=student.current_class).select_related('subject', 'teacher__user')
            
        from apps.announcements.models import Announcement
        context['announcements'] = Announcement.objects.select_related('published_by').order_by('-published_at')[:5]
        return context


# ─────────────────────────────────────────────────────────────
# PROFILE VIEWS
# ─────────────────────────────────────────────────────────────

class UserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Allows authenticated users to view and update their profile details.
    """
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    success_message = "Your profile has been updated successfully."

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    """
    Allows authenticated users to change their password.
    """
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')
    success_message = "Your password has been changed successfully."


# ─────────────────────────────────────────────────────────────
# BACKWARD COMPATIBLE DRF VIEWS (Kept for reference)
# ─────────────────────────────────────────────────────────────

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [IsAdminUser]
    search_fields = ['email', 'first_name', 'last_name', 'role']
    filterset_fields = ['role', 'is_active', 'gender']
    ordering_fields = ['created_at', 'first_name', 'email']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response({'error': 'You cannot delete your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(user)
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
