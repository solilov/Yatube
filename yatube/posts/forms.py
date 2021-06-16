from django.forms import ModelForm, widgets

from .models import Comment, Post


class PostForm(ModelForm):
    """ Форма постов """
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        widgets = {
            'text': widgets.Textarea(attrs={
                'class': 'form_control',
                'placeholder': 'Тест поста'
            })
        }


class CommentForm(ModelForm):
    """ Форма комментариев """
    class Meta:
        model = Comment
        fields = ('text',)

        widgets = {
            'text': widgets.Textarea(attrs={
                'class': 'form_control',
                'placeholder': 'Текст комментария'
            })
        }
