# 🚀 MODULE 4: ViewSets, Routers & API Endpoints - START

## 📋 MODULE 4 OVERVIEW

**Goal:** Build REST API endpoints for all 17 models using Django REST Framework

**What we'll create:**
1. ✅ Permissions classes (IsAdmin, IsTeacher, IsStudent, IsOwner)
2. ✅ ViewSets for all 17 models (CRUD operations)
3. ✅ DRF Routers for automatic URL generation
4. ✅ URL routing configuration
5. ✅ Pagination, Filtering, and Search
6. ✅ API documentation

**Result:** 60+ REST API endpoints ready for frontend consumption

---

## 📊 ENDPOINTS TO BE CREATED

### Authentication Endpoints (5)
```
POST   /api/v1/auth/login/                 - User login
POST   /api/v1/auth/logout/                - User logout
POST   /api/v1/auth/refresh/               - Refresh JWT token
POST   /api/v1/auth/password-reset/        - Reset password
GET    /api/v1/auth/me/                    - Get current user
```

### Accounts/Users (8)
```
GET    /api/v1/accounts/users/             - List all users
POST   /api/v1/accounts/users/             - Create new user
GET    /api/v1/accounts/users/{id}/        - Get user details
PUT    /api/v1/accounts/users/{id}/        - Update user
DELETE /api/v1/accounts/users/{id}/        - Delete user
PATCH  /api/v1/accounts/users/{id}/       - Partial update
GET    /api/v1/accounts/profile/           - Get own profile
PUT    /api/v1/accounts/profile/           - Update own profile
```

### Students (8)
```
GET    /api/v1/students/                   - List students
POST   /api/v1/students/                   - Create student
GET    /api/v1/students/{id}/              - Get student details
PUT    /api/v1/students/{id}/              - Update student
DELETE /api/v1/students/{id}/              - Delete student
GET    /api/v1/students/{id}/attendance/   - Student's attendance
GET    /api/v1/students/{id}/results/      - Student's results
GET    /api/v1/students/{id}/fees/         - Student's fees
```

### Teachers (5)
```
GET    /api/v1/teachers/                   - List teachers
POST   /api/v1/teachers/                   - Create teacher
GET    /api/v1/teachers/{id}/              - Get teacher details
PUT    /api/v1/teachers/{id}/              - Update teacher
DELETE /api/v1/teachers/{id}/              - Delete teacher
```

### Classes & Sections (10)
```
GET    /api/v1/classes/                    - List classes
POST   /api/v1/classes/                    - Create class
GET    /api/v1/classes/{id}/               - Get class details
PUT    /api/v1/classes/{id}/               - Update class
GET    /api/v1/classes/{id}/sections/      - Get sections in class
GET    /api/v1/sections/                   - List all sections
POST   /api/v1/sections/                   - Create section
GET    /api/v1/sections/{id}/              - Get section details
PUT    /api/v1/sections/{id}/              - Update section
GET    /api/v1/sections/{id}/students/     - Get enrolled students
```

### Subjects & Enrollment (10)
```
GET    /api/v1/subjects/                   - List subjects
POST   /api/v1/subjects/                   - Create subject
GET    /api/v1/subjects/{id}/              - Get subject details
PUT    /api/v1/subjects/{id}/              - Update subject
DELETE /api/v1/subjects/{id}/              - Delete subject
GET    /api/v1/enrollments/                - List enrollments
POST   /api/v1/enrollments/                - Enroll student
GET    /api/v1/enrollments/{id}/           - Get enrollment
PUT    /api/v1/enrollments/{id}/           - Update enrollment
DELETE /api/v1/enrollments/{id}/           - Cancel enrollment
```

### Attendance (6)
```
GET    /api/v1/attendance/                 - List attendance
POST   /api/v1/attendance/                 - Mark attendance
POST   /api/v1/attendance/bulk/            - Mark bulk attendance
GET    /api/v1/attendance/{id}/            - Get attendance record
PUT    /api/v1/attendance/{id}/            - Update attendance
GET    /api/v1/attendance/report/          - Get attendance report
```

