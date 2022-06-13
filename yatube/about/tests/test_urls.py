from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.urls_templates_to_check = [
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html'),
        ]

    def test_urls_codes(self):
        """Проверяем код ответа на запрос по заданному пути"""
        for url, _ in self.urls_templates_to_check:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_templates(self):
        """Проверяем подгрузку шаблона по заданному пути"""
        for url, template in self.urls_templates_to_check:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
