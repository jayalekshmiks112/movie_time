# Generated by Django 3.1 on 2023-05-19 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0015_auto_20230519_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='posts',
            field=models.ManyToManyField(to='post.Post'),
        ),
    ]