from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
# from unittest import skip
from django.urls import reverse
from notes.models import Note


User = get_user_model()


# @skip('Проверено')
class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём автора:
        cls.author = User.objects.create(username='Лев Толстой')
        # Создаём читателя:
        cls.reader = User.objects.create(username='Другой пользователь')

        # Создаём заметку:
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author)

    def test_pages_availability_for_anonymous_user(self):
        """Страницы доступны незарегистрированному пользователю"""
        names = ('notes:home', 'users:login', 'users:logout', 'users:signup')
        for name in names:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Страницы доступны зарегистрированному пользователю"""
        names = ('notes:home', 'users:login', 'users:logout', 'users:signup')
        # Логиним пользователя в клиенте:
        self.client.force_login(self.author)

        for name in names:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        """Страницы доступны зарегистрированному пользователю"""
        names = ('notes:detail', 'notes:edit', 'notes:delete')
        args = (self.note.slug,)
        # Логиним автора в клиенте:
        self.client.force_login(self.author)
        for name in names:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        names = ('notes:detail', 'notes:edit', 'notes:delete')
        users = (self.author, self.reader)
        args = (self.note.slug,)
        for user in users:
            for name in names:
                with self.subTest(user=user, name=name, args=args):
                    # Логиним пользователя в клиенте:
                    self.client.force_login(user)
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    if user == self.author:
                        self.assertEqual(response.status_code, HTTPStatus.OK)
                    else:
                        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """Страницы не доступны незарегистрированному пользователю"""
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        urls = (
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                # Получаем адрес страницы:
                url = reverse(name, args=args)
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next,
                # в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
