from django import forms
from django.forms import ModelForm, widgets

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        widgets = {
            'text': widgets.Textarea(attrs={
                'class': 'form_control',
                'placeholder': 'Тест поста'
            })
        }

    def clean_text(self):
        post = self.cleaned_data['text']
        if not post:
            raise forms.ValidationError('Добавьте пост')
        return post


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

        widgets = {
            'text': widgets.Textarea(attrs={
                'class': 'form_control',
                'placeholder': 'Текст комментария'
            })
        }

    def clean_text(self):
        comment = self.cleaned_data['text']
        if not comment:
            raise forms.ValidationError(
                "Не стоит добавлять пустой комментарий")
        return comment
