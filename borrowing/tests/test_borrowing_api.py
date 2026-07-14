from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.tests.helpers import sample_user, sample_book
from borrowing.models import Borrowing

BORROWING_URL = reverse("borrowing:borrowing-list")


class AuthenticatedBorrowingApiTest(APITestCase):
    def setUp(self):
        self.user = sample_user()
        self.client.force_authenticate(self.user)
        self.book = sample_book(inventory=5)

    def test_create_borrowing_decreases_inventory(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": "2026-08-01",
        }
        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_create_borrowing_attaches_user(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": "2026-08-01",
        }
        res = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(book=self.book)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(borrowing.user, self.user)

    def test_cannot_borrow_out_of_stock(self):
        book = sample_book(inventory=0)
        payload = {
            "book": book.id,
            "expected_return_date": "2026-08-01",
        }
        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
