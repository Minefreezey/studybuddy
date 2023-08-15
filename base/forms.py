from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__' #this will create the form based on the metadata of ROOM model, so it will create host, topic, name etc.
        exclude = ['host', 'participants']
        # fields = ['topi','name','description'] <-- this is for specified field we want to show