"""
Django Signals for Activity Logging.

Automatically logs important model operations:
- User login/logout
- Model creation, update, deletion
"""
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ActivityLog

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# USER AUTHENTICATION SIGNALS
# ─────────────────────────────────────────────────────────────

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log when a user logs in.
    
    Triggered by:
        from rest_framework_simplejwt.views import TokenObtainPairView
    """
    try:
        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
        
        ActivityLog.log(
            user=user,
            action=ActivityLog.ActionType.LOGIN,
            model_name='CustomUser',
            object_id=user.id,
            object_repr=user.email,
            description=f"User {user.email} logged in",
            ip_address=ip_address
        )
    except Exception as e:
        logger.error(f"Error logging user login: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log when a user logs out.
    """
    try:
        ip_address = get_client_ip(request) if request else None
        
        ActivityLog.log(
            user=user,
            action=ActivityLog.ActionType.LOGOUT,
            model_name='CustomUser',
            object_id=user.id if user else 0,
            object_repr=user.email if user else 'Unknown',
            description=f"User {'logged out' if user else 'unknown user logged out'}",
            ip_address=ip_address
        )
    except Exception as e:
        logger.error(f"Error logging user logout: {e}")


# ─────────────────────────────────────────────────────────────
# MODEL CHANGE SIGNALS
# ─────────────────────────────────────────────────────────────

def log_model_operation(sender, instance, created, request=None, **kwargs):
    """
    Generic function to log model creation/updates.
    
    Call this from your ViewSet's perform_create/perform_update methods.
    """
    try:
        action = ActivityLog.ActionType.CREATE if created else ActivityLog.ActionType.UPDATE
        
        # Get user from context (passed via request)
        user = request.user if request and hasattr(request, 'user') else None
        
        if not user or user.is_anonymous:
            return
        
        ActivityLog.log(
            user=user,
            action=action,
            model_name=sender.__name__,
            object_id=instance.id,
            object_repr=str(instance),
            description=f"{sender.__name__} {'created' if created else 'updated'}: {str(instance)}"
        )
    except Exception as e:
        logger.error(f"Error logging model operation for {sender.__name__}: {e}")


def log_model_deletion(sender, instance, request=None, **kwargs):
    """
    Generic function to log model deletion.
    """
    try:
        user = request.user if request and hasattr(request, 'user') else None
        
        if not user or user.is_anonymous:
            return
        
        ActivityLog.log(
            user=user,
            action=ActivityLog.ActionType.DELETE,
            model_name=sender.__name__,
            object_id=instance.id,
            object_repr=str(instance),
            description=f"{sender.__name__} deleted: {str(instance)}"
        )
    except Exception as e:
        logger.error(f"Error logging model deletion for {sender.__name__}: {e}")


# ─────────────────────────────────────────────────────────────
# ATTENDANCE SIGNAL
# ─────────────────────────────────────────────────────────────

@receiver(post_save, sender='attendance.Attendance')
def log_attendance_marked(sender, instance, created, **kwargs):
    """
    Log when attendance is marked.
    """
    if created:
        try:
            ActivityLog.log(
                user=instance.marked_by.user if instance.marked_by else None,
                action=ActivityLog.ActionType.MARK_ATTENDANCE,
                model_name='Attendance',
                object_id=instance.id,
                object_repr=f"{instance.student.user.get_full_name()} - {instance.attendance_date}",
                description=f"Attendance marked for {instance.student.user.get_full_name()}: {instance.get_status_display()}"
            )
        except Exception as e:
            logger.error(f"Error logging attendance: {e}")


# ─────────────────────────────────────────────────────────────
# MARKS SIGNAL
# ─────────────────────────────────────────────────────────────

@receiver(post_save, sender='examinations.Marks')
def log_marks_submission(sender, instance, created, update_fields=None, **kwargs):
    """
    Log when marks are entered.
    """
    try:
        if instance.obtained_marks is not None:
            action = ActivityLog.ActionType.CREATE if created else ActivityLog.ActionType.ASSIGN_MARKS
            
            ActivityLog.log(
                user=instance.submitted_by.user if instance.submitted_by else None,
                action=action,
                model_name='Marks',
                object_id=instance.id,
                object_repr=f"{instance.student.user.get_full_name()} - {instance.exam.name}",
                description=f"Marks assigned: {instance.student.user.get_full_name()} - {instance.exam.name} ({instance.marks_obtained}/{instance.exam.total_marks})"
            )
    except Exception as e:
        logger.error(f"Error logging marks: {e}")


# ─────────────────────────────────────────────────────────────
# SUBMISSION SIGNAL
# ─────────────────────────────────────────────────────────────

@receiver(post_save, sender='assignments.Submission')
def log_submission_graded(sender, instance, created, update_fields=None, **kwargs):
    """
    Log when a submission is graded.
    """
    try:
        # Only log if graded
        if instance.marks_obtained is not None and instance.graded_at:
            ActivityLog.log(
                user=instance.graded_by.user if instance.graded_by else None,
                action=ActivityLog.ActionType.GRADE_SUBMISSION,
                model_name='Submission',
                object_id=instance.id,
                object_repr=f"{instance.student.user.get_full_name()} - {instance.assignment.title}",
                description=f"Submission graded: {instance.student.user.get_full_name()} - {instance.assignment.title} ({instance.marks_obtained}/{instance.assignment.max_marks})"
            )
    except Exception as e:
        logger.error(f"Error logging submission grading: {e}")


# ─────────────────────────────────────────────────────────────
# FEE PAYMENT SIGNAL
# ─────────────────────────────────────────────────────────────

@receiver(post_save, sender='fees.FeePayment')
def log_fee_payment(sender, instance, created, **kwargs):
    """
    Log when a fee payment is processed.
    """
    if created:
        try:
            ActivityLog.log(
                user=instance.collected_by,
                action=ActivityLog.ActionType.PAYMENT,
                model_name='FeePayment',
                object_id=instance.id,
                object_repr=f"{instance.invoice.student.user.get_full_name()} - {instance.amount}",
                description=f"Fee payment: {instance.invoice.student.user.get_full_name()} paid {instance.amount} ({instance.get_payment_method_display()})"
            )
        except Exception as e:
            logger.error(f"Error logging fee payment: {e}")


# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_client_ip(request):
    """
    Get client's IP address from request.
    """
    if not request:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
