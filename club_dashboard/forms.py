from django import forms
from accounts.models import StudentProfile, CoachProfile, DirectorProfile,ReceptionistProfile,AdministrativeProfile, AccountantProfile
from students.models import Blog, ServicesModel, ProductsClassificationModel, ServicesClassificationModel, ProductsModel
from .models import ProductShipment


class StudentProfileForm(forms.ModelForm):

    class Meta:
        model = StudentProfile
        fields = ['full_name', 'phone', 'birthday', 'manual_status']

        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder':'اسم الكامل', 'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'phone': forms.TextInput(attrs={'placeholder':'رقم الهاتف', 'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'birthday': forms.DateInput(attrs={'type':'date', 'placeholder':'تاريخ الميلاد', 'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'manual_status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
        }


class ImportStudentsForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
            'accept': '.xlsx,.xls,.csv'
        }),
        help_text="Upload Excel (.xlsx, .xls) or CSV file"
    )

# forms.py
from django import forms
from club_dashboard.models import  Commission

class CoachProfileForm(forms.ModelForm):
    vendor_classification = forms.ChoiceField(
        choices=[],  # Will be populated dynamically
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400'
        }),
        label="تصنيف البائع"
    )

    class Meta:
        model = CoachProfile
        fields = ['full_name', 'phone', 'email', 'activity_type', 'business_name',
                  'description', 'city', 'district', 'street', 'profile_image_base64', 'vendor_classification']

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400',
                'placeholder': 'الاسم الكامل'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400',
                'placeholder': 'رقم الهاتف'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400',
                'placeholder': 'البريد الإلكتروني'
            }),
            'activity_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400'
            }),
            'business_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400',
                'placeholder': 'اسم النشاط التجاري'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400',
                'placeholder': 'وصف الخدمة',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400',
                'placeholder': 'المدينة'
            }),
            'district': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400',
                'placeholder': 'الحي'
            }),
            'street': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50 transition-all duration-300 hover:bg-blue-50 hover:border-blue-400',
                'placeholder': 'الشارع'
            }),
            'profile_image_base64': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        club = kwargs.pop('club', None)
        super().__init__(*args, **kwargs)

        if club:
            # Get available classifications for this club
            classifications = Commission.objects.filter(
                club=club,
                commission_type='vendor',
                is_active=True
            ).values_list('vendor_classification', 'name').distinct()

            # Create choices with Arabic labels
            classification_choices = []
            for classification, name in classifications:
                # You can customize these labels based on your needs
                if classification == 'gold':
                    label = f"ذهبي - {name}"
                elif classification == 'silver':
                    label = f"فضي - {name}"
                elif classification == 'bronze':
                    label = f"برونزي - {name}"
                else:
                    label = f"{classification} - {name}"
                classification_choices.append((classification, label))

            # Add default option if no classifications exist
            if not classification_choices:
                classification_choices = [('silver', 'فضي - افتراضي')]

            self.fields['vendor_classification'].choices = classification_choices



from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class ArticleModelForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'desc', 'img', 'body']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300',
                'placeholder': 'Enter article title...'
            }),
            'desc': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300',
                'placeholder': 'Brief description of the article...'
            }),
            'img': forms.FileInput(attrs={
                'accept': "image/*",
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300'
            }),
            'body': CKEditorUploadingWidget(config_name='article_editor')
        }


class ServicesModelForm(forms.ModelForm):
    classification = forms.ModelChoiceField(
        queryset=ServicesClassificationModel.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
        })
    )

    discounted_price = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors duration-300 hover:border-gray-400',
            'step': '0.01'
        })
    )

    class Meta:
        model = ServicesModel
        fields = ['title', 'desc', 'price', 'pricing_period_months','discounted_price', 'is_enabled', 'coaches']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'desc': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'step': '0.01'}),
            'pricing_period_months': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'is_enabled': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 mr-2'}),
            'coaches': forms.SelectMultiple(attrs={
            'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
        }

class ServicesClassificationModelForm(forms.ModelForm):
    class Meta:
        model = ServicesClassificationModel
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'})
        }




