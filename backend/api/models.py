from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postcode = models.CharField(max_length=10)

class Ticket(models.Model):
    number = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    eventId = models.IntegerField()
    event = models.CharField(max_length=255)
    cancellationReason = models.CharField(max_length=255, blank=True)
    promoter = models.CharField(max_length=255)
    price_amount = models.CharField(max_length=255)
    price_currency = models.CharField(max_length=3)

class Session(models.Model):
    ticket = models.ForeignKey('Ticket', related_name='sessions', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    time = models.CharField(max_length=255)
    doors = models.CharField(max_length=255)
    location = models.OneToOneField('Location', on_delete=models.CASCADE)

class Buyer(models.Model):
    role = models.CharField(max_length=255)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    postcode = models.CharField(max_length=10)

class TicketCreatedEvent(models.Model):
    event = models.CharField(max_length=255)
    ticket = models.OneToOneField('Ticket', on_delete=models.CASCADE)
    buyer = models.OneToOneField('Buyer', on_delete=models.CASCADE)
