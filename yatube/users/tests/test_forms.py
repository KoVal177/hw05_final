from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        """ Создаем клиентов согласно авторизации и авторства поста"""
        self.guest_client = Client()

    def test_signup_user(self):
        """ Проверяем создание нового user через форму"""
        num_users = User.objects.count()
        form_data = {
            'first_name': 'Третьяков',
            'last_name': 'Иван',
            'username': 'tretyak',
            'email': 'tretyak@gorod.com',
            'password1': 'Kakodf53$',
            'password2': 'Kakodf53$',
        }
        self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(User.objects.count(), num_users + 1)
        self.assertTrue(User.objects.filter(
            username=form_data['username'],
            first_name=form_data['first_name'],
            last_name=form_data['last_name'],
            email=form_data['email'],
        ).exists())
