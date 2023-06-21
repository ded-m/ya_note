from django.conf import settings
from django.test import TestCase

from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestNotesPage(TestCase):
    # Вынесем ссылку на домашнюю страницу в атрибуты класса.
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        # Вычисляем текущую дату.
        today = datetime.today()
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text=f'Текст заметки {index}.',
                # Для каждой заметки изменяем slug на index дней от today,
                # где index - счётчик цикла.
                slug='notes' + str(today - timedelta(days=index)),
                author=cls.author
            )
            for index in range(11)
        ]
        Note.objects.bulk_create(all_notes) 

    def test_notes_count(self):
        # Загружаем страницу с заметками.
        response = self.client.get(self.NOTES_URL)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем длину списка.
        notes_count = len(object_list)
        # Проверяем, что на странице именно 10 новостей.
        self.assertEqual(notes_count, 10)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.notes = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки.',
            author=cls.author,
            slug='note_slug'
        )
        # Сохраняем в переменную адрес страницы с новостью:
        cls.detail_url = reverse('notes:detail', args=(cls.notes.slug,))

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
