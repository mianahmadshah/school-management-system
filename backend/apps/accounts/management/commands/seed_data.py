"""
Django management command to seed the database with initial demo data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date, time
import random

from apps.classes.models import Class, Section, AcademicSession
from apps.subjects.models import Subject, Enrollment
from apps.teachers.models import Teacher, TeacherAllocation
from apps.students.models import Student, StudentAdmission
from apps.attendance.models import Attendance
from apps.examinations.models import Exam, Marks, Result
from apps.fees.models import FeeCategory, FeeStructure, FeeInvoice, FeePayment
from apps.timetable.models import Period, Timetable
from apps.announcements.models import Announcement
from apps.assignments.models import Assignment, Submission

User = get_user_model()


def get_or_create_user(username, email, password, role, **extra):
    """Create a user OR fetch existing. Password is hashed on creation only."""
    defaults = {
        'email': email,
        'role': role,
    }
    defaults.update(extra)
    user, created = User.objects.get_or_create(username=username, defaults=defaults)
    if created:
        user.set_password(password)
        user.save()
    return user


class Command(BaseCommand):
    help = 'Seeds the database with initial demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with Connected School ERP Lifecycle Data...')

        # ── 1. Create Academic Sessions ──────────────────────
        session_current, _ = AcademicSession.objects.get_or_create(
            name='2026-2027',
            defaults={
                'start_date': date(2026, 4, 1),
                'end_date': date(2027, 3, 31),
                'is_current': True,
                'is_active': True
            }
        )
        session_past, _ = AcademicSession.objects.get_or_create(
            name='2025-2026',
            defaults={
                'start_date': date(2025, 4, 1),
                'end_date': date(2026, 3, 31),
                'is_current': False,
                'is_active': True
            }
        )

        # ── 2. Create Superuser (Admin) ───────────────────────
        admin = get_or_create_user(
            'admin', 'admin@educore.edu', 'admin123', User.Role.ADMIN,
            first_name='Principal', last_name='Admin'
        )

        # ── 3. Create Teachers ────────────────────────────────
        teachers_data = [
            {'username': 'teacher1', 'email': 'ali.khan@educore.edu', 'first_name': 'Ali', 'last_name': 'Khan', 'spec': 'Mathematics'},
            {'username': 'teacher2', 'email': 'sara.ahmed@educore.edu', 'first_name': 'Sara', 'last_name': 'Ahmed', 'spec': 'Science'},
            {'username': 'teacher3', 'email': 'tariq.mahmood@educore.edu', 'first_name': 'Tariq', 'last_name': 'Mahmood', 'spec': 'English'},
        ]
        teachers = []
        for idx, t_data in enumerate(teachers_data, start=1):
            user = get_or_create_user(
                t_data['username'], t_data['email'], 'teacher123', User.Role.TEACHER,
                first_name=t_data['first_name'], last_name=t_data['last_name'], phone=f'0300{idx}234567'
            )
            teacher, _ = Teacher.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'EMP{idx:03d}',
                    'department': 'Academics',
                    'designation': 'Senior Teacher',
                    'highest_qualification': 'M.Sc. Education',
                    'specialization': t_data['spec'],
                    'experience_years': 6,
                    'joining_date': date(2022, 1, 1),
                }
            )
            teachers.append(teacher)

        # ── 4. Create Classes & Sections ──────────────────────
        classes_config = [
            ('Grade 6', 6, ['A', 'B']),
            ('Grade 7', 7, ['A', 'B']),
            ('Grade 8', 8, ['A', 'B']),
        ]
        classes_map = {}
        sections_map = {}
        for c_name, c_num, sec_names in classes_config:
            cls, _ = Class.objects.get_or_create(
                name=c_name,
                defaults={'numeric_grade': c_num, 'class_teacher': teachers[0], 'is_active': True}
            )
            classes_map[c_name] = cls
            sections_map[c_name] = {}
            for sec_name in sec_names:
                sec, _ = Section.objects.get_or_create(
                    school_class=cls,
                    name=sec_name,
                    defaults={'section_teacher': teachers[0], 'room_number': f"Room {c_num}0{sec_name}", 'max_capacity': 40}
                )
                sections_map[c_name][sec_name] = sec

        grade6_a = sections_map['Grade 6']['A']
        grade6_cls = classes_map['Grade 6']

        # ── 5. Create Subjects ────────────────────────────────
        subjects_data = [
            ('Mathematics', 'MATH-601', grade6_cls),
            ('Science', 'SCI-601', grade6_cls),
            ('English Literature', 'ENG-601', grade6_cls),
        ]
        subjects = []
        for s_name, s_code, s_cls in subjects_data:
            subj, _ = Subject.objects.get_or_create(
                code=s_code,
                defaults={'name': s_name, 'school_class': s_cls, 'teacher': teachers[0], 'is_active': True}
            )
            subjects.append(subj)

        # ── 6. Create Teacher Allocations ─────────────────────
        TeacherAllocation.objects.get_or_create(
            academic_session=session_current,
            school_class=grade6_cls,
            section=grade6_a,
            subject=subjects[0],
            defaults={'teacher': teachers[0], 'is_active': True}
        )
        TeacherAllocation.objects.get_or_create(
            academic_session=session_current,
            school_class=grade6_cls,
            section=grade6_a,
            subject=subjects[1],
            defaults={'teacher': teachers[1], 'is_active': True}
        )

        # ── 7. Create Student Admissions & Enrollments ────────
        students_data = [
            ('student1', 'ADM-2026-001', 'Ahmad', 'Shah', 'ahmad@educore.edu', '8000.00', '10000.00'),
            ('student2', 'ADM-2026-002', 'Fatima', 'Zahra', 'fatima@educore.edu', '10000.00', '10000.00'),
            ('student3', 'ADM-2026-003', 'Hassan', 'Ali', 'hassan@educore.edu', '5000.00', '10000.00'),
        ]

        students = []
        for username, adm_no, fn, ln, email, paid_val, fee_val in students_data:
            user = get_or_create_user(
                username, email, 'student123', User.Role.STUDENT,
                first_name=fn, last_name=ln
            )
            student, _ = Student.objects.get_or_create(
                user=user,
                defaults={
                    'admission_number': adm_no,
                    'current_class': grade6_cls,
                    'section': grade6_a,
                    'admission_date': date(2026, 4, 2),
                    'date_of_birth': date(2012, 5, 10),
                    'gender': 'MALE' if fn in ['Ahmad', 'Hassan'] else 'FEMALE',
                    'father_name': f"{ln} Senior",
                    'address': 'Islamabad, Pakistan',
                    'status': 'ACTIVE'
                }
            )
            students.append(student)

            # Active Enrollment for 2026-2027
            Enrollment.objects.get_or_create(
                student=student,
                academic_session=session_current,
                school_class=grade6_cls,
                section=grade6_a,
                defaults={'academic_year': '2026-2027', 'roll_number': adm_no.split('-')[-1], 'status': 'ENROLLED', 'is_active': True}
            )

            # Admission Record & Initial Payment
            paid = float(paid_val)
            fee = float(fee_val)
            StudentAdmission.objects.get_or_create(
                admission_number=adm_no,
                defaults={
                    'first_name': fn, 'last_name': ln, 'email': email,
                    'father_name': f"{ln} Senior", 'date_of_birth': date(2012, 5, 10),
                    'gender': 'MALE' if fn in ['Ahmad', 'Hassan'] else 'FEMALE',
                    'address': 'Islamabad, Pakistan',
                    'academic_session': session_current,
                    'school_class': grade6_cls,
                    'section': grade6_a,
                    'admission_fee': fee,
                    'amount_paid': paid,
                    'status': 'APPROVED',
                    'created_student': student
                }
            )

            # Fee Invoice & Payment Receipts
            inv, _ = FeeInvoice.objects.get_or_create(
                invoice_number=f"INV-ADM-{adm_no}",
                defaults={
                    'student': student,
                    'academic_session': session_current,
                    'academic_year': '2026-2027',
                    'due_date': date(2026, 4, 30),
                    'total_amount': fee,
                    'amount_paid': paid,
                    'status': 'PAID' if paid >= fee else ('PARTIAL' if paid > 0 else 'UNPAID'),
                    'remarks': 'Admission Fee Invoice'
                }
            )
            if paid > 0:
                FeePayment.objects.get_or_create(
                    invoice=inv,
                    defaults={
                        'amount': paid,
                        'payment_method': 'CASH',
                        'reference_number': f"REC-{adm_no}",
                        'remarks': 'Initial Payment',
                        'collected_by': admin
                    }
                )

        # ── 8. Create Timetable Slots ─────────────────────────
        periods = []
        time_slots = [
            ('1st Period', time(8, 0), time(9, 0), False),
            ('2nd Period', time(9, 0), time(10, 0), False),
            ('Break', time(10, 0), time(10, 30), True),
            ('3rd Period', time(10, 30), time(11, 30), False),
        ]
        for idx, (pname, stime, etime, is_brk) in enumerate(time_slots):
            p, _ = Period.objects.get_or_create(
                name=pname,
                defaults={'start_time': stime, 'end_time': etime, 'is_break': is_brk, 'order': idx}
            )
            periods.append(p)

        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
        for d in days:
            Timetable.objects.get_or_create(
                academic_session=session_current,
                school_class=grade6_cls,
                section=grade6_a,
                period=periods[0],
                day_of_week=d,
                defaults={'subject': subjects[0], 'teacher': teachers[0], 'is_active': True}
            )
            Timetable.objects.get_or_create(
                academic_session=session_current,
                school_class=grade6_cls,
                section=grade6_a,
                period=periods[1],
                day_of_week=d,
                defaults={'subject': subjects[1], 'teacher': teachers[1], 'is_active': True}
            )

        # ── 9. Create Daily Attendance ────────────────────────
        for st in students:
            for d_offset in range(1, 10):
                att_date = date.today() - timedelta(days=d_offset)
                if att_date.weekday() < 5:
                    Attendance.objects.get_or_create(
                        student=st,
                        date=att_date,
                        defaults={
                            'school_class': grade6_cls,
                            'section': grade6_a,
                            'status': 'PRESENT' if d_offset % 4 != 0 else 'ABSENT',
                            'marked_by': teachers[0].user
                        }
                    )

        # ── 10. Create Assignments ────────────────────────────
        Assignment.objects.get_or_create(
            title='Algebra Fundamentals Assignment',
            defaults={
                'description': 'Solve questions 1-10 on page 45 of your Mathematics textbook.',
                'school_class': grade6_cls,
                'section': grade6_a,
                'subject': subjects[0],
                'teacher': teachers[0],
                'due_date': timezone.now() + timedelta(days=5),
                'max_marks': 50,
                'is_active': True
            }
        )

        # ── 11. Create Exams, Marks & Results ─────────────────
        exam, _ = Exam.objects.get_or_create(
            name='Midterm Examinations 2026',
            subject=subjects[0],
            school_class=grade6_cls,
            defaults={
                'academic_session': session_current,
                'exam_type': 'MIDTERM',
                'total_marks': 100,
                'passing_marks': 40,
                'start_date': date.today() - timedelta(days=15),
                'end_date': date.today() - timedelta(days=5),
                'is_published': True,
                'is_active': True
            }
        )

        for st in students:
            marks_val = random.randint(55, 92)
            Marks.objects.get_or_create(
                exam=exam,
                student=st,
                subject=subjects[0],
                defaults={
                    'total_marks': 100,
                    'passing_marks': 40,
                    'obtained_marks': marks_val,
                    'is_passed': marks_val >= 40,
                    'submitted_by': teachers[0]
                }
            )

            Result.objects.get_or_create(
                exam=exam,
                student=st,
                defaults={
                    'total_marks_obtained': marks_val,
                    'total_maximum_marks': 100,
                    'percentage': marks_val,
                    'overall_grade': 'A' if marks_val >= 80 else 'B',
                    'passed': marks_val >= 40,
                    'remarks': 'Good academic performance'
                }
            )

        self.stdout.write(self.style.SUCCESS('[SUCCESS] Connected School ERP Database Seeded Successfully!'))
        self.stdout.write('Default Logins:')
        self.stdout.write('  ADMIN:   admin / admin123')
        self.stdout.write('  TEACHER: teacher1 / teacher123 (Mr. Ali Khan)')
        self.stdout.write('  STUDENT: student1 / student123 (Ahmad Shah)')

