from django.test import TestCase
# from unittest import skip
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


# @skip('Проверено')
class TestNotesPage(TestCase):
    # Вынесем ссылку на страницу заметок
    # и количество заметок в атрибуты класса.
    NOTES_URL = reverse('notes:list')
    NOTES_COUNT = 11

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
            for index in range(cls.NOTES_COUNT)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        # Логиним пользователя в клиенте:
        self.client.force_login(self.author)
        # Загружаем страницу с заметками.
        response = self.client.get(self.NOTES_URL)
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем длину списка.
        notes_count = len(object_list)
        # Проверяем, что на странице именно 11 новостей.
        self.assertEqual(notes_count, self.NOTES_COUNT)


# @skip('Проверено')
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
        # Сохраняем в переменную адрес страницы с заметкой:
        # cls.detail_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_authorized_client_has_form(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            # ('notes:delete', (self.note.slug,)),
            ('notes:add', None)
        )
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
