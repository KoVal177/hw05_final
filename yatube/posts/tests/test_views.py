import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User
from .data_tests import urls_names_templates_to_check

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user_author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='someone')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост4567890',
            author=cls.user_author,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.another_user = User.objects.create_user(username='anotherAuthor')
        cls.another_group = Group.objects.create(
            title='Еще одна группа',
            slug='another-slug',
            description='Еще одно описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """ Создаем клиентов согласно авторизации и авторства поста"""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_author_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author_client.force_login(self.user_author)
        cache.clear()

    def test_names_templates_guest(self):
        """
        Проверяем соответствие names и templates для анонимного пользователя
        """
        check_client = self.guest_client
        for item in urls_names_templates_to_check:
            name = reverse(item['name'], kwargs=item['reverse_kwargs'])
            template = item['template']
            access = item['access']
            with self.subTest(name=name):
                if access in ('all',):
                    response = check_client.get(name)
                    self.assertTemplateUsed(response, template)
                elif access in ('authorized', 'author',):
                    response = check_client.get(name)
                    self.assertTemplateNotUsed(response, template)

    def test_names_templates_athorized(self):
        """
        Проверяем соответствие names и templates для авторизованного
        пользователя
        """
        check_client = self.authorized_client
        for item in urls_names_templates_to_check:
            name = reverse(item['name'], kwargs=item['reverse_kwargs'])
            template = item['template']
            access = item['access']
            with self.subTest(name=name):
                if access in ('authorized',):
                    response = check_client.get(name)
                    self.assertTemplateUsed(response, template)
                elif access in ('author',):
                    response = check_client.get(name)
                    self.assertTemplateNotUsed(response, template)

    def test_names_templates_author(self):
        """
        Проверяем соответствие names и templates для авторизованного
        пользователя - автора
        """
        check_client = self.authorized_author_client
        for item in urls_names_templates_to_check:
            name = reverse(item['name'], kwargs=item['reverse_kwargs'])
            template = item['template']
            access = item['access']
            with self.subTest(name=name):
                if access in ('author',):
                    response = check_client.get(name)
                    self.assertTemplateUsed(response, template)

    def test_templates_lists_contexts(self):
        """
        Проверяем правильность передачи context в templates со списками постов
        """
        for item in urls_names_templates_to_check:
            if item['name'] in ('posts:index',
                                'posts:group_list',
                                'posts:profile',
                                ):
                name = reverse(item['name'], kwargs=item['reverse_kwargs'])
                with self.subTest(name=name):
                    response = self.guest_client.get(name)
                    context = response.context['page_obj'].object_list[0]
                    self.assertEqual(context.text, self.post.text)
                    self.assertEqual(context.author.username,
                                     self.user_author.username)
                    self.assertEqual(context.group.title, self.group.title)
                    self.assertNotEqual(context.image.name, '')

    def test_templates_post_detail_contexts(self):
        """
        Проверяем правильность передачи context в templates деталей поста
        """
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        response = self.guest_client.get(url)
        context = response.context['post']
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.author.username, self.user_author.username)
        self.assertEqual(context.group.title, self.group.title)
        self.assertNotEqual(context.image.name, '')

    def test_templates_post_edit_contexts(self):
        """
        Проверяем правильность передачи context в templates редактирования
        существующего поста
        """
        for item in urls_names_templates_to_check:
            if item['name'] in ('posts:post_edit',):
                name = reverse(item['name'], kwargs=item['reverse_kwargs'])
                with self.subTest(name=name):
                    response = self.authorized_author_client.get(name)
                    context = response.context['form']
                    self.assertEqual(context['text'].value(), self.post.text)
                    self.assertEqual(context['group'].value(), 1)

    def test_templates_post_create_contexts(self):
        """
        Проверяем правильность передачи context в templates создания нового
        поста
        """
        for item in urls_names_templates_to_check:
            if item['name'] in ('posts:post_create',):
                name = reverse(item['name'], kwargs=item['reverse_kwargs'])
                with self.subTest(name=name):
                    response = self.authorized_client.get(name)
                    context = response.context['form']
                    self.assertEqual(context['text'].value(), None)
                    self.assertEqual(context['group'].value(), None)

    def test_another_post_added(self):
        """
        Проверяем корректность появления нового поста на index, group,
        profile страницах
        """
        self.another_post = Post.objects.create(
            text='Еще один пост номер 123456789',
            author=self.another_user,
            group=self.another_group,
        )
        pages_to_check = {
            'posts:index': {},
            'posts:group_list': {'slug': self.another_group.slug},
            'posts:profile': {'username': self.another_user.username},
        }
        for name, kwarg in pages_to_check.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name, kwargs=kwarg))
                context = response.context['page_obj'].object_list[0]
                self.assertEqual(context.text, self.another_post.text)
                self.assertEqual(context.author.username,
                                 self.another_user.username)
                self.assertEqual(context.group.title, self.another_group.title)

    def test_another_post_not_old_group(self):
        """Проверяем, что новый пост не попадает в посты другой группы"""
        self.another_post = Post.objects.create(
            text='Еще один пост номер 123456789',
            author=self.another_user,
            group=self.another_group,
        )
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        old_group_post_id = response.context['page_obj'].object_list[0].id
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.another_group.slug})
        )
        another_group_post_id = response.context['page_obj'].object_list[0].id
        self.assertNotEqual(old_group_post_id, another_group_post_id)

    def test_comment_appears(self):
        """Проверяем появление комментария к посту на странице поста"""
        post = Post.objects.first()
        comment = Comment.objects.create(
            text='Новый комментарий',
            post=post,
            author=self.user_author,
        )
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': post.id})
        )
        comment_response = response.context['comments'].first()
        self.assertEqual(comment_response.text, comment.text)
        self.assertEqual(comment_response.author, comment.author)

    def test_cache(self):
        """ Проверяем работу кэша на index при редактировании поста"""
        url = '/'
        response = self.authorized_author_client.get(url)
        initial_page = response.content
        post_to_edit = Post.objects.first()
        form_data = {
            'text': 'Исправленный текст старого поста',
            'group': 1,
        }
        self.authorized_author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_to_edit.id}),
            data=form_data,
        )
        with self.subTest(url=url):
            response = self.authorized_author_client.get(url)
            new_page = response.content
            self.assertEqual(initial_page, new_page)
            cache.clear()
            response = self.authorized_author_client.get(url)
            new_page = response.content
            self.assertNotEqual(initial_page, new_page)

    def test_add_subscription(self):
        """Проверяем добавление подписки на автора"""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_author.username})
        )
        self.assertIsNotNone(Follow.objects.first())

    def test_delete_subscription(self):
        """Проверяем удаление подписки на автора"""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_author.username})
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_author.username})
        )
        self.assertIsNone(Follow.objects.first())

    def test_subscription_following(self):
        """
        Проверяем появление подписки в ленте подписавшегося
        и ее отсутствие у других
        """
        not_subscribed_user_client = Client()
        not_subscribed_user_client.force_login(self.another_user)
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_author.username})
        )
        response = self.authorized_client.get(reverse(
            'posts:follow_index')
        )
        context = response.context['page_obj'].object_list
        self.assertTrue(len(context) > 0)
        response = not_subscribed_user_client.get(reverse(
            'posts:follow_index')
        )
        context = response.context['page_obj'].object_list
        self.assertTrue(len(context) == 0)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_name = 'paginator_user'
        cls.slug = 'page-slug'
        cls.user = User.objects.create_user(username=cls.user_name)
        cls.group = Group.objects.create(
            title='Группа для паджинатора',
            slug=cls.slug,
            description='Описание группы для паджинатора',
        )
        cls.NUM_POSTS_2_PAGE = 1
        posts = [
            Post(
                author=cls.user,
                text=f'Пост для паджинатора номер очередной {i}',
                group=cls.group,
            ) for i in range(settings.POSTS_PER_PAGE + cls.NUM_POSTS_2_PAGE)
        ]
        Post.objects.bulk_create(posts)
        cls.pages_to_check = {
            'posts:index': {},
            'posts:group_list': {'slug': cls.slug},
            'posts:profile': {'username': cls.user_name},
        }

    def setUp(self):
        """ Создаем клиентов согласно авторизации и авторства поста"""
        self.guest_client = Client()

    def test_paginator_page_1(self):
        """Проверяем паджинатор на 1-й странице"""
        for name, kwarg in self.pages_to_check.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name, kwargs=kwarg))
                context = response.context['page_obj'].object_list
                self.assertEqual(len(context), settings.POSTS_PER_PAGE)

    def test_paginator_page_2(self):
        """Проверяем паджинатор на 2-й странице"""
        for name, kwarg in self.pages_to_check.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name, kwargs=kwarg),
                                                 {'page': 2})
                context = response.context['page_obj'].object_list
                self.assertEqual(len(context), self.NUM_POSTS_2_PAGE)
