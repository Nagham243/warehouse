import sys
import base64
from io import BytesIO
from django import forms
from .models import StudentProfile, ClubsModel,CoachProfile
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from django.conf import settings


class StudentProfileForm(forms.ModelForm):
    """Form for creating/updating a student profile."""

    profile_image_base64 = forms.FileField(
        label="صورة الملف الشخصي",
        required=False,
        widget=forms.FileInput(attrs={
            'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        })
    )

    class Meta:
        model = StudentProfile
        fields = ['full_name', 'phone', 'birthday', 'profile_image_base64']

        widgets = {
            'full_name': forms.TextInput(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500", 'placeholder': 'الاسم كامل'}),
            'phone': forms.TextInput(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500", 'placeholder': 'رقم الهاتف'}),
            'birthday': forms.DateInput(format=('%d-%m-%Y'), attrs={'type': 'date', 'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"}),
        }

    def clean_profile_image_base64(self):
        """Convert uploaded image file to Base64 string before saving."""
        image_file = self.cleaned_data.get("profile_image_base64")

        if image_file:
            try:
                image_data = image_file.read()

                base64_encoded = base64.b64encode(image_data).decode("utf-8")
                return base64_encoded

            except Exception as e:
                print(f"ERROR: Failed to convert student profile image to Base64: {e}")
                raise forms.ValidationError(f"خطأ في معالجة الصورة: {e}")

        return None

    def save(self, commit=True):
        student = super().save(commit=False)

        # Automatically set the main club
        try:
            main_club = ClubsModel.objects.get(id=settings.MAIN_CLUB_ID)
            student.club = main_club
        except ClubsModel.DoesNotExist:
            # Fallback to first club if main club doesn't exist
            student.club = ClubsModel.objects.first()

        if 'profile_image_base64' in self.cleaned_data and self.cleaned_data['profile_image_base64']:
            student.profile_image_base64 = self.cleaned_data['profile_image_base64']

        if commit:
            student.save()
        return student


class DirectorSignupForm(forms.Form):
    """Form for Director signup, including club registration with Base64 image conversion."""

    # User fields
    username = forms.CharField(label="اسم المستخدم", widget=forms.TextInput(attrs={'class': "input-style"}))
    email = forms.EmailField(label="البريد الالكتروني", widget=forms.EmailInput(attrs={'class': "input-style"}))
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={'class': "input-style"}))
    phone = forms.CharField(label="رقم الهاتف", widget=forms.TextInput(attrs={'class': "input-style"}))

    # Club fields
    club_name = forms.CharField(label="اسم النادي", widget=forms.TextInput(attrs={'class': "input-style"}))
    city = forms.ChoiceField(label="المدينة", choices=[], widget=forms.Select(attrs={'class': "input-style"}))
    street = forms.CharField(label="الشارع", widget=forms.TextInput(attrs={'class': "input-style"}))
    district = forms.CharField(label="الحي", required=False, widget=forms.TextInput(attrs={'class': "input-style"}))
    about = forms.CharField(label="عن النادي", required=False, widget=forms.Textarea(attrs={'class': "input-style", 'rows': 3}))
    desc = forms.CharField(label="وصف قصير", required=False, widget=forms.Textarea(attrs={'class': "input-style", 'rows': 2}))
    club_profile_image_base64 = forms.FileField(label="شعار الصالون", required=False, widget=forms.FileInput(attrs={'class': "input-style"}))

    def __init__(self, *args, **kwargs):
        """Initialize form and handle city choices dynamically."""
        super().__init__(*args, **kwargs)

        # Import city choices dynamically to avoid circular import issues
        from .fields import citys

        # Ensure `citys` is a valid tuple and has data
        if not isinstance(citys, tuple) or not citys:
            citys = (('', 'اختر المدينة'),)  # Safe fallback as a tuple

        # Convert tuple to list before assigning (Django requires lists for choices)
        self.fields['city'].choices = list(citys)

    def clean_club_profile_image_base64(self):
        """Convert uploaded image file to Base64 string before saving."""
        image_file = self.cleaned_data.get("club_profile_image_base64")

        if image_file:
            try:
                # Read image binary data
                image_data = image_file.read()

                # Debugging: Print first 50 bytes of the image
                print(f"DEBUG: First 50 bytes of image = {image_data[:50]}")

                # Encode to Base64
                base64_encoded = base64.b64encode(image_data).decode("utf-8")
                print(f"DEBUG: Base64 length = {len(base64_encoded)}")

                return base64_encoded

            except Exception as e:
                print(f"ERROR: Failed to convert image to Base64: {e}")
                raise forms.ValidationError(f"خطأ في معالجة الصورة: {e}")

        return None  # No image uploaded


class EditClubProfileForm(forms.ModelForm):
    """Form for editing club profile with Base64 image handling."""

    club_profile_image_base64 = forms.FileField(label="شعار النادي", required=False, widget=forms.FileInput(attrs={'class': "input-style"}))

    class Meta:
        model = ClubsModel
        fields = ['name', 'desc', 'about', 'club_profile_image_base64']

    def save(self, commit=True):
        club = super().save(commit=False)

        # Handle image upload and Base64 conversion
        if self.cleaned_data.get('club_profile_image_base64'):
            image = self.cleaned_data['club_profile_image_base64']
            image_data = image.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
            club.club_profile_image_base64 = base64_encoded

        if commit:
            club.save()
        return club

class ReceptionistSignupForm(forms.Form):
    """Form for Receptionist signup."""

    # User fields
    username = forms.CharField(label="اسم المستخدم", widget=forms.TextInput(attrs={'class': "input-style"}))
    email = forms.EmailField(label="البريد الالكتروني", widget=forms.EmailInput(attrs={'class': "input-style"}))
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",'placeholder': 'أدخل كلمة المرور'}))

    # Receptionist fields
    full_name = forms.CharField(label="الاسم الكامل", widget=forms.TextInput(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",'placeholder': 'الاسم كامل'}))
    phone = forms.CharField(label="رقم الهاتف", widget=forms.TextInput(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",'placeholder': 'رقم الهاتف'}))
    club = forms.ModelChoiceField(
        queryset=ClubsModel.objects.all(),
        label="النادي",
        widget=forms.Select(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"})
    )
    about = forms.CharField(
        label="معلومات إضافية",
        required=False,
        widget=forms.Textarea(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500", 'rows': 3, 'placeholder': 'معلومات إضافية'})
    )

class AdministratorSignupForm(forms.Form):
    """Form for Administrator signup."""

    # User fields
    username = forms.CharField(label="اسم المستخدم", widget=forms.TextInput(attrs={'class': "input-style"}))
    email = forms.EmailField(label="البريد الالكتروني", widget=forms.EmailInput(attrs={'class': "input-style"}))
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",'placeholder': 'أدخل كلمة المرور'}))

    # Receptionist fields
    full_name = forms.CharField(label="الاسم الكامل", widget=forms.TextInput(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",'placeholder': 'الاسم كامل'}))
    phone = forms.CharField(label="رقم الهاتف", widget=forms.TextInput(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",'placeholder': 'رقم الهاتف'}))
    club = forms.ModelChoiceField(
        queryset=ClubsModel.objects.all(),
        label="النادي",
        widget=forms.Select(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"})
    )
    about = forms.CharField(
        label="معلومات إضافية",
        required=False,
        widget=forms.Textarea(attrs={'class': "w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500", 'rows': 3, 'placeholder': 'معلومات إضافية'})
    )

class ForgotPasswordForm(forms.Form):
    """Form for requesting password reset"""

    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 rounded-lg border border-indigo-200 focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 placeholder-indigo-300 text-indigo-800 transition-all',
            'placeholder': 'أدخل بريدك الإلكتروني',
            'required': True
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
        return email

class ResetPasswordForm(forms.Form):
    """Form for resetting password with new password"""

    new_password = forms.CharField(
        label="كلمة المرور الجديدة",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 rounded-lg border border-indigo-200 focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 placeholder-indigo-300 text-indigo-800 transition-all',
            'placeholder': 'أدخل كلمة المرور الجديدة',
            'required': True
        })
    )

    confirm_password = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 rounded-lg border border-indigo-200 focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 placeholder-indigo-300 text-indigo-800 transition-all',
            'placeholder': 'أعد إدخال كلمة المرور الجديدة',
            'required': True
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError({
                    'confirm_password': 'كلمات المرور غير متطابقة.'
                })

            if len(new_password) < 8:
                raise ValidationError({
                    'new_password': 'كلمة المرور يجب أن تكون 8 أحرف على الأقل.'
                })

        return cleaned_data


class VendorRegistrationForm(forms.ModelForm):

    # Business document file field
    business_document_file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'input-style',
            'accept': '.pdf,.jpg,.jpeg,.png',
            'id': 'business_document_file'
        }),
        label="ملف الوثيقة التجارية"
    )

    # Add terms acceptance checkbox
    accept_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        }),
        label="أوافق على سياسة الخصوصية وشروط الاستخدام"
    )

    class Meta:
        model = CoachProfile
        fields = [
            'full_name',
            'phone',
            'email',
            'activity_type',
            'city',
            'district',
            'street',
            'business_name',
            'description',
            'business_document_type',
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'الاسم الكامل',
                'class': 'input-style'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'رقم الهاتف',
                'class': 'input-style'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'البريد الإلكتروني',
                'class': 'input-style'
            }),
            'activity_type': forms.Select(attrs={
                'class': 'input-style'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'المدينة',
                'class': 'input-style'
            }),
            'district': forms.TextInput(attrs={
                'placeholder': 'الحي',
                'class': 'input-style'
            }),
            'street': forms.TextInput(attrs={
                'placeholder': 'الشارع',
                'class': 'input-style'
            }),
            'business_name': forms.TextInput(attrs={
                'placeholder': 'اسم النشاط التجاري',
                'class': 'input-style'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'وصف الخدمة',
                'rows': 4,
                'class': 'input-style'
            }),
            'business_document_type': forms.Select(attrs={
                'class': 'input-style',
                'id': 'business_document_type'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required except description and business_document_file
        for field_name, field in self.fields.items():
            if field_name not in ['description', 'business_document_file']:
                field.required = True



class VendorApprovalForm(forms.Form):
    """Form for directors to approve/reject vendors"""
    action = forms.ChoiceField(
        choices=[
            ('approve', 'موافقة'),
            ('reject', 'رفض')
        ],
        widget=forms.RadioSelect()
    )

    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'ملاحظات (اختياري)',
            'rows': 3,
            'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        required=False,
        label="ملاحظات"
    )