from collections import namedtuple

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTE_TITLE = 'Название заметки'
NOTE_TEXT = 'Текст заметки'
NOTE_SLUG = 'Chekhov'

NEW_NOTE_TITLE = 'Новое название заметки'
NEW_NOTE_TEXT = 'Новый текст заметки'
NEW_NOTE_SLUG = 'Sholokhov'


form_data = {'title': NOTE_TITLE,
             'text': NOTE_TEXT,
             'slug': NOTE_SLUG}

url_name = namedtuple(
    'name',
    ['home', 'add', 'edit', 'detail', 'delete',
     'list', 'success', 'login', 'logout', 'signup'])

url = url_name(
    reverse('notes:home'),
    reverse('notes:add'),
    reverse('notes:edit', args=(NOTE_SLUG,)),
    reverse('notes:detail', args=(NOTE_SLUG,)),
    reverse('notes:delete', args=(NOTE_SLUG,)),
    reverse('notes:list'),
    reverse('notes:success'),
    reverse('users:login'),
    reverse('users:logout'),
    reverse('users:signup'),
)


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Антон Чехов')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author)


class BaseTestListPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        all_notes = [
            Note(title=f'Заголовок {index}',
                 text='Просто текст.',
                 slug=f'Tolstoy_{index}',
                 author=cls.author)
            for index in range(5)
        ]
        Note.objects.bulk_create(all_notes)
