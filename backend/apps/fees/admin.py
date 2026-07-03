from django.contrib import admin
from .models import FeeCategory, FeeInvoice, FeePayment


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_amount', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


class FeePaymentInline(admin.TabularInline):
    model = FeePayment
    extra = 0
    readonly_fields = ['payment_date', 'collected_by']


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'student', 'total_amount', 'amount_paid', 'status', 'due_date']
    list_filter = ['status', 'due_date']
    search_fields = ['invoice_number', 'student__user__first_name', 'student__admission_number']
    readonly_fields = ['amount_paid', 'status']
    inlines = [FeePaymentInline]


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'payment_method', 'payment_date', 'collected_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['invoice__invoice_number', 'reference_number']
    readonly_fields = ['collected_by']

    def save_model(self, request, obj, form, change):
        if not change and not obj.collected_by:
            obj.collected_by = request.user
        super().save_model(request, obj, form, change)
