from django.contrib.auth import get_user_model

from books.models import Book


def sample_user(**params):
    defaults = {
        "email": "testjgvghbk@test",
        "password": "testtest",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_book(**params):
    defaults = {
        "title": "test",
        "author": "test",
        "cover": "Hard",
        "inventory": 5,
        "daily_fee": "1.50",
    }
    defaults.update(params)
    return Book.objects.create(**defaults)
