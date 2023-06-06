from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.signals import post_save, post_delete
from django.utils.text import slugify
from django.urls import reverse
import uuid

# Create your models here.

class Series(models.Model):
    id = models.CharField(unique=True, max_length=50, primary_key=True)
    title = models.CharField(max_length=50, null=True)
    language = models.CharField(max_length=50, null=True)
    overview = models.TextField(null=True)
    poster = models.URLField(max_length=200, null=True)
    release_date = models.CharField(max_length=50, null=True)

    # created by
    production_name = models.CharField(max_length=50, null=True)
    production_logo = models.URLField(max_length=200, null=True)

    first_air_date = models.CharField(max_length=50, null=True)
    in_production = models.BooleanField(null=True)
    no_of_episodes = models.IntegerField(null=True)
    no_of_seasons = models.IntegerField(null=True)
    origin_country = models.CharField(max_length=50, null=True)

    tagline = models.CharField(max_length=50, null=True)
    adult = models.BooleanField(default=False)

    popularity = models.IntegerField(null=True)
    vote_average = models.FloatField(null=True)
    vote_count = models.IntegerField(null=True)

    lit = models.IntegerField(default=0)
    shit = models.IntegerField(default=0)

    subscribers = models.ManyToManyField(User)

class Season(models.Model):
    id = models.CharField(unique=True, max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    air_date = models.CharField(max_length=50)
    episode_count = models.IntegerField()
    overview = models.TextField()
    poster = models.URLField(max_length=200)
    season_number = models.IntegerField()


class Movie(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50, null=True)
    language = models.CharField(max_length=50, null=True)
    overview = models.TextField(null=True)
    poster = models.URLField(max_length=200, null=True)
    release_date = models.CharField(max_length=50, null=True)

    # created by
    production_name = models.CharField(max_length=50, null=True)
    production_logo = models.URLField(max_length=200, null=True)

    revenue = models.IntegerField(null=True)
    budget = models.IntegerField(null=True)
    runtime = models.IntegerField(null=True)

    tagline = models.CharField(max_length=50)
    adult = models.BooleanField(null=True)

    popularity = models.IntegerField(null=True)
    vote_average = models.FloatField(null=True)
    vote_count = models.IntegerField(null=True)

    lit = models.IntegerField(default=0)
    shit = models.IntegerField(default=0)

    subscribers = models.ManyToManyField(User)
    already_seen = models.ManyToManyField(User, related_name='seen')


class Playlist(models.Model):
    key = models.SlugField(unique=True, default=uuid.uuid1)
    title = models.CharField(max_length=50, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    saved_by = models.ManyToManyField(User, related_name="saved", null=True)
    access = models.ManyToManyField(User, related_name="shared_to", null=True)

    movies = models.ManyToManyField(Movie, null=True)
    series = models.ManyToManyField(Series, null=True)
    
    liked_by = models.ManyToManyField(User, related_name='liked', null=True)