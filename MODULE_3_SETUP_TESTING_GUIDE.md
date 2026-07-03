"""
===================================================================
MODULE 3: SETUP AND TESTING GUIDE
===================================================================

This guide walks through completing the database setup and testing
all models before moving to API endpoints (Module 4).
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: VERIFY ALL FILES ARE IN PLACE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Check all model files exist:
   - backend/apps/accounts/models.py
   - backend/apps/students/models.py
   - backend/apps/teachers/models.py
   - backend/apps/classes/models.py
   - backend/apps/subjects/models.py
   - backend/apps/attendance/models.py
   - backend/apps/examinations/models.py
   - backend/apps/fees/models.py
   - backend/apps/announcements/models.py
   - backend/apps/assignments/models.py
   - backend/apps/timetable/models.py
   - backend/apps/activity_logs/models.py

✅ Check all serializer files exist:
   - backend/apps/*/serializers.py (12 files)

✅ Check admin.py files exist:
   - backend/apps/*/admin.py (11 files)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: CREATE DATABASE MIGRATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run these commands from the backend directory:

1. Create migration files:
   
   $ python manage.py makemigrations

   Expected output:
   ✓ Creating migrations for:
     - accounts
     - students
     - teachers
     - classes
     - subjects
     - attendance
     - examinations
     - fees
     - announcements
     - assignments
     - timetable
     - activity_logs

2. Check the migration files are created:
   
   $ ls -la backend/apps/*/migrations/

   Each app should have:
   - __init__.py
   - 0001_initial.py (or higher number)

3. Review what will be created:
   
   $ python manage.py sqlmigrate accounts 0001
   $ python manage.py sqlmigrate students 0001
   
   (Replace with other apps to see SQL)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: APPLY MIGRATIONS TO DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Apply all migrations:
   
   $ python manage.py migrate

   Expected output:
   ✓ Operations to perform:
       Apply all migrations...
     Running migrations:
       Applying accounts.0001_initial... OK
       Applying students.0001_initial... OK
       ... (all apps)

2. Verify tables were created:
   
   $ python manage.py dbshell
   
   Inside SQLite shell:
   > .tables
   
   Should see: accounts_customuser, students_student, teachers_teacher, 
              classes_class, classes_section, etc.

3. Exit shell:
   > .exit


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: CREATE SUPERUSER (ADMIN ACCOUNT)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Create admin user:
   
   $ python manage.py createsuperuser

   Prompts:
   Email: admin@school.com
   First Name: School
   Last Name: Admin
   Phone: +92-300-1234567
   Date of birth: 1990-01-01
   Gender: MALE
   Password: [Enter secure password]
   Password (again): [Confirm]

2. Verify admin was created:
   
   $ python manage.py shell
   
   >>> from apps.accounts.models import CustomUser
   >>> admin = CustomUser.objects.get(email='admin@school.com')
   >>> print(admin.full_name, admin.role, admin.is_staff)
   >>> exit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: TEST ADMIN PANEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Start development server:
   
   $ python manage.py runserver

2. Open browser and visit:
   
   http://127.0.0.1:8000/admin/

3. Login with admin credentials created above

4. Verify all apps are registered:
   
   Should see:
   ✓ ACCOUNTS
     - CustomUser
   ✓ ACTIVITY LOGS
     - Activity Log
   ✓ ANNOUNCEMENTS
     - Announcement
   ✓ ASSIGNMENT
     - Assignment
     - Submission
   ✓ ATTENDANCE
     - Attendance
   ✓ CLASSES
     - Class
     - Section
   ✓ EXAMINATIONS
     - Exam
     - Marks
     - Result
   ✓ FEES
     - Fee Category
     - Fee Invoice
     - Fee Payment
     - Fee Structure
   ✓ STUDENTS
     - Student
   ✓ SUBJECTS
     - Enrollment
     - Subject
   ✓ TEACHERS
     - Teacher
   ✓ TIMETABLE
     - Period
     - Timetable


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 6: CREATE TEST DATA (CLASSES AND SECTIONS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use the admin panel:

1. Create Classes:
   - Go to CLASSES > Class > Add Class
   
   Create:
   Name: Grade 1
   Numeric Grade: 1
   Description: Primary Class 1
   
   Name: Grade 6
   Numeric Grade: 6
   
   Name: Grade 9
   Numeric Grade: 9
   
   Name: Grade 10
   Numeric Grade: 10

2. Create Sections:
   - Go to CLASSES > Section > Add Section
   
   For Grade 9, create:
   Class: Grade 9
   Name: A
   Max Capacity: 40
   
   Class: Grade 9
   Name: B
   Max Capacity: 40
   
   Class: Grade 9
   Name: C
   Max Capacity: 35


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 7: CREATE TEST TEACHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Create a teacher user via Django shell:
   
   $ python manage.py shell
   
   >>> from apps.accounts.models import CustomUser
   >>> from apps.teachers.models import Teacher
   >>> 
   >>> # Create user
   >>> teacher_user = CustomUser.objects.create_user(
   ...     email='teacher1@school.com',
   ...     username='teacher1',
   ...     password='TeacherPass123!',
   ...     first_name='Ahmed',
   ...     last_name='Khan',
   ...     role='TEACHER',
   ...     phone='+92-300-1234567'
   ... )
   >>> 
   >>> # Create teacher profile
   >>> teacher = Teacher.objects.create(
   ...     user=teacher_user,
   ...     employee_id='EMP001',
   ...     qualification='M.Sc Physics',
   ...     experience_years=5,
   ...     status='ACTIVE',
   ...     employment_type='FULL_TIME'
   ... )
   >>> 
   >>> print(f"Created teacher: {teacher}")
   >>> exit()

2. Or use admin panel:
   - Create CustomUser in ACCOUNTS
   - Create Teacher in TEACHERS, linking to the user


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 8: CREATE TEST SUBJECT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Via admin panel:
   - Go to SUBJECTS > Subject > Add Subject
   
   Name: Mathematics
   Code: MATH-101
   Class: Grade 9
   Teacher: Ahmed Khan
   Subject Type: Compulsory
   Credits: 4

2. Or via shell:
   
   $ python manage.py shell
   
   >>> from apps.subjects.models import Subject
   >>> from apps.classes.models import Class
   >>> from apps.teachers.models import Teacher
   >>> 
   >>> class_9 = Class.objects.get(name='Grade 9')
   >>> teacher = Teacher.objects.get(employee_id='EMP001')
   >>> 
   >>> subject = Subject.objects.create(
   ...     name='Mathematics',
   ...     code='MATH-101',
   ...     school_class=class_9,
   ...     teacher=teacher,
   ...     subject_type='COMPULSORY',
   ...     credits=4
   ... )
   >>> print(f"Created: {subject}")
   >>> exit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 9: CREATE TEST STUDENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Via shell:
   
   $ python manage.py shell
   
   >>> from apps.accounts.models import CustomUser
   >>> from apps.students.models import Student
   >>> from apps.classes.models import Class, Section
   >>> from datetime import date
   >>> 
   >>> # Create user
   >>> student_user = CustomUser.objects.create_user(
   ...     email='student1@school.com',
   ...     username='student1',
   ...     password='StudentPass123!',
   ...     first_name='Ali',
   ...     last_name='Ahmed',
   ...     role='STUDENT',
   ...     phone='+92-300-9876543'
   ... )
   >>> 
   >>> # Get class and section
   >>> class_9 = Class.objects.get(name='Grade 9')
   >>> section_a = Section.objects.get(school_class=class_9, name='A')
   >>> 
   >>> # Create student
   >>> student = Student.objects.create(
   ...     user=student_user,
   ...     admission_number='STU001',
   ...     current_class=class_9,
   ...     section=section_a,
   ...     admission_date=date(2024, 4, 1),
   ...     date_of_birth=date(2010, 6, 15),
   ...     gender='MALE',
   ...     blood_group='O+',
   ...     nationality='Pakistani',
   ...     address='123 Main Street, Lahore',
   ...     father_name='Ahmed Khan',
   ...     father_phone='+92-300-1111111'
   ... )
   >>> 
   >>> print(f"Created: {student}")
   >>> exit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 10: VERIFY DATA IN ADMIN PANEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to STUDENTS > Student
   - Should see the student you created
   - Verify all fields are displayed correctly

2. Go to SUBJECTS > Subject
   - Should see Mathematics linked to Grade 9 and Teacher Ahmed Khan

3. Go to ACCOUNTS > Users
   - Should see all three users (admin, teacher, student)
   - Verify roles are correct

4. Go to ACTIVITY LOGS > Activity Log
   - Should see creation records for all users


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 11: TEST MODEL RELATIONSHIPS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run Python shell tests:

$ python manage.py shell

>>> # Test Class-Section relationship
>>> from apps.classes.models import Class, Section
>>> grade_9 = Class.objects.get(name='Grade 9')
>>> print(f"Grade 9 has {grade_9.total_sections} sections")
>>> print(f"Total students in Grade 9: {grade_9.total_students}")
>>> 
>>> # Test Section properties
>>> section_a = Section.objects.get(school_class=grade_9, name='A')
>>> print(f"Section A - Current: {section_a.current_strength}, Available: {section_a.available_seats}")
>>> print(f"Is Full? {section_a.is_full}")
>>> 
>>> # Test Student relationships
>>> from apps.students.models import Student
>>> student = Student.objects.get(admission_number='STU001')
>>> print(f"Student: {student.full_name}")
>>> print(f"Email: {student.email}")
>>> print(f"Age: {student.age}")
>>> print(f"Class: {student.current_class.name}")
>>> print(f"Section: {student.section.name}")
>>> 
>>> # Test enrollment
>>> from apps.subjects.models import Enrollment
>>> enrollment = Enrollment.objects.create(
   ...     student=student,
   ...     school_class=grade_9,
   ...     section=section_a,
   ...     academic_year='2024-2025',
   ...     roll_number='001'
... )
>>> print(f"Enrollment created: {enrollment}")
>>> 
>>> exit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 12: RUN TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run model tests:

$ python manage.py test apps.students
$ python manage.py test apps.teachers
$ python manage.py test apps.classes
$ python manage.py test apps.subjects


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE 3 COMPLETE! ✅
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next: MODULE 4 - ViewSets, Serializers, and API Endpoints
"""
