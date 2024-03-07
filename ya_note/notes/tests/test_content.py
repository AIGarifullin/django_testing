from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteList(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Антон Чехов')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Chekhov',
            author=cls.author)

    def test_notes_list_for_different_users(self):
        client_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in client_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            name = 'notes:list'
            url = reverse(name)
            with self.subTest(user=user, name=name):
                response = self.client.get(url)
                object_list = response.context['object_list']
                # Проверяем истинность утверждения "заметка есть в списке":
                self.assertEqual((self.note in object_list), note_in_list)


class TestListPage(TestCase):
    LIST_URL = reverse('notes:list', args=None)

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        all_notes = [
            Note(title=f'Заголовок {index}',
                 text='Просто текст.',
                 slug=f'Tolstoy_{index}',
                 author=cls.author)
            for index in range(5)  # Создаем пять заметок
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_id = [note.id for note in object_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)


class TestAddEditPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Антон Чехов')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Chekhov',
            author=cls.author)

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)))
        for name, args in urls:
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                # Проверим, что объект формы соответствует классу формы.
                self.assertIsInstance(response.context['form'], NoteForm)
