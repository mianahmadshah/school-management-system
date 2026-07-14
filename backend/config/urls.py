"""
Root URL configuration for School Management System.
All app URLs are included here.
Includes Web UI routes (Django templates) at the root level and DRF APIs under /api/v1/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

# Views
from apps.accounts.views import (
    UserLoginView,
    UserLogoutView,
    DashboardRedirectView,
    AdminDashboardView,
    TeacherDashboardView,
    StudentDashboardView,
    UserProfileView,
    UserPasswordChangeView,
)
from apps.students.views import (
    StudentListView,
    StudentDetailView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
)
from apps.teachers.views import (
    TeacherListView,
    TeacherDetailView,
    TeacherCreateView,
    TeacherUpdateView,
    TeacherDeleteView,
)
from apps.classes.views import (
    ClassListView,
    ClassDetailView,
    ClassCreateView,
    ClassUpdateView,
    ClassDeleteView,
    SectionCreateView,
    SectionUpdateView,
    SectionDeleteView,
)
from apps.subjects.views import (
    SubjectListView,
    SubjectDetailView,
    SubjectCreateView,
    SubjectUpdateView,
    SubjectDeleteView,
    EnrollmentCreateView,
)
from apps.attendance.views import (
    AttendanceListView,
    MarkAttendanceView,
    StudentAttendanceView,
)
from apps.examinations.views import (
    ExamListView, ExamDetailView, ExamCreateView, ExamUpdateView, ExamDeleteView,
    MarksEntryView, MarksListView,
    ResultListView, GenerateResultView, StudentResultView,
)
from apps.fees.views import (
    FeeCategoryListView, FeeCategoryCreateView, FeeCategoryUpdateView, FeeCategoryDeleteView,
    FeeStructureListView, FeeStructureCreateView,
    FeeInvoiceListView, FeeInvoiceCreateView, FeeInvoiceDetailView,
    RecordPaymentView,
)
from apps.timetable.views import (
    PeriodListView, PeriodCreateView, PeriodUpdateView, PeriodDeleteView,
    TimetableListView, TimetableCreateView, TimetableUpdateView, TimetableDeleteView,
    StudentTimetableView, TeacherTimetableView,
)
from apps.announcements.views import (
    AnnouncementListView, AnnouncementDetailView, AnnouncementCreateView, AnnouncementUpdateView, AnnouncementDeleteView,
)
from apps.assignments.views import (
    AssignmentListView, AssignmentDetailView, AssignmentCreateView, AssignmentUpdateView, AssignmentDeleteView, GradeSubmissionView,
)
from apps.reports.views import (
    ReportDashboardView, AttendanceReportView, AcademicReportView, FeeCollectionReportView,
)

urlpatterns = [
    # Django admin backend panel
    path('django-admin/', admin.site.urls),

    # ─── Web UI (Django Templates) ──────────────────────────────────────────
    path('', DashboardRedirectView.as_view(), name='dashboard_redirect'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/change-password/', UserPasswordChangeView.as_view(), name='password_change'),
    
    # Dashboards
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('student/dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),

    # Student Management
    path('admin/students/', StudentListView.as_view(), name='student_list'),
    path('admin/students/add/', StudentCreateView.as_view(), name='student_create'),
    path('admin/students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('admin/students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student_update'),
    path('admin/students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),

    # Teacher Management
    path('admin/teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('admin/teachers/add/', TeacherCreateView.as_view(), name='teacher_create'),
    path('admin/teachers/<int:pk>/', TeacherDetailView.as_view(), name='teacher_detail'),
    path('admin/teachers/<int:pk>/edit/', TeacherUpdateView.as_view(), name='teacher_update'),
    path('admin/teachers/<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher_delete'),

    # Class Management
    path('admin/classes/', ClassListView.as_view(), name='class_list'),
    path('admin/classes/add/', ClassCreateView.as_view(), name='class_create'),
    path('admin/classes/<int:pk>/', ClassDetailView.as_view(), name='class_detail'),
    path('admin/classes/<int:pk>/edit/', ClassUpdateView.as_view(), name='class_update'),
    path('admin/classes/<int:pk>/delete/', ClassDeleteView.as_view(), name='class_delete'),

    # Section Management
    path('admin/sections/add/', SectionCreateView.as_view(), name='section_create'),
    path('admin/sections/<int:pk>/edit/', SectionUpdateView.as_view(), name='section_update'),
    path('admin/sections/<int:pk>/delete/', SectionDeleteView.as_view(), name='section_delete'),

    # Subject Management
    path('admin/subjects/', SubjectListView.as_view(), name='subject_list'),
    path('admin/subjects/add/', SubjectCreateView.as_view(), name='subject_create'),
    path('admin/subjects/<int:pk>/', SubjectDetailView.as_view(), name='subject_detail'),
    path('admin/subjects/<int:pk>/edit/', SubjectUpdateView.as_view(), name='subject_update'),
    path('admin/subjects/<int:pk>/delete/', SubjectDeleteView.as_view(), name='subject_delete'),

    # Enrollment
    path('admin/enrollments/add/', EnrollmentCreateView.as_view(), name='enrollment_create'),

    # Attendance Management
    path('admin/attendance/', AttendanceListView.as_view(), name='attendance_list'),
    path('admin/attendance/mark/', MarkAttendanceView.as_view(), name='mark_attendance'),
    path('student/attendance/', StudentAttendanceView.as_view(), name='my_attendance'),

    # Examinations Management
    path('admin/exams/', ExamListView.as_view(), name='exam_list'),
    path('admin/exams/add/', ExamCreateView.as_view(), name='exam_create'),
    path('admin/exams/<int:pk>/', ExamDetailView.as_view(), name='exam_detail'),
    path('admin/exams/<int:pk>/edit/', ExamUpdateView.as_view(), name='exam_update'),
    path('admin/exams/<int:pk>/delete/', ExamDeleteView.as_view(), name='exam_delete'),

    # Marks Management
    path('admin/marks/', MarksListView.as_view(), name='marks_list'),
    path('admin/marks/entry/', MarksEntryView.as_view(), name='marks_entry'),

    # Results Management
    path('admin/results/', ResultListView.as_view(), name='result_list'),
    path('admin/results/generate/', GenerateResultView.as_view(), name='generate_result'),
    path('student/results/', StudentResultView.as_view(), name='my_results'),

    # Fee Management
    path('admin/fees/categories/', FeeCategoryListView.as_view(), name='fee_category_list'),
    path('admin/fees/categories/add/', FeeCategoryCreateView.as_view(), name='fee_category_create'),
    path('admin/fees/categories/<int:pk>/edit/', FeeCategoryUpdateView.as_view(), name='fee_category_update'),
    path('admin/fees/categories/<int:pk>/delete/', FeeCategoryDeleteView.as_view(), name='fee_category_delete'),
    path('admin/fees/structures/', FeeStructureListView.as_view(), name='fee_structure_list'),
    path('admin/fees/structures/add/', FeeStructureCreateView.as_view(), name='fee_structure_create'),
    path('admin/fees/invoices/', FeeInvoiceListView.as_view(), name='invoice_list'),
    path('admin/fees/invoices/add/', FeeInvoiceCreateView.as_view(), name='invoice_create'),
    path('admin/fees/invoices/<int:pk>/', FeeInvoiceDetailView.as_view(), name='invoice_detail'),
    path('admin/fees/invoices/<int:pk>/pay/', RecordPaymentView.as_view(), name='record_payment'),

    # Timetable Management
    path('admin/timetable/', TimetableListView.as_view(), name='timetable_list'),
    path('admin/timetable/add/', TimetableCreateView.as_view(), name='timetable_create'),
    path('admin/timetable/<int:pk>/edit/', TimetableUpdateView.as_view(), name='timetable_update'),
    path('admin/timetable/<int:pk>/delete/', TimetableDeleteView.as_view(), name='timetable_delete'),
    path('admin/periods/', PeriodListView.as_view(), name='period_list'),
    path('admin/periods/add/', PeriodCreateView.as_view(), name='period_create'),
    path('admin/periods/<int:pk>/edit/', PeriodUpdateView.as_view(), name='period_update'),
    path('admin/periods/<int:pk>/delete/', PeriodDeleteView.as_view(), name='period_delete'),
    path('student/timetable/', StudentTimetableView.as_view(), name='my_timetable'),
    path('teacher/timetable/', TeacherTimetableView.as_view(), name='teacher_timetable'),

    # Announcements
    path('admin/announcements/', AnnouncementListView.as_view(), name='announcement_list'),
    path('admin/announcements/add/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('admin/announcements/<int:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('admin/announcements/<int:pk>/edit/', AnnouncementUpdateView.as_view(), name='announcement_update'),
    path('admin/announcements/<int:pk>/delete/', AnnouncementDeleteView.as_view(), name='announcement_delete'),

    # Assignments
    path('admin/assignments/', AssignmentListView.as_view(), name='assignment_list'),
    path('admin/assignments/add/', AssignmentCreateView.as_view(), name='assignment_create'),
    path('admin/assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment_detail'),
    path('admin/assignments/<int:pk>/edit/', AssignmentUpdateView.as_view(), name='assignment_update'),
    path('admin/assignments/<int:pk>/delete/', AssignmentDeleteView.as_view(), name='assignment_delete'),
    path('admin/assignments/submissions/<int:pk>/grade/', GradeSubmissionView.as_view(), name='grade_submission'),

    # Reports
    path('admin/reports/', ReportDashboardView.as_view(), name='report_dashboard'),
    path('admin/reports/attendance/', AttendanceReportView.as_view(), name='report_attendance'),
    path('admin/reports/academic/', AcademicReportView.as_view(), name='report_academic'),
    path('admin/reports/fees/', FeeCollectionReportView.as_view(), name='report_fees'),

    # Password Reset via Email
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Permissions error
    path('unauthorized/', TemplateView.as_view(template_name='accounts/unauthorized.html'), name='unauthorized'),

    # ─── REST API Version 1 (DRF) ─────────────────────────────────────────────
    path('api/v1/', include('api.v1.urls')),
]

# ─── Error Handlers ────────────────────────────────────────
handler404 = 'config.views.error_404'
handler500 = 'config.views.error_500'
handler403 = 'config.views.error_403'

# Serve media and static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
