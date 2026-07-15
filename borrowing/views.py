from datetime import date

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
)
from notifications.telegram_helper import send_message
from payments.stripe_helper import create_stripe_session


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            book = serializer.validated_data["book"]
            book.inventory -= 1
            book.save()
            borrowing = serializer.save(user=self.request.user)
        text = (
            "📚 New borrowing created!\n\n"
            f"Borrower: {borrowing.user}\n"
            f"Book: {borrowing.book.title}\n"
            f"Borrow date: {borrowing.borrow_date}\n"
            f"Expected return: {borrowing.expected_return_date}"
        )
        send_message(text=text)
        create_stripe_session(borrowing)

    def get_queryset(self):
        queryset = Borrowing.objects.select_related(
            "book", "user"
        ).prefetch_related("payments")
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")
        if is_active == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)

        user_id = self.request.query_params.get("user_id")
        if user_id and user.is_staff:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        book = borrowing.book
        if borrowing.actual_return_date:
            raise ValidationError("This borrowing is already returned")

        with transaction.atomic():
            borrowing.actual_return_date = date.today()
            borrowing.save()
            book.inventory += 1
            book.save()
            return Response(status=status.HTTP_200_OK)
