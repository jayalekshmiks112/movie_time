from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from django.forms import DateTimeField
from search.models import *

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    reciepient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    body = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def sender_message(from_user, to_user, body):
        sender_message = Message(
            user=from_user,
            sender = from_user,
            reciepient = to_user,
            body = body,
            is_read = True
            )
        sender_message.save()
    
        reciepient_message = Message(
            user=to_user,
            sender = from_user,
            reciepient = from_user,
            body = body,
            is_read = True
            )
        reciepient_message.save()
        return sender_message

    def get_message(user):
        users = []
        messages = Message.objects.filter(user=user).values('reciepient').annotate(last=Max('date')).order_by('-last')
        for message in messages:
            users.append({
                'user': User.objects.get(pk=message['reciepient']),
                'last': message['last'],
                'unread': Message.objects.filter(user=user, reciepient__pk=message['reciepient'], is_read=False).count()
            })
        return users
            
class MediaShare(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    reciepient = models.ForeignKey(User, related_name='reciepient', on_delete=models.CASCADE)

    media_type = models.CharField(max_length=50)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)

    on = models.DateTimeField(auto_now_add=True)

    def send_message(from_user, to_username, media_type, media):
        send_to = User.objects.filter(username=to_username).first()
        if media_type=='movie':
            MediaShare.objects.create(
                sender=from_user,
                reciepient=send_to,
                media_type='movie',
                movie=media
            )
        else :
            MediaShare.objects.create(
                sender=from_user,
                reciepient=send_to,
                media_type='series',
                series=media
            )
