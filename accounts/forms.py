from django import forms
from django.contrib.auth import get_user_model
from .models import Skill

User = get_user_model()

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password (repeat)', widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','headline','location']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

class ProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(), required=False,
        widget=forms.SelectMultiple(attrs={'size': 8})
    )

    class Meta:
        model = User
        fields = ['first_name','last_name','headline','location','bio','skills',
                  'is_available_for_hire','available_from','availability_note','profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows':4}),
            'available_from': forms.DateInput(attrs={'type':'date'}),
        }
