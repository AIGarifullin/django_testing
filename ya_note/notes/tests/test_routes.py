from http import HTTPStatus

from .common import BaseTestCase, url


class TestRoutes(BaseTestCase):
    def test_home_availability_for_anonymous_user(self):
        """Проверить доступ страниц для всех пользователей."""
        urls = (url.home, url.login, url.logout, url.signup)
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Проверить доступ страниц для автора заметки."""
        urls = (url.list, url.add, url.success)
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
            urls = (url.edit, url.detail, url.delete)
            for name in urls:
                with self.subTest(client=client):
                    response = client.get(name)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверить редирект для анонимного пользователя."""
        urls = (url.add, url.edit, url.detail,
                url.delete, url.list, url.success)
        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{url.login}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
