# nontes/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    # Текст заметки понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'Mikhalkov'

    @classmethod
    def setUpTestData(cls):
        # Адрес страницы для создания заметки.
        cls.url = reverse('notes:add', args=None)
        cls.done_url = reverse('notes:success', args=None)
        cls.list_url = reverse('notes:list', args=None)
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='Сергей Михалков')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Данные для POST-запроса при создании заметки.
        cls.form_data = {'title': cls.NOTE_TITLE,
                         'text': cls.NOTE_TEXT,
                         'slug': cls.NOTE_SLUG}

    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с названием заметки.
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        url = reverse('notes:add')
        expected_url = f'{login_url}?next={url}'
        # Проверяем, что произошла переадресация на страницу логина:
        self.assertRedirects(response, expected_url)
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Ожидаем, что заметок в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что выполняется редирект на страницу "Успешно".
        self.assertRedirects(response, self.done_url)
        # Считаем количество заметок.
        response = self.auth_client.get(self.list_url)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        # Убеждаемся, что есть одна заметка.
        self.assertEqual(notes_count, 1)
        # Получаем объект заметки из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты заметки совпадают с ожидаемыми.
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_not_unique_slug(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=self.NOTE_SLUG,
            author=self.user)
        # Отправляем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, есть ли в ответе ошибка формы.
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING
        )
        # Дополнительно убедимся, что новая заметка не была создана.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        # Убираем поле slug из словаря:
        self.form_data.pop('slug')
        response = self.auth_client.post(url, data=self.form_data)
        # Проверяем, что даже без slug заметка была создана:
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get()
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.form_data['title'])
        # Проверяем, что slug заметки соответствует ожидаемому:
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Название заметки_1'
    NOTE_TEXT = 'Текст заметки_1'
    NOTE_SLUG = 'Pushkin_1'

    NEW_NOTE_TITLE = 'Название заметки_2'
    NEW_NOTE_TEXT = 'Текст заметки_2'
    NEW_NOTE_SLUG = 'Pushkin_2'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Александр Пушкин')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.user)

        cls.notes_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.done_url = reverse('notes:success', args=None)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # URL для редактирования заметки.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления заметки.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Формируем данные для POST-запроса по обновлению заметки.
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG}

    def test_author_can_delete_note(self):
        # От имени автора заметки отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к странице "Успешно".
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, self.done_url)
        # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 0)

    def test_note_existence(self):
        notes_count = Note.objects.count()
        # В начале теста в БД всегда есть 1 заметка, созданная в setUpTestData.
        self.assertEqual(notes_count, 1)

    def test_user_cant_delete_comment_of_another_user(self):
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.delete_url)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что заметка по-прежнему на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_comment(self):
        # Выполняем запрос на редактирование от имени автора заметки.
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.done_url)
        # Обновляем объект заметки.
        self.note.refresh_from_db()
        # Проверяем, что аттрибуты заметки соответствует обновленному.
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        # Выполняем запрос на редактирование заметки от имени другого
        # пользователя.
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект заметки.
        self.note.refresh_from_db()
        # Проверяем, что аттрибуты заметки остались теми же, что и были.
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
