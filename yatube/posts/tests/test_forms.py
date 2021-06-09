from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User

User = get_user_model()


class NewPostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create(username='test_user')
        cls.user2 = User.objects.create(username='second_user')
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем авторизованного пользователя, не автора поста
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_record_new_post_in_bd(self):
        """Проверка, что при создании поста добавляется запись в БД"""
        # Подсчитаем количество записей в базе
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, перенаправлен ли пользователь на главную страницу
        # после создания поста
        self.assertRedirects(response, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_desired_post_in_bd(self):
        """При редактировании поста изменяется нужная запись в БД"""
        # Подсчитаем количество записей в базе
        post_count = Post.objects.count()
        # Получаем изначальный текст поста
        text_post1 = NewPostFormTests.post1.text
        form_data = {
            'text': 'Новый тестовый текст',
        }
        # Отправляем POST-запрос на изменение текста поста
        self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': 'test_user', 'post_id': NewPostFormTests.post1.id
            }),
            data=form_data,
            follow=True
        )
        # Получаем измененный текст поста
        new_text_post1 = Post.objects.get(id=NewPostFormTests.post1.id).text
        # Проверим,
        # что начальный текст не равен тексту после выполнения запроса
        self.assertNotEqual(
            text_post1, new_text_post1
        )
        # Проверим, что колличество постов не изменилось
        self.assertEqual(Post.objects.count(), post_count)

    def test_guest_user_cannot_post(self):
        """
        Неавторизованный пользователь не может создать пост
        при помощи ПОСТ-запроса
        """
        # Подсчитаем количество записей в базе
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        # Отправляем POST-запрос
        self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверим, что количество записей не изменилось
        self.assertEqual(Post.objects.count(), post_count)
