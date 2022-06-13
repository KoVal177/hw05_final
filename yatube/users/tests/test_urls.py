from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='someone')
        cls.urls_templates_to_check = [
            ('/auth/login/', 'users/login.html', 'all'),
            ('/auth/logout/', 'users/logged_out.html', 'all'),
            ('/auth/signup/', 'users/signup.html', 'all'),
            ('/auth/password_change_done/', 'users/password_change_done.html',
             'authorized'),
            ('/auth/password_change/', 'users/password_change_form.html',
             'authorized'),
            ('/auth/reset/done/', 'users/password_reset_complete.html', 'all'),
            ('/auth/reset/Mw/60f-07b7c07e4196aff4af9c/',
             'users/password_reset_confirm.html', 'all'),
            ('/auth/password_reset/done/', 'users/password_reset_done.html',
             'all'),
            ('/auth/password_reset/', 'users/password_reset_form.html', 'all'),
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_codes_guest(self):
        """Проверяем код ответа для анонимного пользователя"""
        for url, _, access in self.urls_templates_to_check:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if access in ('all',):
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif access in ('authorized',):
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_codes_authorized(self):
        """Проверяем код ответа для авторизованного пользователя"""
        for url, _, access in self.urls_templates_to_check:
            with self.subTest(url=url):
                if access in ('authorized',):
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_templates_guest(self):
        """Проверяем template для анонимного пользователя"""
        for url, template, access in self.urls_templates_to_check:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if access in ('all',):
                    self.assertTemplateUsed(response, template)
                elif access in ('authorized',):
                    self.assertTemplateNotUsed(response, template)

    def test_urls_templates_authorized(self):
        """Проверяем template для авторизованного пользователя"""
        for url, template, access in self.urls_templates_to_check:
            with self.subTest(url=url):
                if access in ('authorized',):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, template)