class ProductsModelForm(forms.ModelForm):

    class Meta:
        model = ProductsModel
        fields = ['title','desc', 'price', 'stock', 'classification', 'manufacturing_date', 'expiration_date', 'is_enabled']

        widgets = {
        'title': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        'desc': forms.Textarea(attrs={'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        'price':forms.NumberInput(attrs={'step': 0.00, 'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        'stock':forms.NumberInput(attrs={'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        'classification':forms.SelectMultiple(attrs={'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        'manufacturing_date': forms.DateInput(attrs={'type': 'date', 'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        'expiration_date': forms.DateInput(attrs={'type': 'date', 'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        'is_enabled':forms.CheckboxInput(),
        }

class ProductsClassificationModelForm(forms.ModelForm):

    class Meta:
        model = ProductsClassificationModel
        fields = ['title']

        widgets = {
            'title':forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'})
        }

class DirectorProfileForm(forms.ModelForm):
    profile_image_base64 = forms.ImageField(required=False, label="صورة الملف الشخصي")
    class Meta:
        model = DirectorProfile
        fields = ['full_name', 'phone', 'about']  # No 'club' field

        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'اسم الكامل',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'رقم الهاتف',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'about': forms.Textarea(attrs={
                'placeholder': 'نبذة عن المدير',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'rows': 3
            }),
        }

class ReceptionistProfileForm(forms.ModelForm):
    class Meta:
        model = ReceptionistProfile
        fields = ['full_name', 'phone', 'email', 'about']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'اسم الكامل',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'رقم الهاتف',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'البريد الالكتروني',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'about': forms.Textarea(attrs={
                'placeholder': 'نبذة عن الاستقبال',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'rows': 3
            }),
        }

class AdministratorProfileForm(forms.ModelForm):
    class Meta:
        model = AdministrativeProfile
        fields = ['full_name', 'phone', 'email', 'about']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'اسم الكامل',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'رقم الهاتف',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'البريد الالكتروني',

                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'about': forms.Textarea(attrs={
                'placeholder': 'نبذة عن الاداري',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False



class AccountantProfileForm(forms.ModelForm):
    class Meta:
        model = AccountantProfile
        fields = ['full_name', 'phone', 'email', 'about']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'الاسم الكامل',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'رقم الهاتف',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'البريد الإلكتروني',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'about': forms.Textarea(attrs={
                'placeholder': 'نبذة عن المحاسب',
                'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False


class ProductShipmentForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=ProductsModel.objects.all(),
        label="المنتج",
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'})
    )

    class Meta:
        model = ProductShipment
        fields = ['product', 'quantity', 'manufacturing_date', 'expiration_date', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'min': 1
            }),
            'manufacturing_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'type': 'date'
            }),
            'expiration_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        club = kwargs.pop('club', None)
        super(ProductShipmentForm, self).__init__(*args, **kwargs)

        if club:
            self.fields['product'].queryset = ProductsModel.objects.filter(club=club)



from django import forms
from .models import Category, SubCategory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Enter category description',
                'rows': 4
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            })
        }
        labels = {
            'name': 'Category Name',
            'description': 'Description',
            'image': 'Category Image',
            'is_active': 'Active'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            # Check for duplicate names (exclude current instance if editing)
            queryset = Category.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError('A category with this name already exists.')
        return name


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'name': forms.TextInput(attrs={
                'class': 'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Enter subcategory name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Enter subcategory description',
                'rows': 4
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            })
        }
        labels = {
            'category': 'Parent Category',
            'name': 'Subcategory Name',
            'description': 'Description',
            'image': 'Subcategory Image',
            'is_active': 'Active'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active categories in the dropdown
        self.fields['category'].queryset = Category.objects.filter(is_active=True).order_by('name')
        self.fields['category'].empty_label = "Select a category"

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        name = cleaned_data.get('name')

        if category and name:
            name = name.strip()
            # Check for duplicate subcategory names within the same category
            queryset = SubCategory.objects.filter(category=category, name__iexact=name)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError(f'A subcategory with the name "{name}" already exists in the "{category.name}" category.')

        return cleaned_data


from django import forms
from .models import ProductsModel

class ProductApprovalForm(forms.Form):
    """Form for approving products with notes"""
    approval_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'ملاحظات الموافقة (اختياري)...'
        }),
        required=False,
        label='ملاحظات الموافقة'
    )

