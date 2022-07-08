from django.db import models

# Create your models here.

class Message(models.Model):
    sender = models.fields.CharField(max_length=50)
    text = models.fields.CharField(max_length=1000)

class Conversation(models.Model):
    msg = models.ForeignKey(Message, on_delete=models.CASCADE)
