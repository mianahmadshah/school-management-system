"""
Django management command to seed the database with initial data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date, time
import random

from apps.classes.models import Class, Section
from apps.subjects.models import Subject
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.attendance.models import Attendance
from apps.examinations.models import Exam, Result
from apps.fees.models import FeeCategory, FeeStructure, FeeInvoice, FeePayment
from apps.timetable.models import Period, Timetable
from apps.announcements.models import Announcement
from apps.assignments.models import Assignment, Submission

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with initial demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@educore.edu',
                password='admin123',
                role='ADMIN',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin123'))
        
        # Create teachers
        teachers_data = [
            {'username': 'teacher1', 'email': 'teacher1@educore.edu', 'password': 'teacher123', 'first_name': 'Ahmed', 'last_name': 'Khan'},
            {'username': 'teacher2', 'email': 'teacher2@educore.edu', 'password': 'teacher123', 'first_name': 'Sarah', 'last_name': 'Ali'},
            {'username': 'teacher3', 'email': 'teacher3@educore.edu', 'password': 'teacher123', 'first_name': 'Muhammad', 'last_name': 'Hassan'},
        ]
        
        teachers = []
        for t_data in teachers_data:
            if not User.objects.filter(username=t_data['username']).exists():
                user = User.objects.create_user(
                    username=t_data['username'],
                    email=t_data['email'],
                    password=t_data['password'],
                    role='TEACHER',
                    first_name=t_data['first_name'],
                    last_name=t_data['last_name']
                )
                teacher = Teacher.objects.create(
                    user=user,
                    phone_number='03001234567',
                    qualification='Masters',
                    experience_years=5,
                    joining_date=date.today() - timedelta(days=365)
                )
                teachers.append(teacher)
                self.stdout.write(self.style.SUCCESS(f'Created teacher: {t_data["username"]}'))
        
        if not teachers:
            teachers = list(Teacher.objects.all())
        
        # Create classes and sections
        classes_data = [
            {'name': 'Class 9', 'sections': ['A', 'B']},
            {'name': 'Class 10', 'sections': ['A', 'B']},
        ]
        
        classes = []
        sections = []
        for c_data in classes_data:
            cls, created = Class.objects.get_or_create(name=c_data['name'], defaults={'is_active': True})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created class: {cls.name}'))
            classes.append(cls)
            
            for sec_name in c_data['sections']:
                section, created = Section.objects.get_or_create(
                    school_class=cls,
                    name=sec_name,
                    defaults={'is_active': True}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created section: {cls.name} - {sec_name}'))
                sections.append(section)
        
        if not sections:
            sections = list(Section.objects.all())
        
        # Create subjects
        subjects_data = [
            {'name': 'Mathematics', 'code': 'MATH'},
            {'name': 'Physics', 'code': 'PHY'},
            {'name': 'Chemistry', 'code': 'CHEM'},
            {'name': 'English', 'code': 'ENG'},
            {'name': 'Urdu', 'code': 'URD'},
        ]
        
        subjects = []
        for s_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=s_data['code'],
                defaults={'name': s_data['name'], 'is_active': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created subject: {subject.name}'))
            subjects.append(subject)
        
        if not subjects:
            subjects = list(Subject.objects.all())
        
        # Create students
        students_data = [
            {'username': 'student1', 'admission': 'ADM001', 'first_name': 'Ali', 'last_name': 'Hassan', 'class_idx': 0, 'section_idx': 0},
            {'username': 'student2', 'admission': 'ADM002', 'first_name': 'Fatima', 'last_name': 'Zahra', 'class_idx': 0, 'section_idx': 0},
            {'username': 'student3', 'admission': 'ADM003', 'first_name': 'Hassan', 'last_name': 'Ali', 'class_idx': 0, 'section_idx': 1},
            {'username': 'student4', 'admission': 'ADM004', 'first_name': 'Ayesha', 'last_name': 'Khan', 'class_idx': 1, 'section_idx': 0},
            {'username': 'student5', 'admission': 'ADM005', 'first_name': 'Usman', 'last_name': 'Ahmed', 'class_idx': 1, 'section_idx': 1},
        ]
        
        students = []
        for s_data in students_data:
            if not User.objects.filter(username=s_data['username']).exists():
                user = User.objects.create_user(
                    username=s_data['username'],
                    email=f"{s_data['username']}@educore.edu",
                    password='student123',
                    role='STUDENT',
                    first_name=s_data['first_name'],
                    last_name=s_data['last_name']
                )
                student = Student.objects.create(
                    user=user,
                    admission_number=s_data['admission'],
                    current_class=classes[s_data['class_idx']],
                    section=sections[s_data['section_idx']],
                    date_of_birth=date(2008, 1, 1),
                    gender='MALE' if s_data['first_name'] in ['Ali', 'Hassan', 'Usman'] else 'FEMALE',
                    blood_group='A+',
                    address='Islamabad, Pakistan',
                    is_active=True
                )
                students.append(student)
                self.stdout.write(self.style.SUCCESS(f'Created student: {s_data["username"]}'))
        
        if not students:
            students = list(Student.objects.all())
        
        # Create fee categories
        fee_categories = []
        for cat_name in ['Tuition', 'Transport', 'Examination']:
            cat, _ = FeeCategory.objects.get_or_create(name=cat_name, defaults={'is_active': True})
            fee_categories.append(cat)
        
        # Create fee structures
        for cls in classes:
            for cat in fee_categories[:1]:  # Tuition for each class
                FeeStructure.objects.get_or_create(
                    category=cat,
                    school_class=cls,
                    defaults={'amount': 5000.00, 'is_active': True}
                )
        
        # Create fee invoices
        for student in students:
            for cls in classes:
                if student.current_class == cls:
                    structure = FeeStructure.objects.filter(school_class=cls, category=fee_categories[0]).first()
                    if structure:
                        invoice, _ = FeeInvoice.objects.get_or_create(
                            student=student,
                            academic_year='2024-25',
                            category=structure,
                            defaults={
                                'total_amount': structure.amount,
                                'amount_paid': structure.amount * 0.5,
                                'due_date': date.today() + timedelta(days=30),
                                'status': 'PARTIAL',
                                'is_active': True
                            }
                        )
        
        # Create exams
        exams = []
        exam1, _ = Exam.objects.get_or_create(
            name='Mid-Term Exam',
            exam_type='MIDTERM',
            academic_year='2024-25',
            defaults={
                'start_date': date.today() - timedelta(days=30),
                'end_date': date.today() - timedelta(days=10),
                'is_published': True
            }
        )
        exams.append(exam1)
        
        # Create results
        for student in students:
            for subject in subjects[:3]:
                marks = random.randint(40, 95)
                result, _ = Result.objects.get_or_create(
                    exam=exam1,
                    student=student,
                    subject=subject,
                    defaults={
                        'marks_obtained': marks,
                        'total_marks': 100,
                        'is_pass': marks >= 50
                    }
                )
        
        # Create attendance records
        for student in students:
            for day in range(1, 11):
                att_date = date.today() - timedelta(days=day)
                if att_date.weekday() < 5:  # Weekdays only
                    status = random.choice(['PRESENT', 'PRESENT', 'PRESENT', 'ABSENT', 'LATE'])
                    Attendance.objects.get_or_create(
                        student=student,
                        date=att_date,
                        defaults={'status': status, 'is_active': True}
                    )
        
        # Create periods
        periods = []
        for i, (name, start, end, is_break) in enumerate([
            ('1st Period', time(8, 0), time(9, 0), False),
            ('2nd Period', time(9, 0), time(10, 0), False),
            ('Break', time(10, 0), time(10, 30), True),
            ('3rd Period', time(10, 30), time(11, 30), False),
            ('4th Period', time(11, 30), time(12, 30), False),
        ]):
            period, _ = Period.objects.get_or_create(
                name=name,
                defaults={'start_time': start, 'end_time': end, 'is_break': is_break, 'order': i}
            )
            periods.append(period)
        
        # Create timetable entries
        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
        for cls in classes[:1]:
            for section in sections[:2]:
                for day in days:
                    for i, period in enumerate(periods[:4]):
                        if not period.is_break:
                            subject = subjects[i % len(subjects)]
                            teacher = teachers[i % len(teachers)]
                            Timetable.objects.get_or_create(
                                school_class=cls,
                                section=section,
                                period=period,
                                day_of_week=day,
                                defaults={
                                    'subject': subject,
                                    'teacher': teacher,
                                    'is_active': True
                                }
                            )
        
        # Create announcement
        Announcement.objects.get_or_create(
            title='Welcome to New Academic Year',
            defaults={
                'content': 'We are excited to welcome all students and teachers to the new academic year 2024-25. Classes will begin next Monday.',
                'target_audience': 'ALL',
                'is_important': True,
                'is_published': True,
                'published_by': User.objects.filter(username='admin').first()
            }
        )
        
        # Create assignment
        for cls in classes[:1]:
            for section in sections[:1]:
                Assignment.objects.get_or_create(
                    title='Mathematics Homework - Algebra',
                    defaults={
                        'description': 'Complete exercise 3.1 from your textbook. Show all steps.',
                        'school_class': cls,
                        'section': section,
                        'subject': subjects[0],
                        'teacher': teachers[0],
                        'due_date': timezone.now() + timedelta(days=7),
                        'max_marks': 20,
                        'is_active': True
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))
        self.stdout.write('Default logins:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Teachers: teacher1, teacher2, teacher3 / teacher123')
        self.stdout.write('  Students: student1-5 / student123')