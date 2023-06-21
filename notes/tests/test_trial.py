from django.test import TestCase
from unittest import skip
# Импортируем модель, чтобы работать с ней в тестах.
from notes.models import Note


# Создаём тестовый класс с произвольным названием, наследуем его от TestCase.
@skip('Пример теста')
class TestNotes(TestCase):

    # В методе класса setUpTestData создаём тестовые объекты.
    # Оборачиваем метод соответствующим декоратором.    
    @classmethod
    def setUpTestData(cls):
        # Стандартным методом Django ORM create() создаём объект класса.
        # Присваиваем объект атрибуту класса: назовём его news.
        cls.notes = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
        )

    # Проверим, что объект действительно было создан.
    def test_successful_creation(self):
        # При помощи обычного ORM-метода посчитаем количество записей в базе.
        news_count = Note.objects.count()
        # Сравним полученное число с единицей.
        self.assertEqual(news_count, 1)

    def test_title(self):
        # Сравним свойство объекта и ожидаемое значение.
        self.assertEqual(self.news.title, 'Заголовок заметки')
