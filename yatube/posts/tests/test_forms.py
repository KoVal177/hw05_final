import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
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
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост4567890',
            author=cls.user,
            group=cls.group,
        )
        cls.comment_data = {
            'text': 'Новый комментарий',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """ Создаем клиентов согласно авторизации и авторства поста"""
        self.guest_client = Client()
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.user)

    def test_create_post(self):
        """ Проверяем создание нового поста с картинкой через форму"""
        num_posts = Post.objects.count()
        form_data = {
            'text': 'Текст нового поста',
            'group': 1,
            'image': self.uploaded,
        }
        self.authorized_author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), num_posts + 1)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            image='posts/small.gif',
        ).exists())

    def test_edit_post(self):
        """ Проверяем редактирование существующего поста через форму"""
        num_posts = Post.objects.count()
        post_to_edit = Post.objects.first()
        text_before = post_to_edit.text
        form_data = {
            'text': 'Исправленный текст старого поста',
            'group': 1,
        }
        self.authorized_author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_to_edit.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), num_posts)
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())
        self.assertFalse(Post.objects.filter(text=text_before).exists())

    def test_add_comment_guest(self):
        """
        Проверяем невозможность добавления комментария к посту
        анонимным пользователем
        """
        post_to_comment = Post.objects.first()
        init_num_comments = len(Comment.objects.filter(post=post_to_comment)
                                .all())
        self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': post_to_comment.id}),
            data=self.comment_data,
            follow=True,
        )
        final_num_comments = len(Comment.objects.filter(post=post_to_comment)
                                 .all())
        self.assertTrue(init_num_comments == final_num_comments)

    def test_add_comment_authorized(self):
        """
        Проверяем возможность добавления комментария к посту
        авторизованным пользователем
        """
        post_to_comment = Post.objects.first()
        init_num_comments = len(Comment.objects.filter(post=post_to_comment)
                                .all())
        self.authorized_author_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': post_to_comment.id}),
            data=self.comment_data,
            follow=True,
        )
        final_num_comments = len(Comment.objects.filter(post=post_to_comment)
                                 .all())
        self.assertTrue(init_num_comments < final_num_comments)
