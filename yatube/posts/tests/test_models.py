from django.conf import settings
from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group_title = 'Тестовая группа'
        cls.post_text = 'Тестовый пост4567890'
        cls.group = Group.objects.create(
            title=cls.group_title,
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.post_text,
        )

    def test_group_correct_str(self):
        """Проверяем, что у моделей корректно работает __str__"""
        models_values = [
            (self.group, self.group_title),
            (self.post, self.post_text[:settings.POST_STRINGER_LENGTH]),
        ]
        for model, expected_value in models_values:
            with self.subTest():
                self.assertEqual(str(model), expected_value)

    def test_fields_verbose_names(self):
        """Проверяем verbose_name в полях"""
        fields_verbose_names = [
            ('text', 'Текст поста'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор'),
            ('group', 'Группа'),
        ]
        for field, verbose_name in fields_verbose_names:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    verbose_name
                )

    def test_fields_help_texts(self):
        """Проверяем help_text в полях"""
        fields_help_texts = [
            ('text', 'Введите текст поста'),
            ('group', 'Выберите группу'),
        ]
        for field, help_text in fields_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    help_text
                )
