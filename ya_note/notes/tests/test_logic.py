from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .common import (BaseTestCase, form_data,
                     NOTE_TITLE, NOTE_TEXT, NOTE_SLUG,
                     NEW_NOTE_TITLE, NEW_NOTE_TEXT,
                     NEW_NOTE_SLUG, url)


class TestNoteCreation(BaseTestCase):
    def test_user_can_create_note(self):
        """Проверить возможность создания заметки автором."""
        self.note.delete()
        init_notes_count = Note.objects.count()
        response = self.author_client.post(url.add, data=form_data)
        self.assertRedirects(response, url.success)
        self.assertEqual(Note.objects.count(), init_notes_count + 1)
        note = Note.objects.get()
        self.assertEqual(note.title, form_data['title'])
        self.assertEqual(note.text, form_data['text'])
        self.assertEqual(note.slug, form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Проверить невозможность создания заметки анонимом."""
        self.note.delete()
        init_notes_count = Note.objects.count()
        response = self.client.post(url.add, data=form_data)
        self.assertRedirects(response, f'{url.login}?next={url.add}')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, init_notes_count)

    def test_not_unique_slug(self):
        """Проверить уникальность слага."""
        init_notes_count = Note.objects.count()
        response = self.author_client.post(url.add, data=form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=NOTE_SLUG + WARNING
        )
        self.assertEqual(Note.objects.count(), init_notes_count)

    def test_empty_slug(self):
        """Проверить случай пустого поля слаг."""
        self.note.delete()
        init_notes_count = Note.objects.count()
        form_data = {'title': NOTE_TITLE,
                     'text': NOTE_TEXT}
        response = self.author_client.post(url.add, data=form_data)
        self.assertRedirects(response, url.success)
        self.assertEqual(Note.objects.count(), init_notes_count + 1)
        note = Note.objects.get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(BaseTestCase):
    def test_author_can_delete_note(self):
        """Проверить возможность удаления заметки автором."""
        init_notes_count = Note.objects.count()
        response = self.author_client.delete(url.delete)
        self.assertRedirects(response, url.success)
        self.assertEqual(Note.objects.count(), init_notes_count - 1)

    def test_user_cant_delete_comment_of_another_user(self):
        """Проверить невозможность удаления заметки не автором."""
        init_notes_count = Note.objects.count()
        response = self.reader_client.delete(url.delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), init_notes_count)

    def test_author_can_edit_comment(self):
        """Проверить возможность редактирования заметки автором."""
        form_data['title'] = NEW_NOTE_TITLE
        form_data['text'] = NEW_NOTE_TEXT
        form_data['slug'] = NEW_NOTE_SLUG
        response = self.author_client.post(url.edit, data=form_data)
        self.assertRedirects(response, url.success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, NEW_NOTE_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверить невозможность редактирования заметки не автором."""
        response = self.reader_client.post(url.edit, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NOTE_TITLE)
        self.assertEqual(self.note.text, NOTE_TEXT)
        self.assertEqual(self.note.slug, NOTE_SLUG)
