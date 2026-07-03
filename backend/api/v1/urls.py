"""
URL configuration for API v1.

Include this in the main URLs configuration with:
    path('api/v1/', include('api.v1.urls'))
"""
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.v1.routers import router


@api_view(['GET'])
def api_root(request):
    """
    API Root endpoint with documentation.
    
    Welcome to School Management System API v1.
    
    Available endpoints:
    - /api/v1/users/                - User management
    - /api/v1/students/             - Student management
    - /api/v1/teachers/             - Teacher management
    - /api/v1/classes/              - Class management
    - /api/v1/sections/             - Section management
    - /api/v1/subjects/             - Subject management
    - /api/v1/enrollments/          - Enrollment management
    - /api/v1/attendance/           - Attendance tracking
    - /api/v1/exams/                - Examination management
    - /api/v1/marks/                - Marks management
    - /api/v1/results/              - Results management
    - /api/v1/fees/                 - Fee management
    - /api/v1/announcements/        - Announcements
    - /api/v1/assignments/          - Assignment management
    - /api/v1/submissions/          - Submission management
    - /api/v1/periods/              - Period management
    - /api/v1/timetable/            - Timetable management
    - /api/v1/logs/                 - Activity logs
    
    For more details on each endpoint, visit /api/v1/{endpoint}/?format=json
    """
    return Response({
        'message': 'Welcome to School Management System API v1',
        'version': '1.0.0',
        'available_endpoints': {
            'users': request.build_absolute_uri('users/'),
            'students': request.build_absolute_uri('students/'),
            'teachers': request.build_absolute_uri('teachers/'),
            'classes': request.build_absolute_uri('classes/'),
            'sections': request.build_absolute_uri('sections/'),
            'subjects': request.build_absolute_uri('subjects/'),
            'enrollments': request.build_absolute_uri('enrollments/'),
            'attendance': request.build_absolute_uri('attendance/'),
            'exams': request.build_absolute_uri('exams/'),
            'marks': request.build_absolute_uri('marks/'),
            'results': request.build_absolute_uri('results/'),
            'fees': request.build_absolute_uri('fees/'),
            'announcements': request.build_absolute_uri('announcements/'),
            'assignments': request.build_absolute_uri('assignments/'),
            'submissions': request.build_absolute_uri('submissions/'),
            'periods': request.build_absolute_uri('periods/'),
            'timetable': request.build_absolute_uri('timetable/'),
            'logs': request.build_absolute_uri('logs/'),
        }
    })


app_name = 'api_v1'

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
]
