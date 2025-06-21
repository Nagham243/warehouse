from django import forms
from accounts.models import StudentProfile, CoachProfile,ReceptionistProfile
from .models import SalonBooking
from students.models import ServicesModel
from datetime import datetime


class SalonBookingForm(forms.Form):
    notes = forms.CharField(
        required=False,
        label="ملاحظات",
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'rows': 3
        })
    )

class ServiceSelectionForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=ServicesModel.objects.all(),
        label="نوع الخدمة",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'onchange': 'updateServiceDetails(this)'
        })
    )
    coach = forms.ModelChoiceField(
        queryset=CoachProfile.objects.none(),
        label="اختر الموظف",
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-indigo-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
        })
    )
    duration = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(ServiceSelectionForm, self).__init__(*args, **kwargs)

        if 'data' in kwargs:
            data = kwargs['data']
            service_id = data.get(f'{self.prefix}-service')
        elif 'initial' in kwargs:
            service_id = kwargs['initial'].get('service')
        else:
            service_id = None

        if service_id:
            try:
                service = ServicesModel.objects.get(id=service_id)
                self.fields['coach'].queryset = service.coaches.all()
            except ServicesModel.DoesNotExist:
                self.fields['coach'].queryset = CoachProfile.objects.none()
        else:
            self.fields['coach'].queryset = CoachProfile.objects.none()


class ReceptionistProfileForm(forms.ModelForm):
    class Meta:
        model = ReceptionistProfile
        fields = ['full_name', 'phone', 'email', 'about']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'email': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'about': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500', 'rows': 4}),
        }