class ProductRejectionForm(forms.Form):
    """Form for rejecting products with reason"""
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500',
            'rows': 3,
            'placeholder': 'سبب الرفض...',
            'required': True
        }),
        required=True,
        label='سبب الرفض'
    )

class BulkProductActionForm(forms.Form):
    """Form for bulk actions on products"""
    ACTION_CHOICES = [
        ('approve', 'قبول'),
        ('reject', 'رفض'),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='الإجراء'
    )

    product_ids = forms.ModelMultipleChoiceField(
        queryset=ProductsModel.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='المنتجات المحددة'
    )

    bulk_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 2,
            'placeholder': 'ملاحظات (اختياري)...'
        }),
        required=False,
        label='ملاحظات'
    )

class ProductFilterForm(forms.Form):
    """Form for filtering products"""
    STATUS_CHOICES = [
        ('all', 'جميع المنتجات'),
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبولة'),
        ('rejected', 'مرفوضة'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='الحالة'
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'البحث بالاسم، البائع، أو البريد الإلكتروني...'
        }),
        label='البحث'
    )





from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Commission
from django.db import models

class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = [
            'name', 'commission_type', 'commission_rate',
            'vendor_classification', 'start_date', 'end_date',
            'discount_amount', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل الوصف'
            }),
            'commission_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'commission_type'
            }),
            'commission_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل نسبة العمولة',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
            'vendor_classification': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'vendor_classification',
                'placeholder': 'أدخل تصنيف البائع (مثال: silver, gold, platinum)',
                'list': 'classification_list'  # For datalist suggestions
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'start_date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'end_date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل مقدار الخصم',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.club = kwargs.pop('club', None)
        super().__init__(*args, **kwargs)
        self.fields['discount_amount'].required = False

        # Set initial values based on commission type
        if not self.instance.pk:
            self.fields['vendor_classification'].required = False
            self.fields['start_date'].required = False
            self.fields['end_date'].required = False
            # Set default value for vendor_classification
            self.fields['vendor_classification'].initial = 'silver'

        # Get existing classifications for suggestions
        if self.club:
            self.existing_classifications = Commission.get_available_classifications(self.club)

    # In forms.py
    def clean(self):
        cleaned_data = super().clean()
        commission_type = cleaned_data.get('commission_type')
        discount_amount = cleaned_data.get('discount_amount')
        vendor_classification = cleaned_data.get('vendor_classification')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        commission_rate = cleaned_data.get('commission_rate')

        # Validate vendor type commission
        if commission_type == 'vendor':
            if not vendor_classification:
                raise ValidationError('تصنيف البائع مطلوب لعمولة البائع')

            # Clean and normalize vendor classification
            vendor_classification = vendor_classification.strip().lower()
            cleaned_data['vendor_classification'] = vendor_classification

            # Check if classification already exists for this club
            existing_commission = Commission.objects.filter(
                club=self.club,
                commission_type='vendor',
                vendor_classification=vendor_classification,
                is_active=True
            )

            if self.instance.pk:
                existing_commission = existing_commission.exclude(pk=self.instance.pk)

            if existing_commission.exists():
                raise ValidationError(f'يوجد بالفعل عمولة نشطة لتصنيف "{vendor_classification}"')

            # Clear time period fields
            cleaned_data['start_date'] = None
            cleaned_data['end_date'] = None
            cleaned_data['discount_amount'] = None  # Clear discount for vendor type

        # Validate time period commission
        elif commission_type == 'time_period':
            if not start_date or not end_date:
                raise ValidationError('تاريخ البداية والنهاية مطلوبان لعمولة الفترة الزمنية')

            if start_date >= end_date:
                raise ValidationError('تاريخ البداية يجب أن يكون قبل تاريخ النهاية')

            if start_date < timezone.now().date():
                raise ValidationError('تاريخ البداية يجب أن يكون في المستقبل أو اليوم')

            if not discount_amount:
                raise ValidationError('مقدار الخصم مطلوب للعرض الزمني')

            if discount_amount < 0 or discount_amount > 100:
                raise ValidationError('مقدار الخصم يجب أن يكون بين 0 و 100')

            # Check for overlapping time periods
            overlapping_commissions = Commission.objects.filter(
                club=self.club,
                commission_type='time_period',
                is_active=True
            ).filter(
                models.Q(start_date__lte=start_date, end_date__gte=start_date) |
                models.Q(start_date__lte=end_date, end_date__gte=end_date) |
                models.Q(start_date__gte=start_date, end_date__lte=end_date)
            )

            if self.instance.pk:
                overlapping_commissions = overlapping_commissions.exclude(pk=self.instance.pk)

            if overlapping_commissions.exists():
                raise ValidationError('يوجد تداخل في الفترات الزمنية مع عمولة أخرى نشطة')

            # Clear vendor classification
            cleaned_data['vendor_classification'] = None

        # Validate commission rate
        if commission_rate is not None:
            if commission_rate < 0 or commission_rate > 100:
                raise ValidationError('نسبة العمولة يجب أن تكون بين 0 و 100')

        return cleaned_data


