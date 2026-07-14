from celery import shared_task
from django.utils import timezone

from borrowing.models import Borrowing
from notifications.telegram_helper import send_message


@shared_task
def check_overdue_borrowings():
    today = timezone.now().date()
    overdue = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
    )
    if not overdue.exists():
        send_message("No borrowings overdue today!")
        return

    for borrowing in overdue:
        text = (
            "⚠️ Overdue borrowing!\n\n"
            f"Borrower: {borrowing.user}\n"
            f"Book: {borrowing.book.title}\n"
            f"Expected return: {borrowing.expected_return_date}"
        )
        send_message(text=text)
