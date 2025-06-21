from django import forms
from accounts.models import ClubsModel, DirectorProfile

class ClubsForm(forms.ModelForm):

    class Meta:
        model = ClubsModel
        fields = ['name', 'city', 'district', 'street']

        widgets = {
            'name': forms.TextInput(attrs={'class': "w-full px-4 py-2 rounded-md border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:ring-opacity-50 transition duration-150 ease-in-out bg-gray-50"}),
            'city': forms.Select(attrs={'class': "w-full px-4 py-2 rounded-md border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:ring-opacity-50 transition duration-150 ease-in-out bg-gray-50"}),
            'district': forms.TextInput(attrs={'class': "w-full px-4 py-2 rounded-md border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:ring-opacity-50 transition duration-150 ease-in-out bg-gray-50"}),
            'street': forms.TextInput(attrs={'class': "w-full px-4 py-2 rounded-md border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:ring-opacity-50 transition duration-150 ease-in-out bg-gray-50"}),

        }
class DirectorForm(forms.ModelForm):

    class Meta:
        model = DirectorProfile
        fields = ['full_name', 'phone', 'club']

        widgets = {
            'full_name': forms.TextInput(attrs={'class': "w-full px-4 py-2 rounded-md border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:ring-opacity-50 transition duration-150 ease-in-out bg-gray-50"}),
            'phone': forms.TextInput(attrs={'class': "w-full px-4 py-2 rounded-md border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:ring-opacity-50 transition duration-150 ease-in-out bg-gray-50"}),
            'club': forms.TextInput(attrs={'class': "w-full px-4 py-2 rounded-md border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:ring-opacity-50 transition duration-150 ease-in-out bg-gray-50"}),
        }