from django import forms
from .models import Job
from companies.models import Company

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['company','title','description','location','employment_type','salary_min','salary_max']
        widgets = {'description': forms.Textarea(attrs={'rows':6})}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['company'].queryset = Company.objects.filter(admins=user)
        else:
            self.fields['company'].queryset = Company.objects.none()