class BulkVendorCommissionForm(forms.Form):
    """Form for bulk assignment of commissions to vendors"""
    vendors = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='البائعين'
    )
    commission = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='العمولة'
    )

    def __init__(self, *args, **kwargs):
        club = kwargs.pop('club', None)
        super().__init__(*args, **kwargs)

        if club:
            # Get approved vendors for the club
            self.fields['vendors'].queryset = club.coachprofile_set.filter(
                approval_status='approved'
            )

            # Get active vendor commissions for the club
            self.fields['commission'].queryset = Commission.objects.filter(
                club=club,
                commission_type='vendor',
                is_active=True
            )


class CommissionFilterForm(forms.Form):
    """Form for filtering commissions"""
    COMMISSION_TYPE_CHOICES = [('', 'جميع الأنواع')] + Commission.COMMISSION_TYPES
    STATUS_CHOICES = [
        ('', 'جميع الحالات'),
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
    ]

    commission_type = forms.ChoiceField(
        choices=COMMISSION_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm'
        }),
        label='نوع العمولة'
    )

    # Dynamic vendor classification field
    vendor_classification = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'البحث في تصنيف البائع...',
            'list': 'filter_classification_list'
        }),
        label='تصنيف البائع'
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm'
        }),
        label='الحالة'
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'البحث في اسم العمولة أو النسبة...'
        }),
        label='البحث'
    )

    def __init__(self, *args, **kwargs):
        self.club = kwargs.pop('club', None)
        super().__init__(*args, **kwargs)

        # Get existing classifications for suggestions
        if self.club:
            self.existing_classifications = Commission.get_available_classifications(self.club)


from django import forms
from students.models import ServicesModel

class ServiceApprovalForm(forms.Form):
    """Form for approving services with notes"""
    approval_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'ملاحظات الموافقة (اختياري)...'
        }),
        required=False,
        label='ملاحظات الموافقة'
    )

class ServiceRejectionForm(forms.Form):
    """Form for rejecting services with reason"""
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500',
            'rows': 3,
            'placeholder': 'سبب الرفض...',
            'required': True
        }),
        required=True,
        label='سبب الرفض'
    )

class BulkServiceActionForm(forms.Form):
    """Form for bulk actions on services"""
    ACTION_CHOICES = [
        ('approve', 'قبول'),
        ('reject', 'رفض'),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='الإجراء'
    )

    service_ids = forms.ModelMultipleChoiceField(
        queryset=ServicesModel.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='الخدمات المحددة'
    )

    bulk_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 2,
            'placeholder': 'ملاحظات (اختياري)...'
        }),
        required=False,
        label='ملاحظات'
    )

class ServiceFilterForm(forms.Form):
    """Form for filtering services"""
    STATUS_CHOICES = [
        ('all', 'جميع الخدمات'),
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبولة'),
        ('rejected', 'مرفوضة'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='الحالة'
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'البحث بالاسم، المدرب، أو البريد الإلكتروني...'
        }),
        label='البحث'
    )



# forms.py
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import RefundDispute, RefundDisputeAttachment, RefundStatus, RefundType, DisputeType


