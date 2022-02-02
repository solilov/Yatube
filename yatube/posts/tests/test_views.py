import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(username='test_user')
        cls.second = User.objects.create(username='second')
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            image=PostPagesTests.uploaded
        )
        cls.group = Group.objects.create(
            title='test_name',
            slug='test-slug'
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст2',
            author=cls.user,
            group=cls.group,
            image=PostPagesTests.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.second)

    def test_pages_use_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        """
        templates_pages_names = {
            'posts/index.html': reverse('index'),
            'posts/group.html': reverse('group_posts',
                                        kwargs={
                                            'slug': PostPagesTests.group.slug
                                        }),
            'posts/new.html': reverse('new_post')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        """
        Шаблон home сформирован с правильным контекстом.
        """
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        first = response.context.get('page').object_list[-1]
        self.assertEqual(first, PostPagesTests.post1)

    def test_group_page_shows_correct_context(self):
        """
        Шаблон group сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': PostPagesTests.group.slug})
        )
        object1 = response.context.get('page').object_list[0]
        object2 = response.context['group']
        self.assertEqual(object1, PostPagesTests.post2)
        self.assertEqual(object2, PostPagesTests.group)

    def test_new_page_shows_correct_context(self):
        """
        Шаблон new сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_shows_correct_context(self):
        """
        Шаблон post_edit сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={
                'username': 'test_user',
                'post_id': PostPagesTests.post1.id
            }
        ))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        """
        Шаблон profile сформирован с правильным контекстом.
        """
        response = self.guest_client.get(reverse(
            'profile',
            kwargs={
                'username': 'test_user'
            }
        ))
        context = {
            response.context.get('author'): PostPagesTests.user,
            response.context.get(
                'count'
            ): PostPagesTests.user.posts.count(),
            response.context.get('page').object_list[0]: PostPagesTests.post2
        }
        for cont, values in context.items():
            with self.subTest(cont=cont):
                self.assertEqual(cont, values)

    def test_post_shows_correct_context(self):
        """
        Шаблон post сформирован с правильным контекстом.
        """
        response = self.guest_client.get(reverse(
            'post',
            kwargs={
                'username': PostPagesTests.user.username,
                'post_id': PostPagesTests.post1.id
            }
        ))
        context = {
            response.context.get('author'): PostPagesTests.user,
            response.context.get(
                'count'
            ): PostPagesTests.user.posts.count(),
            response.context.get('post'): PostPagesTests.post1
        }
        for cont, values in context.items():
            with self.subTest(cont=cont):
                self.assertEqual(cont, values)

    def test_new_post_with_group_show_in_home_page(self):
        """
        Проверка на то, что пост с группой появляется на главной странице.
        """
        response = self.authorized_client.get(reverse('index'))
        two = response.context.get('page').object_list[0]
        self.assertEqual(two, PostPagesTests.post2)

    def test_new_post_with_group_show_in_group_page(self):
        """
        Проверка на то, что пост с группой появляется на cтранице группы.
        """
        response = self.authorized_client.get(reverse(
            'group_posts', kwargs={'slug': 'test-slug'})
        )
        two = response.context.get('page').object_list[0]
        self.assertEqual(two, PostPagesTests.post2)

    def test_index_cached(self):
        """
        Проверка работы кэша на главной странице.
        """
        response_start = self.guest_client.get(reverse('index'))
        response_test_cache = self.guest_client.get(reverse('index'))
        cache.clear()
        response_three = self.guest_client.get(reverse('index'))
        self.assertEqual(response_start.content, response_test_cache.content)
        self.assertNotEqual(response_start.content, response_three.content)

    def test_authorized_client_can_subscribe(self):
        """
        Проверка, что авторизованный пользователь
        может подписываться на других.
        """
        # Подписываем авторизованного клиента на автора
        self.authorized_client2.get(reverse(
            'profile_follow', kwargs={'username': PostPagesTests.user}
        ))
        follow = Follow.objects.all()[0]
        # Проверем, что появился 1 подписчик и
        # соответствие автора и подписчика
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.author, PostPagesTests.user)
        self.assertEqual(follow.user, PostPagesTests.second)

    def test_authorized_client_can_unsubscribe(self):
        """
        Проверка, что авторизованный пользователь
        может удалять автора из подписок.
        """
        # Подписываем авторизованного клиента на автора
        self.authorized_client2.get(reverse(
            'profile_follow', kwargs={'username': PostPagesTests.user}
        ))
        # Проверяем кол-во подписчиков после подписки
        after_subscribe = Follow.objects.count()
        # Отписываем авторизованного клиента от автора
        self.authorized_client2.get(reverse(
            'profile_unfollow', kwargs={'username': PostPagesTests.user}
        ))
        # Проверяем кол-во подписчиков после отписки
        after_unsubscribe = Follow.objects.count()
        # Сравниваем кол-во подписчиков до и после
        self.assertEqual(after_subscribe, after_unsubscribe + 1)

    def test_new_post_in_follow_page_for_follower(self):
        """
        Проверка, что новый пост отображается в ленте избранных авторов,
        если пользователь подписан на него.
        """
        # Делаем подписку
        Follow.objects.create(
            user=PostPagesTests.second,
            author=PostPagesTests.user
        )
        # Создаем новый пост
        Post.objects.create(author=PostPagesTests.user, text='test_text')
        response = self.authorized_client2.get(reverse('follow_index'))
        posts_count = len(response.context.get('page'))
        self.assertEqual(posts_count, 3)

    def test_new_post_in_follow_page_for_unfollower(self):
        """
        Проверка, что новый пост не отображается в ленте избранных авторов,
        если пользователь не подписан на него.
        """
        # Создаем новый пост
        Post.objects.create(author=PostPagesTests.user, text='test_text')
        response = self.authorized_client2.get(reverse('follow_index'))
        posts_count = len(response.context.get('page'))
        self.assertEqual(posts_count, 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            description='test_description',
            slug='test_slug',
        )
        for cls.post in range(13):
            cls.post = Post.objects.create(
                text='Тестовый текст',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_ten_records(self):
        """
        Проверка паджинатора главная страница(1 страница).
        """
        pages = {
            reverse('index'): 'index',
            reverse('profile', kwargs={'username': 'test_user'}): 'profile',
            reverse('group_posts', kwargs={'slug': 'test_slug'}): 'group_posts'
        }
        for key in pages.keys():
            response = self.client.get(key)
            self.assertEqual(
                len(response.context.get('page').object_list), 10
            )

    def test_second_page_contains_three_records(self):
        """
        Проверка паджинатора главная страница(2 страница).
        """
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
