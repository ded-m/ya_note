from http import HTTPStatus
# from unittest import skip
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    # Заметка
    TITLE = 'Тестовая заметка'
    TEXT = 'Текст заметки'
    SLUG = 'note_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.url = reverse('notes:add')
        # Данные для POST-запроса при создании заметки.
        cls.form_data = {'text': cls.TEXT,
                         'title': cls.TITLE,
                         'author': cls.author,
                         'slug': cls.SLUG
                         }

    # @skip('проверено')
    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с данными заметки.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Ожидаем, что заметок в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    # @skip('проверено')
    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        # Совершаем запрос через авторизованный клиент.
        response = self.client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл на страницу с именем SUCCESS.
        self.assertRedirects(response, reverse('notes:success'))
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть одна заметка.
        self.assertEqual(notes_count, 1)
        # Получаем объект заметки из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты заметки совпадают с ожидаемыми.
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.author)

    # @skip('проверено')
    def test_user_repeats_slug(self):
        self.client.force_login(self.author)
        # Создаём 2 одинаковых заметки с одинаковым SLUG`.
        self.client.post(self.url, data=self.form_data)
        response = self.client.post(self.url, data=self.form_data)
        # Проверяем, есть ли в ответе ошибка формы.
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG+WARNING
        )
        # Дополнительно убедимся, что вторая заметка не была создана.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


# @skip('готово')
class TestNoteEitDelete(TestCase):
    TITLE = 'Тестовая заметка'
    TEXT = 'Текст заметки.'
    SLUG = 'note_slug'
    TITLE_UPDATED = 'Тестовая заметка upd'
    TEXT_UPDATED = 'Текст заметки. upd'
    SLUG_UPDATED = 'note_slug_upd'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.user = User.objects.create(username='Михаил Лермонтов')
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
            slug=cls.SLUG
        )
        cls.delete_url = reverse('notes:delete', args=(cls.SLUG,))
        cls.edit_url = reverse('notes:edit', args=(cls.SLUG,))
        cls.success = reverse('notes:success')
        # Информация для обновления заметки
        cls.form_data = {'text': cls.TEXT_UPDATED,
                         'title': cls.TITLE_UPDATED,
                         'author': cls.author,
                         'slug': cls.SLUG_UPDATED
                         }

    # @skip('проверено')
    def test_author_can_delete_comment(self):
        self.client.force_login(self.author)
        # От имени автора заметки отправляем DELETE-запрос на удаление.
        response = self.client.delete(self.delete_url)
        # Проверяем, что редирект привёл к странице с именем SUCCESS.
        self.assertRedirects(response, self.success)
        # Считаем количество заметок в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль заметок в системе.
        self.assertEqual(notes_count, 0)

    # @skip('проверено')
    def test_user_cant_delete_comment_of_another_user(self):
        self.client.force_login(self.user)
        # Выполняем запрос на удаление от другого пользователя.
        response = self.client.delete(self.delete_url)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что заметка по-прежнему на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    # @skip('проверено')
    def test_author_can_edit_comment(self):
        self.client.force_login(self.author)
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.success)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertEqual(self.note.title, self.TITLE_UPDATED)
        self.assertEqual(self.note.text, self.TEXT_UPDATED)

    # @skip('проверено')
    def test_user_cant_edit_comment_of_another_user(self):
        self.client.force_login(self.user)
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.client.post(self.edit_url, data=self.form_data)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.text, self.TEXT)
