from django.test import TestCase
from unittest import skip
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


@skip('Пропущено')
class TestNotesPage(TestCase):
    # Вынесем ссылку на страницу заметок в атрибуты класса.
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        # Вычисляем текущую дату.
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text=f'Текст заметки {index}.',
                # Для каждой заметки изменяем slug,
                # где index - счётчик цикла.
                slug=f'notes_{index}',
                author=cls.author
            )
            for index in range(11)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        # Загружаем страницу с заметками.
        response = self.client.get(self.NOTES_URL)
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем длину списка.
        notes_count = len(object_list)
        # Проверяем, что на странице именно 10 новостей.
        self.assertEqual(notes_count, 10)

@skip('Пропущено')
class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки.',
            author=cls.author,
            slug='note_slug'
        )
        # Сохраняем в переменную адрес страницы с новостью:
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
