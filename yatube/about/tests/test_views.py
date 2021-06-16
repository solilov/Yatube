from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        pages = {
            reverse('about:author'): 'author',
            reverse('about:tech'): 'tech'
        }
        for key in pages.keys():
            response = self.guest_client.get(key)
            self.assertEqual(response.status_code, 200)

    def test_pages_uses_correct_template(self):
        pages = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for key, values in pages.items():
            with self.subTest(values=values):
                response = self.guest_client.get(key)
                self.assertTemplateUsed(response, values)
