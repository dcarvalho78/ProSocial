from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name','slug','description','website','industry','location','logo','banner_image']
        widgets = {'description': forms.Textarea(attrs={'rows':4})}
