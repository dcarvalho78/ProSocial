from django import forms
from .models import Post, Reply, UserProfile
from .models import UserProfile, Company, Job, Skill
from .models import Post, Reply, UserProfile, Company, Job, Skill, Project


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'availability', 'skills']
        widgets = {
            'skills': forms.CheckboxSelectMultiple,
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'avatar']  # Avatar hinzugefügt

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'employment_type']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Was gibt\'s Neues? #hashtags @freunde ...'}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Antwort schreiben...'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Über mich...'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'url', 'image', 'skills']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.CheckboxSelectMultiple(),
        }
