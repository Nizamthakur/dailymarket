from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import RegistrationForm, CustomUserEditForm
from products.admin import super_admin_site


class CustomUserAdmin(UserAdmin):
    form = CustomUserEditForm
    add_form = RegistrationForm
    model = CustomUser

    list_display = (
        "email",
        "id",
        "first_name",
        "last_name",
        "mobile",
        "user_role",
        "vendor_type",
        "is_vendor_approved",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "user_role",
        "vendor_type",
        "is_vendor_approved",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)

    fieldsets = (
        ("Login Info", {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "mobile")}),
        ("Role & Status", {"fields": ("user_role", "vendor_type", "is_vendor_approved")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        # ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
        ("Personal Info", {"fields": ("first_name", "last_name", "mobile")}),
        ("Role & Status", {"fields": ("user_role", "vendor_type", "is_vendor_approved")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
    )

    actions = ['approve_vendors']

    def approve_vendors(self, request, queryset):
        vendors_to_approve = queryset.filter(user_role='3', is_vendor_approved=False)
        updated = vendors_to_approve.update(is_vendor_approved=True)
        self.message_user(request, f"{updated} vendor(s) approved successfully.")

    approve_vendors.short_description = "Approve selected vendors"


super_admin_site.register(CustomUser, CustomUserAdmin)