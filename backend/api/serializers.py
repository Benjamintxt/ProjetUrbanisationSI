from rest_framework import serializers

class TicketSessionSerializer(serializers.Serializer):
    name = serializers.CharField()
    date = serializers.DateField()
    time = serializers.TimeField()
    doors = serializers.TimeField()
    location = serializers.DictField()

class TicketSerializer(serializers.Serializer):
    number = serializers.CharField()
    type = serializers.CharField()
    title = serializers.CharField()
    category = serializers.CharField()
    eventId = serializers.IntegerField()
    event = serializers.CharField()
    cancellationReason = serializers.CharField(allow_blank=True)
    sessions = TicketSessionSerializer(many=True)
    promoter = serializers.CharField()
    price = serializers.DictField()

class BuyerSerializer(serializers.Serializer):
    role = serializers.CharField(required=False)
    firstName = serializers.CharField(required=False)
    lastName = serializers.CharField(required=False)
    postcode = serializers.CharField(required=False)

class WebhookDataSerializer(serializers.Serializer):
    event = serializers.CharField()
    details = serializers.DictField(child=serializers.DictField())
    buyer = BuyerSerializer(required=False)

    def create(self, validated_data):
        # You can customize the create method if needed
        return validated_data
