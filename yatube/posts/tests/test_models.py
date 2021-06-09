from django.test import TestCase

from posts.models import Group, Post, User


class GroupModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_name'
        )

    def test_title_group(self):
        group = GroupModelsTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_title_verbose_name_group(self):
        """verbose_name поля title совпадает с ожидаемым."""
        group = GroupModelsTest.group
        # Получаем из свойста класса Gruop значение verbose_name для title
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Название группы')


class PostModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.post = Post.objects.create(
            text='Тестовый текст, первые 15 символов',
            author=cls.user
        )

    def test_text_post(self):
        post = PostModelsTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post)[:15])
