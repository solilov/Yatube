from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель сообщества"""
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True)
    description = models.TextField()

    class Meta:
        """Дефолтная сотрировка по названию"""
        ordering = ('title',)

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель поста"""
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="groups")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        """Дефолтная сортировка по дате(от послденего)"""
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев"""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Дефолтная сортировка по дате(от послденего)"""
        ordering = ('-created',)

    def __str__(self):
        return self.text


class Follow(models.Model):
    """Модель подписок"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        """ Проверка на уникальность """
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]
