from django import forms
from accounts.models import CoachProfile

class CoachProfileForm(forms.ModelForm):
    class Meta:
        model = CoachProfile
        fields = [
            'full_name', 'phone', 'email', 'activity_type',
            'business_name', 'description', 'business_document_type',
            'city', 'district', 'street'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200',
                'placeholder': 'أدخل الاسم الكامل'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200',
                'placeholder': 'أدخل رقم الهاتف'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200',
                'placeholder': 'أدخل البريد الإلكتروني'
            }),
            'activity_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200 bg-white cursor-pointer'
            }),
            'business_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200',
                'placeholder': 'أدخل اسم النشاط التجاري'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200 min-h-[100px] resize-vertical',
                'placeholder': 'أدخل وصف الخدمة',
                'rows': 4
            }),
            'business_document_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200 bg-white cursor-pointer'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200',
                'placeholder': 'أدخل المدينة'
            }),
            'district': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200',
                'placeholder': 'أدخل الحي'
            }),
            'street': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-rose-400 transition-all duration-200',
                'placeholder': 'أدخل الشارع'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make some fields required
        self.fields['full_name'].required = True
        self.fields['phone'].required = True
        self.fields['email'].required = True
        self.fields['business_name'].required = True
        self.fields['activity_type'].required = True

        # Add custom validation messages
        self.fields['email'].error_messages = {
            'invalid': 'يرجى إدخال بريد إلكتروني صحيح',
            'required': 'البريد الإلكتروني مطلوب'
        }

        self.fields['phone'].error_messages = {
            'required': 'رقم الهاتف مطلوب'
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError('رقم الهاتف يجب أن يحتوي على أرقام فقط')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists for another coach
            existing_coach = CoachProfile.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None)
            if existing_coach.exists():
                raise forms.ValidationError('هذا البريد الإلكتروني مستخدم من قبل مدرب آخر')
        return email