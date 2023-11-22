from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import WebhookDataSerializer, TicketSerializer, BuyerSerializer

class WebhookView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = WebhookDataSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            ticket_serializer = TicketSerializer(data=data.get('details', {}).get('ticket', {}))
            buyer_serializer = BuyerSerializer(data=data.get('buyer', {}))

            if ticket_serializer.is_valid() and buyer_serializer.is_valid():
                # Process the valid data as needed
                ticket_data = ticket_serializer.validated_data
                buyer_data = buyer_serializer.validated_data
                print("Received data:", data)
                print("Ticket Data:", ticket_data)
                print("Buyer Data:", buyer_data)

                # Implement your logic here using the extracted data

                return Response({"status": "success"}, status=status.HTTP_200_OK)
            else:
                print("Ticket Serializer errors:", ticket_serializer.errors)
                print("Buyer Serializer errors:", buyer_serializer.errors)
                return Response({"status": "error", "errors": {"ticket": ticket_serializer.errors, "buyer": buyer_serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
