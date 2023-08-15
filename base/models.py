from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, SET_NULL

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Room(models.Model):
    host = models.ForeignKey(User,on_delete= models.SET_NULL,null=True)
    topic =  models.ForeignKey(Topic,on_delete= models.SET_NULL,null=True) # When topic is deleted, the room will be left NULL (Blank)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True) # we need to have related_name becuase User is already connected to host field, so use related_name to avoid collision
    # and blank= True because it can leave as No participants
    updated = models.DateTimeField(auto_now=True) #Takes a snapshot everytime we saave
    created = models.DateTimeField(auto_now_add=True) # take a timestamp only when we first add this instance

    class Meta:
        # ordering =['updated', 'created'] <-- this will ordering with ascending order (what latest created will be at bottommost)
        ordering = ['-updated', '-created'] # reversed the above, the latest create will be at topmost
    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #models.CASCADE is when the room is deleted, the entire message in the room will be deleted
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) #Takes a snapshot everytime we saave
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50] # trim it down, we only the first 50 characters in PREVIEW