### Examinations, Marks, Results (15)
```
GET    /api/v1/exams/                      - List exams
POST   /api/v1/exams/                      - Create exam
GET    /api/v1/exams/{id}/                 - Get exam details
PUT    /api/v1/exams/{id}/                 - Update exam
DELETE /api/v1/exams/{id}/                 - Delete exam
GET    /api/v1/marks/                      - List marks
POST   /api/v1/marks/                      - Enter marks
POST   /api/v1/marks/bulk/                 - Bulk enter marks
GET    /api/v1/marks/{id}/                 - Get mark record
PUT    /api/v1/marks/{id}/                 - Update mark
GET    /api/v1/results/                    - List results
POST   /api/v1/results/                    - Generate result
GET    /api/v1/results/{id}/               - Get result details
GET    /api/v1/results/student/{id}/       - Get student results
```

### Fees (12)
```
GET    /api/v1/fees/categories/            - List fee categories
POST   /api/v1/fees/categories/            - Create category
GET    /api/v1/fees/invoices/              - List invoices
POST   /api/v1/fees/invoices/              - Create invoice
GET    /api/v1/fees/invoices/{id}/         - Get invoice details
PUT    /api/v1/fees/invoices/{id}/         - Update invoice
POST   /api/v1/fees/payments/              - Record payment
GET    /api/v1/fees/payments/              - List payments
POST   /api/v1/fees/report/                - Generate fee report
GET    /api/v1/fees/student/{id}/          - Get student's fees
GET    /api/v1/fees/due-list/              - Get outstanding fees
```

### Announcements (5)
```
GET    /api/v1/announcements/              - List announcements
POST   /api/v1/announcements/              - Create announcement
GET    /api/v1/announcements/{id}/         - Get announcement
PUT    /api/v1/announcements/{id}/         - Update announcement
DELETE /api/v1/announcements/{id}/         - Delete announcement
```

### Assignments & Submissions (12)
```
GET    /api/v1/assignments/                - List assignments
POST   /api/v1/assignments/                - Create assignment
GET    /api/v1/assignments/{id}/           - Get assignment
PUT    /api/v1/assignments/{id}/           - Update assignment
DELETE /api/v1/assignments/{id}/           - Delete assignment
GET    /api/v1/assignments/{id}/submissions/ - Get submissions
POST   /api/v1/submissions/                - Submit assignment
GET    /api/v1/submissions/{id}/           - Get submission
PUT    /api/v1/submissions/{id}/           - Update submission
POST   /api/v1/submissions/{id}/grade/     - Grade submission
GET    /api/v1/submissions/student/{id}/   - Get student submissions
```

### Timetable (6)
```
GET    /api/v1/periods/                    - List periods
POST   /api/v1/periods/                    - Create period
GET    /api/v1/timetable/                  - List timetable
POST   /api/v1/timetable/                  - Create timetable entry
GET    /api/v1/timetable/class/{id}/       - Get class schedule
GET    /api/v1/timetable/section/{id}/     - Get section schedule
```

### Activity Logs (3)
```
GET    /api/v1/logs/                       - List activity logs
GET    /api/v1/logs/user/{id}/             - Get user's activity
GET    /api/v1/logs/object/{model}/{id}/   - Get object's activity
```

---

## 🏗️ ARCHITECTURE

```
ViewSet
  ├── queryset: Define what data this view works with
  ├── serializer_class: How to serialize the data
  ├── permission_classes: Who can access
  ├── pagination_class: How many results per page
  └── Methods:
      ├── list() - GET all
      ├── create() - POST new
      ├── retrieve() - GET one
      ├── update() - PUT/PATCH
      └── destroy() - DELETE

Router
  ├── Automatically generates URLs
  ├── Registers all ViewSets
  └── Includes(/api/v1/, api_urls)

URL Config
  └── includes(router.urls)
```

