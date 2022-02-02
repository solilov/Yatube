from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    """
    Админка для модели Post.
    """
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """
    Админка для модели Group.
    """
    list_display = ('title', 'slug', 'description')
    search_fields = ("title",)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
