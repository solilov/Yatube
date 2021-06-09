from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()


class AboutURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.create(username='test_user')
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_static_pages_available_everyone(self):
        """Статичные страницы достпуны любому пользователю."""
        pages = {
            '/about/author/': 'author',
            '/about/tech/': 'tech'
        }
        for key in pages.keys():
            with self.subTest(key=key):
                response = self.guest_client.get(key)
                self.assertEqual(response.status_code, 200)

    def test_static_pages_uses_correct_template(self):
        """Cтатичные страницы используют соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'author.html',
            '/about/tech/': 'tech.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
