from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User

User = get_user_model()


class NewPostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.user2 = User.objects.create(username='second_user')
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_record_new_post_in_bd(self):
        """
        Проверка, что при создании поста добавляется запись в БД.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_desired_post_in_bd(self):
        """
        При редактировании поста изменяется нужная запись в БД.
        """
        post_count = Post.objects.count()
        text_post1 = NewPostFormTests.post1.text
        form_data = {
            'text': 'Новый тестовый текст',
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': 'test_user', 'post_id': NewPostFormTests.post1.id
            }),
            data=form_data,
            follow=True
        )
        new_text_post1 = Post.objects.get(id=NewPostFormTests.post1.id).text
        self.assertNotEqual(
            text_post1, new_text_post1
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_guest_user_cannot_post(self):
        """
        Неавторизованный пользователь не может создать пост
        при помощи ПОСТ-запроса.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
