from django.contrib import admin, messages
from django.db.models import ProtectedError
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import *
from django.contrib.auth.models import Group
from Vendors.models import WithdrawRequest
# ================= Super Admin Site ================= #
class SuperAdminSite(admin.AdminSite):
    site_header = 'Super Admin Dashboard'
    site_title = 'Super Admin Dashboard'
    index_title = 'Control Your Site From Here'

    def has_permission(self, request):
        # Only superuser can access
        return request.user.is_authenticated and request.user.is_superuser

    login_view = 'superadmin:login'  # Optional if you have custom login


super_admin_site = SuperAdminSite(name='superadminsite')


# ================= Inline Models ================= #
class ProductImages(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAditionalInformations(admin.TabularInline):
    model = ProductAditionalInformation
    extra = 1


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ['title', 'vendor_stores', 'regular_price']
    show_change_link = True


# ================= Product Admin ================= #
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductImages, ProductAditionalInformations)
    list_display = ['title', 'vendor_stores', 'is_top_deal', 'is_featured', 'regular_price', 'created_at']
    list_editable = ('vendor_stores', 'is_top_deal', 'is_featured')
    list_filter = ['categories', 'vendor_stores']
    search_fields = ['title', 'categories__name', 'vendor_stores__name']

    def save_model(self, request, obj, form, change):
        if obj.discounted_parcent > 100:
            raise ValidationError("Discount percentage cannot be more than 100%")
        super().save_model(request, obj, form, change)


# ================= Cart Admin ================= #
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['product', 'user']
    list_filter = ['user']
    search_fields = ['product__title', 'user__email']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            try:
                obj.delete()
            except ProtectedError:
                self.message_user(
                    request,
                    f"Cannot delete {obj.product.title} because it is used in some order/cart.",
                    level=messages.ERROR
                )


# ================= Categories Admin ================= #
@admin.register(Categories, site=super_admin_site)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'industry', 'slug', 'created_at')
    list_filter = ('industry',)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductInline]

    def delete_queryset(self, request, queryset):
        success_count = 0
        fail_count = 0
        failed_items = []

        for category in queryset:
            try:
                if category.product_set.exists():
                    category.product_set.update(categories=None)
                category.subcategories_set.all().delete()
                category.delete()
                success_count += 1
            except IntegrityError as e:
                fail_count += 1
                failed_items.append(category.name)
                self.message_user(
                    request,
                    f"Could not delete {category.name}: {str(e)}",
                    level=messages.ERROR
                )

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully deleted {success_count} categories.",
                level=messages.SUCCESS
            )
        if fail_count > 0:
            self.message_user(
                request,
                f"Failed to delete {fail_count} categories: {', '.join(failed_items)}",
                level=messages.ERROR
            )

    def delete_model(self, request, obj):
        try:
            if obj.product_set.exists():
                obj.product_set.update(categories=None)
            obj.subcategories_set.all().delete()
            super().delete_model(request, obj)
            self.message_user(
                request,
                f"Category '{obj.name}' deleted successfully.",
                level=messages.SUCCESS
            )
        except IntegrityError as e:
            self.message_user(
                request,
                f"Could not delete category '{obj.name}': {str(e)}",
                level=messages.ERROR
            )
            raise


# ================= SubCategories Admin ================= #
@admin.register(SubCategories, site=super_admin_site)
class SubCategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'categories', 'slug', 'created_at')
    list_filter = ('categories',)
    prepopulated_fields = {"slug": ("name",)}

    def delete_queryset(self, request, queryset):
        success_count = 0
        fail_count = 0
        failed_items = []

        for subcategory in queryset:
            try:
                subcategory.delete()
                success_count += 1
            except IntegrityError as e:
                fail_count += 1
                failed_items.append(subcategory.name)
                self.message_user(
                    request,
                    f"Could not delete {subcategory.name}: {str(e)}",
                    level=messages.ERROR
                )

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully deleted {success_count} subcategories.",
                level=messages.SUCCESS
            )
        if fail_count > 0:
            self.message_user(
                request,
                f"Failed to delete {fail_count} subcategories: {', '.join(failed_items)}",
                level=messages.ERROR
            )

    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
            self.message_user(
                request,
                f"SubCategory '{obj.name}' deleted successfully.",
                level=messages.SUCCESS
            )
        except IntegrityError as e:
            self.message_user(
                request,
                f"Could not delete subcategory '{obj.name}': {str(e)}",
                level=messages.ERROR
            )
            raise


# ================= Banner Admin ================= #
@admin.register(Banner, site=super_admin_site)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'discount_percentage', 'is_active', 'order')
    list_editable = ('discount_percentage', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title', 'category__name')



class HelpVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_editable = ('is_active',)


class OrderComplainAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'message', 'created_at', 'resolved')
    list_filter = ('resolved', 'created_at')
    search_fields = ('order_number', 'message')
    list_editable = ('resolved',)

class ResellProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "created_at")
    search_fields = ("title",)
# ================= Placed Order Item Admin ================= #
class PlacedeOderItemAdmin(admin.ModelAdmin):
    list_display = ['get_order_number', 'product', 'quantity', 'total_price']
    list_filter = ['placed_oder']
    search_fields = ['product__title', 'placed_oder__order_number']

    def get_order_number(self, obj):
        return obj.placed_oder.order_number
    get_order_number.short_description = "Order Number"

class WithdrawRequestAdmin(admin.ModelAdmin):
    list_display = ("vendor", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("vendor__name",)

# ================= Register Models ================= #



super_admin_site.register(WithdrawRequest,WithdrawRequestAdmin)
super_admin_site.register(ResellProduct, ResellProductAdmin)
super_admin_site.register(OrderComplain, OrderComplainAdmin)
super_admin_site.register(HelpVideo, HelpVideoAdmin)
super_admin_site.register(Industry)
super_admin_site.register(Product, ProductAdmin)
super_admin_site.register(ProductImage)
super_admin_site.register(ProductAditionalInformation)
super_admin_site.register(Cart, CartModelAdmin)
super_admin_site.register(CustomerAddress)
super_admin_site.register(PlacedOder)
super_admin_site.register(PlacedeOderItem, PlacedeOderItemAdmin)
super_admin_site.register(CuponCodeGenaration)
super_admin_site.register(CompletedOder)
super_admin_site.register(CompletedOderItems)
super_admin_site.register(ProductStarRatingAndReview)
super_admin_site.register(Group)
