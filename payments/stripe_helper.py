import stripe
from django.conf import settings
from django.urls import reverse

from borrowing.models import Borrowing
from payments.models import Payment, Status, Type


def create_stripe_session(borrowing: Borrowing, request):
    days = (borrowing.expected_return_date - borrowing.borrow_date).days
    sum_money = days * borrowing.book.daily_fee
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(sum_money * 100),
                    "product_data": {"name": borrowing.book.title},
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(
            reverse("payments:payment-success")
        )
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(
            reverse("payments:payment-cancel")
        ),
    )

    payment = Payment.objects.create(
        status=Status.PENDING,
        type=Type.PAYMENT,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=sum_money,
    )
    return payment
