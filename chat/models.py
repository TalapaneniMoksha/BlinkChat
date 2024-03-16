from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.CharField(null=True, blank=True, max_length=1000)
    participants = models.ManyToManyField(User, related_name='rooms_participated', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    restricted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)  # Add this line for PDF uploads
    image = models.ImageField(upload_to='images/', null=True, blank=True)  # Add this line for image uploads
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated', '-created']
        
    def __str__(self):
        return self.body[:50]