class RefundDisputeForm(forms.ModelForm):
    """Form for creating/editing refund disputes"""

    class Meta:
        model = RefundDispute
        fields = [
            'title', 'description', 'deal', 'refund_type', 'dispute_type',
            'requested_refund_amount', 'priority', 'client_evidence', 'vendor_response'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter dispute title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issue in detail'
            }),
            'deal': forms.Select(attrs={'class': 'form-control'}),
            'refund_type': forms.Select(attrs={'class': 'form-control'}),
            'dispute_type': forms.Select(attrs={'class': 'form-control'}),
            'requested_refund_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'vendor_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Vendor response (if any)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter deals based on user permissions
        if self.user and not self.user.is_staff:
            # If not staff, only show user's own orders
            self.fields['deal'].queryset = self.fields['deal'].queryset.filter(
                user=self.user
            )

    def clean_requested_refund_amount(self):
        """Validate requested refund amount"""
        amount = self.cleaned_data.get('requested_refund_amount')
        deal = self.cleaned_data.get('deal')

        if amount and deal:
            if amount > deal.total_price:
                raise ValidationError(
                    f"Requested refund amount cannot exceed order total of {deal.total_price}"
                )

            if amount <= 0:
                raise ValidationError("Refund amount must be greater than 0")

        return amount

    def clean(self):
        """Additional form validation"""
        cleaned_data = super().clean()
        deal = cleaned_data.get('deal')

        if deal:
            # Check if there's already an active dispute for this order
            existing_dispute = RefundDispute.objects.filter(
                deal=deal,
                status__in=[RefundStatus.PENDING, RefundStatus.INVESTIGATING]
            ).exclude(pk=self.instance.pk if self.instance else None)

            if existing_dispute.exists():
                raise ValidationError(
                    "There is already an active dispute for this order."
                )

        return cleaned_data


class RefundDecisionForm(forms.Form):
    """Form for admin to make decision on refund dispute"""

    DECISION_CHOICES = [
        ('approve', 'Approve Refund'),
        ('reject', 'Reject Refund'),
        ('investigate', 'Needs Investigation'),
    ]

    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    approved_refund_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        help_text="Amount to be refunded (required if approving)"
    )

    vendor_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'max': '100'
        }),
        help_text="Percentage of refund amount vendor will receive"
    )

    client_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'max': '100'
        }),
        help_text="Percentage of refund amount client will receive"
    )

    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Explain why the refund is being rejected'
        }),
        required=False,
        help_text="Required if rejecting the refund"
    )

    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Internal notes for this decision'
        }),
        required=False,
        help_text="Internal notes (not visible to client/vendor)"
    )

    def __init__(self, *args, **kwargs):
        self.dispute = kwargs.pop('dispute', None)
        super().__init__(*args, **kwargs)

        # Set initial values if dispute is provided
        if self.dispute:
            self.fields['approved_refund_amount'].initial = self.dispute.requested_refund_amount

    def clean(self):
        """Validate the form based on decision"""
        cleaned_data = super().clean()
        decision = cleaned_data.get('decision')
        approved_amount = cleaned_data.get('approved_refund_amount')
        vendor_percentage = cleaned_data.get('vendor_percentage', 0)
        client_percentage = cleaned_data.get('client_percentage', 0)
        rejection_reason = cleaned_data.get('rejection_reason')

        # Validation based on decision
        if decision == 'approve':
            if not approved_amount:
                raise ValidationError({
                    'approved_refund_amount': 'Approved refund amount is required when approving.'
                })

            if approved_amount <= 0:
                raise ValidationError({
                    'approved_refund_amount': 'Approved refund amount must be greater than 0.'
                })

            if self.dispute and approved_amount > self.dispute.requested_refund_amount:
                raise ValidationError({
                    'approved_refund_amount': 'Approved amount cannot exceed requested amount.'
                })

            # Validate percentages
            if vendor_percentage + client_percentage != 100:
                raise ValidationError(
                    'Vendor and client percentages must sum to 100%.'
                )

        elif decision == 'reject':
            if not rejection_reason:
                raise ValidationError({
                    'rejection_reason': 'Rejection reason is required when rejecting.'
                })

        return cleaned_data


