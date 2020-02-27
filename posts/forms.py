from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        widgets = {
            'group':forms.Select(attrs={'class': 'form-control'}),
            'text':forms.Textarea(attrs={'class': 'form-control'}),
            'image':forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text',]
