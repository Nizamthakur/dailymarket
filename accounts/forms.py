from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


# ================= User Registration Form =================
class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'mobile', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'mobile': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
        }


# ================= User Profile Edit Form =================
class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'mobile']  # email বাদ দিলাম
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'mobile': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
        }


# ================= Vendor Registration Form =================
class VendorRegistrationForm(UserCreationForm):
    vendor_type = forms.ChoiceField(
        choices=CustomUser.VENDOR_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'mobile', 'vendor_type', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'mobile': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_role = '3'  # Vendor role
        user.is_vendor_approved = False  # Waiting for admin approval
        if commit:
            user.save()
        return user