class RefundAttachmentForm(forms.ModelForm):
    """Form for uploading refund dispute attachments"""

    class Meta:
        model = RefundDisputeAttachment
        fields = ['file', 'description', 'file_type']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,application/pdf,.doc,.docx'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of this file'
            }),
            'file_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file')

        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 10MB.')

            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx', '.txt']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError(
                    f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
                )

        return file


class RefundFilterForm(forms.Form):
    """Form for filtering refund disputes"""

    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + RefundStatus.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    dispute_type = forms.ChoiceField(
        choices=[('', 'All Types')] + DisputeType.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    priority = forms.ChoiceField(
        choices=[
            ('', 'All Priorities'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    refund_type = forms.ChoiceField(
        choices=[('', 'All Refund Types')] + RefundType.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, description, order ID, or email'
        })
    )

    amount_min = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min amount',
            'step': '0.01'
        })
    )

    amount_max = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max amount',
            'step': '0.01'
        })
    )

    def clean(self):
        """Validate date range and amount range"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        amount_min = cleaned_data.get('amount_min')
        amount_max = cleaned_data.get('amount_max')

        # Validate date range
        if date_from and date_to and date_from > date_to:
            raise ValidationError('Start date cannot be after end date.')

        # Validate amount range
        if amount_min and amount_max and amount_min > amount_max:
            raise ValidationError('Minimum amount cannot be greater than maximum amount.')

        return cleaned_data


class BulkActionForm(forms.Form):
    """Form for bulk actions on disputes"""

    ACTION_CHOICES = [
        ('', 'Select Action'),
        ('mark_investigating', 'Mark as Investigating'),
        ('set_priority_low', 'Set Priority: Low'),
        ('set_priority_medium', 'Set Priority: Medium'),
        ('set_priority_high', 'Set Priority: High'),
        ('set_priority_urgent', 'Set Priority: Urgent'),
        ('export_selected', 'Export Selected'),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    selected_disputes = forms.CharField(
        widget=forms.HiddenInput(),
        help_text="Comma-separated list of dispute IDs"
    )

    def clean_selected_disputes(self):
        """Validate selected disputes"""
        disputes_str = self.cleaned_data.get('selected_disputes', '')

        if not disputes_str:
            raise ValidationError('No disputes selected.')

        try:
            dispute_ids = [int(id.strip()) for id in disputes_str.split(',') if id.strip()]

            # Validate that all IDs exist
            existing_disputes = RefundDispute.objects.filter(id__in=dispute_ids)
            if existing_disputes.count() != len(dispute_ids):
                raise ValidationError('Some selected disputes do not exist.')

            return dispute_ids

        except ValueError:
            raise ValidationError('Invalid dispute IDs provided.')

    def clean(self):
        """Validate action and selected disputes combination"""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')

        if not action:
            raise ValidationError('Please select an action.')

        return cleaned_data


class RefundResolutionForm(forms.Form):
    """Form for resolving disputes"""

    resolution_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Explain how this dispute was resolved'
        }),
        help_text="Provide details about the resolution"
    )

    notify_parties = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Send notification to client and vendor"
    )

    def clean_resolution_notes(self):
        """Validate resolution notes"""
        notes = self.cleaned_data.get('resolution_notes')

        if not notes or len(notes.strip()) < 10:
            raise ValidationError('Resolution notes must be at least 10 characters long.')

        return notes.strip()


class RefundSearchForm(forms.Form):
    """Advanced search form for refunds"""

    ORDER_BY_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('-updated_at', 'Recently Updated'),
        ('requested_refund_amount', 'Amount: Low to High'),
        ('-requested_refund_amount', 'Amount: High to Low'),
        ('priority', 'Priority'),
        ('status', 'Status'),
    ]

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search disputes...',
            'autocomplete': 'off'
        })
    )

    status = forms.MultipleChoiceField(
        choices=RefundStatus.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    dispute_type = forms.MultipleChoiceField(
        choices=DisputeType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    priority = forms.MultipleChoiceField(
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    order_by = forms.ChoiceField(
        choices=ORDER_BY_CHOICES,
        initial='-created_at',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Show only overdue disputes (>7 days old)"
    )

    has_attachments = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Show only disputes with attachments"
    )

