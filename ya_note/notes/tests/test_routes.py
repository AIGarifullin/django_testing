from http import HTTPStatus

from .common import BaseTestCase, URLS


class TestRoutes(BaseTestCase):
    def test_home_availability_for_anonymous_user(self):
        """Проверить доступ страниц для всех пользователей."""
        urls = (URLS.home, URLS.login, URLS.logout, URLS.signup)
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Проверить доступ страниц для автора заметки."""
        urls = (URLS.list, URLS.add, URLS.success)
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Проверить возможность изменения заметки пользователями."""
        client_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in client_statuses:
            urls = (URLS.edit, URLS.detail, URLS.delete)
            for name in urls:
                with self.subTest(client=client):
                    response = client.get(name)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверить редирект для анонимного пользователя."""
        urls = (URLS.add, URLS.edit, URLS.detail,
                URLS.delete, URLS.list, URLS.success)
        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{URLS.login}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
