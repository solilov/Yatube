# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post, User


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='test_user')
        cls.user2 = User.objects.create_user(username='test_user2')
        cls.group = Group.objects.create(
            title='test_name',
            slug='1'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        # Кортеж всех url-ов
        cls.urls = {
            'home': '/',
            'group1': f'/group/{PostURLTests.group.slug}/',
            'new': '/new',
            'edit': (
                f'/{PostURLTests.user.username}/{PostURLTests.post.id}/edit/'
            ),
            'profile': f'/{PostURLTests.user.username}/',
            'post': f'/{PostURLTests.user.username}/{PostURLTests.post.id}/',
            'test': '/test_test/',
            'comment': (
                f'/{PostURLTests.user.username}'
                f'/{PostURLTests.post.id}'
                f'/comment/'
            )
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Авторизуем пользователя 2
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_server_return_404(self):
        """Возвращает ли сервер код 404"""
        response = self.guest_client.get(self.urls['test'])
        self.assertEqual(response.status_code, 404)

    def test_home_group_profile_post_available_everyone(self):
        """
        Страницы home, group, profile, post доступны всем
        """
        # Список url-ов доступных всем пользователям
        url = [
            self.urls['home'],
            self.urls['group1'],
            self.urls['profile'],
            self.urls['post']
        ]
        for name in url:
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertEqual(response.status_code, 200)

    def test_new_post_page(self):
        """Страница /new доступна авторизованному пользователю."""
        response = self.authorized_client.get(self.urls['new'])
        self.assertEqual(response.status_code, 200)

    def test_page_post_edit_available_non_authorized_client(self):
        """
        Страница редактирования поста не доступна не
        авторизованному пользователю
        """
        response = self.guest_client.get(self.urls['edit'])
        self.assertNotEqual(response.status_code, 200)

    def test_page_post_edit_available_authorized_client_not_author(self):
        """
        Страница редактирования поста не доступна
        авторизованному пользователю, но не автору.
        """
        response = self.authorized_client2.get(self.urls['edit'])
        self.assertNotEqual(response.status_code, 200)

    def test_page_post_edit_available_authorized_client_author(self):
        """
        Страница редактирования поста доступна авторизованному
        пользователю, который является автором
        """
        response = self.authorized_client.get(self.urls['edit'])
        self.assertEqual(response.status_code, 200)

    def test_page_post_edit_redirect_authorized_client_not_author(self):
        """
        Страница редактирования поста не доступна
        авторизованному пользователю, но не автору
        """
        response = self.authorized_client2.get(self.urls['edit'],
                                               follow=True)
        self.assertRedirects(response, self.urls['post'])

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.urls['home']: 'posts/index.html',
            self.urls['group1']: 'posts/group.html',
            self.urls['new']: 'posts/new.html',
            self.urls['edit']: 'posts/new.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_comment_post_available_non_authorized_client(self):
        """
        Страница /comments не доступна не авторизованному пользователю.
        """
        response = self.guest_client.get(self.urls['comment'])
        self.assertNotEqual(response.status_code, 200)
