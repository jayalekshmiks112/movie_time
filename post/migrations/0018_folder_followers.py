# Generated by Django 3.1 on 2023-05-22 16:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0017_auto_20230521_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='followers',
            field=models.ManyToManyField(related_name='followed_folders', to=settings.AUTH_USER_MODEL),
        ),
    ]
