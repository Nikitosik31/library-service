from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from books.tests.helpers import sample_user, sample_book

BOOK_URL = reverse("books:book-list")


class UnauthenticatedBookApiTest(APITestCase):
    def test_read_book_list(self):
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTest(APITestCase):
    def setUp(self):
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden(self):
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": "Hard",
            "inventory": 3,
            "daily_fee": "2.00",
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(APITestCase):
    def setUp(self):
        self.user = sample_user(is_staff=True)
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": "Hard",
            "inventory": 3,
            "daily_fee": "2.00",
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
