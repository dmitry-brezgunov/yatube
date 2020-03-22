from django import forms
from .models import Post, Comment, Group

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
        widgets = {
            'text':forms.Textarea(attrs={'class': 'form-control'}),
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'slug', 'description']
        widgets = {
            'title':forms.TextInput(attrs={'class': 'form-control'}),
            'slug':forms.TextInput(attrs={'class': 'form-control'}),
            'description':forms.Textarea(attrs={'class': 'form-control'}),
        }
