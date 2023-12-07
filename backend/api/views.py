from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Buyer, Ticket, TicketCreatedEvent
from .serializers import WebhookDataSerializer, TicketSerializer, BuyerSerializer

class WebhookView(APIView):
    def post(self, request, *args, **kwargs):
        print("Received data:", request.data)
        serializer = WebhookDataSerializer(data=request.data)
        print("Serialized data : ", serializer)
        print("Is Serializer Valid?", serializer.is_valid())

        if serializer.is_valid():
            data = serializer.validated_data
            print("Validated Data:", data)
            ticket_data = data.get('details', {}).get('ticket', {})
            buyer_data = data.get('buyer', {})

            ticket_serializer = TicketSerializer(data=ticket_data)
            print("Ticket ID:", ticket.id)
            buyer_serializer = BuyerSerializer(data=buyer_data)

            if ticket_serializer.is_valid() and buyer_serializer.is_valid():
                try:
                    # Create Ticket and Buyer instances
                    print("Creating Ticket instance with data:", ticket_data)
                    ticket = Ticket.objects.create(**ticket_serializer.validated_data)
                    print("Ticket instance created successfully")

                    print("Creating Buyer instance with data:", buyer_data)
                    buyer = Buyer.objects.create(**buyer_serializer.validated_data)
                    print("Buyer instance created successfully")

                    # Create TicketCreatedEvent instance
                    print("Creating TicketCreatedEvent instance")
                    TicketCreatedEvent.objects.create(event=data.get('event'), ticket=ticket, buyer=buyer)
                    print("TicketCreatedEvent instance created successfully")

                    # You can implement additional logic here if needed

                    return Response({"status": "success"}, status=status.HTTP_200_OK)

                except Exception as e:
                    error_message = f"Error creating instances: {e}"
                    print(error_message)
                    return Response({"status": "error", "error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"status": "error", "errors": {"ticket": ticket_serializer.errors, "buyer": buyer_serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Serializer is invalid. Errors:", serializer.errors)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
