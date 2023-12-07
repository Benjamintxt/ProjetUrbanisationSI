from rest_framework import serializers
from .models import Location, Ticket, Buyer, Session

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'street', 'city', 'postcode']

class SessionSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = Session
        fields = ['name', 'date', 'time', 'doors', 'location']

class PriceSerializer(serializers.Serializer):
    amount = serializers.CharField()
    currency = serializers.CharField()

class TicketSerializer(serializers.ModelSerializer):
    sessions = SessionSerializer(many=True)
    promoter = serializers.CharField()
    price = PriceSerializer()

    class Meta:
        model = Ticket
        fields = ['number', 'type', 'title', 'category', 'eventId', 'event',
                  'cancellationReason', 'sessions', 'promoter', 'price']

    def create(self, validated_data):
        sessions_data = validated_data.pop('sessions')
        ticket = Ticket.objects.create(**validated_data)

        for session_data in sessions_data:
            location_data = session_data.pop('location')
            session = ticket.sessions.create(**session_data)
            Location.objects.create(session=session, **location_data)

        return ticket

class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = ['role', 'firstName', 'lastName', 'postcode']

class WebhookDataSerializer(serializers.Serializer):
    event = serializers.CharField()
    details = TicketSerializer()
    buyer = BuyerSerializer()
    
    def create(self, validated_data):
        ticket_data = validated_data.pop('details')
        buyer_data = validated_data.pop('buyer', None)

        ticket_serializer = TicketSerializer(data=ticket_data)
        ticket_serializer.is_valid(raise_exception=True)
        ticket = ticket_serializer.save()

        if buyer_data:
            Buyer.objects.create(ticket=ticket, **buyer_data)

        return ticket
