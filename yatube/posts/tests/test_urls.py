from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User
from .data_tests import urls_names_templates_to_check


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='someone')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост4567890',
        )

    def setUp(self):
        """ Создаем клиентов согласно авторизации и авторства поста"""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_author_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author_client.force_login(self.user_author)
        cache.clear()

    def test_urls_404(self):
        """Проверяем код ответа при запросе несуществующей страницы"""
        response = self.guest_client.get('/unexisting-page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_status_codes_guest(self):
        """Проверяем код ответа на запрос анонимного пользователя"""
        for item in urls_names_templates_to_check:
            url = item['url']
            access = item['access']
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if access in ('all',):
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif access in ('authorized', 'author',):
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_status_codes_athorized(self):
        """Проверяем код ответа на запрос авторизованного пользователя"""
        for item in urls_names_templates_to_check:
            url = item['url']
            access = item['access']
            with self.subTest(url=url):
                if access in ('authorized',):
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif access in ('author',):
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_status_codes_author(self):
        """Проверяем код ответа на запрос автора"""
        for item in urls_names_templates_to_check:
            url = item['url']
            access = item['access']
            with self.subTest(url=url):
                if access in ('author',):
                    response = self.authorized_author_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_status_templates_guest(self):
        """Проверяем template на запрос анонимного пользователя"""
        for item in urls_names_templates_to_check:
            url = item['url']
            template = item['template']
            access = item['access']
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if access in ('all',):
                    self.assertTemplateUsed(response, template)
                elif access in ('authorized', 'author'):
                    self.assertTemplateNotUsed(response, template)

    def test_urls_templates_athorized(self):
        """Проверяем template на запрос авторизованного пользователя"""
        for item in urls_names_templates_to_check:
            url = item['url']
            template = item['template']
            access = item['access']
            with self.subTest(url=url):
                if access in ('authorized',):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, template)
                elif access in ('author',):
                    response = self.authorized_client.get(url)
                    self.assertTemplateNotUsed(response, template)

    def test_urls_templates_author(self):
        """Проверяем template на запрос автора"""
        for item in urls_names_templates_to_check:
            url = item['url']
            template = item['template']
            access = item['access']
            with self.subTest(url=url):
                if access in ('author',):
                    response = self.authorized_author_client.get(url)
                    self.assertTemplateUsed(response, template)
