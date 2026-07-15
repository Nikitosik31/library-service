import stripe
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment, Status
from payments.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)
        return queryset

    @action(detail=False, methods=["get"], url_path="cancel")
    def cancel(self, request):
        return Response(
            {
                "message": "Payment can be paid later. "
                "The session is available for 24 hours."
            }
        )

    @action(detail=False, methods=["get"], url_path="success")
    def success(self, request):
        session_id = request.query_params.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            payment = Payment.objects.get(session_id=session_id)
            payment.status = Status.PAID
            payment.save()
            return Response({"message": "Payment successful! "})
        return Response(
            {"message": "Payment not completed yet! . "},
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )
