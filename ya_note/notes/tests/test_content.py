from notes.forms import NoteForm
from .common import BaseTestCase, BaseTestListPage, url


class TestNoteList(BaseTestCase):
    def test_notes_list_for_different_users(self):
        """Проверить доступ к списку заметок."""
        client_statuses = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, note_in_list in client_statuses:
            with self.subTest(client=client):
                response = client.get(url.list)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_authorized_client_has_form(self):
        """Проверить наличие формы у автора заметки."""
        for name in (url.add, url.edit):
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)


class TestListPage(BaseTestListPage):
    def test_notes_order(self):
        """Проверить сортировку заметок."""
        response = self.author_client.get(url.list)
        object_list = response.context['object_list']
        all_id = [note.id for note in object_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)
