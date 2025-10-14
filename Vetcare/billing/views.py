from django.conf import settings
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Invoice, Payment
from .serializers import InvoiceSerializer, PaymentSerializer
import uuid
import requests



PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_BASE_URL = "https://api.paystack.co"


class CreateInvoiceView(generics.CreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        reference = str(uuid.uuid4()).replace('-', '')[:12]
        serializer.save(user=self.request.user, reference=reference)


class InitializePaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        invoice_id = request.data.get('invoice_id')
        invoice = Invoice.objects.get(id=invoice_id)

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "email": request.user.email,
            "amount": int(invoice.amount * 100),  # Paystack expects kobo
            "reference": invoice.reference,
        }

        response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=data, headers=headers)
        res_data = response.json()

        if res_data.get('status'):
            return Response(res_data, status=status.HTTP_200_OK)
        else:
            return Response(res_data, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        reference = request.query_params.get('reference')

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        }

        response = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers)
        res_data = response.json()

        if res_data.get('status') and res_data['data']['status'] == 'success':
            try:
                invoice = Invoice.objects.get(reference=reference)
                invoice.mark_paid()
                Payment.objects.create(
                    invoice=invoice,
                    paystack_reference=reference,
                    amount=invoice.amount,
                    verified=True,
                )
            except Invoice.DoesNotExist:
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Payment verified successfully"}, status=status.HTTP_200_OK)

        return Response(res_data, status=status.HTTP_400_BAD_REQUEST)