---

## 📝 FILES TO CREATE/MODIFY

### New Files:
```
backend/apps/accounts/permissions.py    - Permission classes
backend/apps/accounts/viewsets.py       - Auth ViewSets
backend/api/v1/                         - API v1 directory
  ├── __init__.py
  ├── routers.py                        - All routers combined
  ├── urls.py                           - URL configuration
  └── pagination.py                     - Pagination settings
```

### Modify Files:
```
backend/config/urls.py                  - Include /api/v1/ URLs
backend/config/settings.py              - Add pagination settings (optional)
```

### ViewSet Files (one per app):
```
backend/apps/students/viewsets.py
backend/apps/teachers/viewsets.py
backend/apps/classes/viewsets.py
backend/apps/subjects/viewsets.py
backend/apps/attendance/viewsets.py
backend/apps/examinations/viewsets.py
backend/apps/fees/viewsets.py
backend/apps/announcements/viewsets.py
backend/apps/assignments/viewsets.py
backend/apps/timetable/viewsets.py
backend/apps/activity_logs/viewsets.py
```

---

## 🔐 PERMISSION CLASSES

We'll create:
```python
class IsAdmin(BasePermission):
    """Only admins can access"""

class IsTeacher(BasePermission):
    """Only teachers can access"""

class IsStudent(BasePermission):
    """Only students can access"""

class IsOwner(BasePermission):
    """Only object owner can edit"""

class IsAdminOrReadOnly(BasePermission):
    """Admin can do anything, others can read"""

class IsAdminOrTeacherReadOnly(BasePermission):
    """Admin can do anything, teachers can read"""
```

---

## 🔍 FILTER & SEARCH

For each ViewSet, we'll add:
```python
filter_backends = [
    DjangoFilterBackend,      # Filter by fields
    SearchFilter,             # Search in fields
    OrderingFilter            # Sort by fields
]
filterset_fields = ['status', 'created_at']
search_fields = ['name', 'email']
ordering_fields = ['created_at', 'name']
ordering = ['-created_at']
```

---

## 📄 EXAMPLE ViewSet (Students)

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.students.models import Student
from apps.students.serializers import StudentSerializer
from apps.accounts.permissions import IsAdmin, IsStudent

class StudentViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Student model.
    
    Permissions:
    - Admins: Full access
    - Teachers: Read-only
    - Students: Can view/edit only their own profile
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['status', 'current_class', 'gender']
    search_fields = ['user__first_name', 'user__last_name', 'admission_number', 'user__email']
    ordering_fields = ['admission_number', 'user__first_name']
    ordering = ['admission_number']
    
    def get_permissions(self):
        """
        Override permissions per action.
        - list/retrieve: Any authenticated user
        - create/update: Only admin
        - destroy: Only admin
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get student's attendance records"""
        student = self.get_object()
        attendance = student.attendance_records.all()
        return Response({
            'total_records': attendance.count(),
            'present': attendance.filter(status='PRESENT').count(),
            'absent': attendance.filter(status='ABSENT').count(),
            'late': attendance.filter(status='LATE').count(),
            'on_leave': attendance.filter(status='LEAVE').count(),
        })
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get student's results"""
        student = self.get_object()
        results = student.results.all()
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)
```

---

## 🎯 NEXT STEPS

**Phase 1 (Now):**
1. Create permissions classes
2. Create ViewSets for core models (Students, Teachers, Classes)
3. Setup routers

**Phase 2:**
4. Create remaining ViewSets
5. Add filtering and search
6. Configure pagination

**Phase 3:**
7. Test all endpoints with Postman
8. Add API documentation
9. Performance optimization

---

## ⏱️ ESTIMATED TIME: 4-6 hours

Breaking down:
- Permissions: 30 min
- ViewSets: 2 hours
- Routers & URLs: 1 hour
- Testing: 1 hour
- Documentation: 30 min

---

## ✨ READY TO START?

Proceeding with implementation...
