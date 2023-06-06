# Generated by Django 4.1.4 on 2023-05-28 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0006_alter_playlist_access_alter_playlist_key_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authy', '0010_story'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='caption',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='story',
            name='live_till',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='story',
            name='movie',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='search.movie'),
        ),
        migrations.AlterField(
            model_name='story',
            name='series',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='search.series'),
        ),
        migrations.AlterField(
            model_name='story',
            name='tags',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='story',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]