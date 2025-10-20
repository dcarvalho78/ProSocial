from django import forms
from .models import Post
from companies.models import Company

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content','company','image']
        widgets = {'content': forms.Textarea(attrs={'rows':3,'placeholder':'What do you want to share?'})}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['company'].queryset = Company.objects.filter(admins=user)
        else:
            self.fields['company'].queryset = Company.objects.none()
        self.fields['company'].required = False
