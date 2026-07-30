from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserModelTests(TestCase):
    """Unit tests for CustomUser model and role properties."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@school.com',
            password='Password123!',
            role=User.Role.ADMIN,
            first_name='Admin',
            last_name='User'
        )
        self.teacher = User.objects.create_user(
            username='teacher_test',
            email='teacher@school.com',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Teacher',
            last_name='User'
        )
        self.student = User.objects.create_user(
            username='student_test',
            email='student@school.com',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='User'
        )

    def test_user_roles(self):
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.admin.is_teacher)
        self.assertFalse(self.admin.is_student)

        self.assertTrue(self.teacher.is_teacher)
        self.assertFalse(self.teacher.is_admin)
        self.assertFalse(self.teacher.is_student)

        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_admin)
        self.assertFalse(self.student.is_teacher)

    def test_full_name_property(self):
        self.assertEqual(self.admin.full_name, 'Admin User')

    def test_user_str_representation(self):
        self.assertEqual(str(self.admin), 'Admin User (ADMIN)')

    def test_email_field_unique(self):
        self.assertEqual(self.admin.USERNAME_FIELD, 'email')
