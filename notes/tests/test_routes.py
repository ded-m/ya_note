# news/tests/test_routes.py
# Импортируем класс HTTPStatus.
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
# from unittest import skip
# Импортируем функцию reverse().
from django.urls import reverse
# Импортируем класс модели заметок.
from notes.models import Note


User = get_user_model()


# @skip('Проверено')
class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя:
        cls.author = User.objects.create(username='Лев Толстой')
        
        # Создаём заметку:
        cls.note = Note.objects.create(title='Заголовок', text='Текст', author=cls.author)


    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),

        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_redirect_for_anonymous_client(self):
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
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
