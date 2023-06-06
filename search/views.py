from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings

from .models import *
from django.contrib.auth.models import User
from authy.models import Profile
from django.urls import resolve
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.generic import View
from django.db.models import Q
# from post.models import Post, Follow, Stream
import requests, os, uuid
from .utils import *
from authy.models import Story
# Create your views here.

class SearchView(View):
    def post(self, request, format=None):
        data = request.POST
        query = data.get('query')
        adult = data.get('adult')

        response = execute_api_call(
            f"search/multi",
            {
                'query': query,
                'include_adult': adult,
                'language': 'en-US',
                'page': 1
            }
        )

        results = response.get('results')
        for result in results:
            print(result.get('backdrop_path'))
            if result.get('media_type') == 'movie':
                if not Movie.objects.filter(id=result.get('id')).exists():
                    Movie.objects.create(
                        id = result.get('id'),
                        title = result.get('original_title'),
                        language = result.get('original_language'),
                        overview = result.get('overview'),
                        poster = result.get('poster_path'),
                        release_date = result.get('release_date'),
                        vote_average = result.get('vote_average'),
                        vote_count = result.get('vote_count'),
                        popularity = result.get('popularity'),
                        adult = result.get('adult'),
                    )
            else :
                if not Series.objects.filter(id=result.get('id')).exists():
                    Series.objects.create(
                        id = result.get('id'),
                        title = result.get('original_name'),
                        language = result.get('original_language'),
                        overview = result.get('overview'),
                        poster = result.get('poster_path'),
                        release_date = result.get('release_date'),
                        vote_average = result.get('vote_average'),
                        vote_count = result.get('vote_count'),
                        popularity = result.get('popularity'),
                        adult = result.get('adult'),
                    )
        return render(request, 'search/results.html', {'results': results, 'query':query, 'type': 'media'})

class MediaDetailView(View):
    def get(self, request, media_type, media_id):
        if media_type == 'movie':
            media = Movie.objects.get(id=media_id)
        elif media_type == 'tv':
            media = Series.objects.get(id=media_id)
        else:
            media = None

        # Fetch additional details from TMDB API and update the object
        if media and not media.production_name:
            endpoint = f'/{media_type}/{media.id}'
            response = execute_api_call(endpoint, {})
            # if response.status_code == 200:
            data = response
            # Update the object with the fetched details
            if media_type == 'movie':
                media.release_date = data['release_date']
                media.production_name = data['production_companies'][0]['name']
                media.production_logo = data['production_companies'][0]['logo_path']
                media.runtime = data['runtime']
                media.revenue = data['revenue']
                media.budget = data['budget']
                # Update more movie-specific fields
            elif media_type == 'tv':
                media.first_air_date = data['first_air_date']
                media.production_name = data['production_companies'][0]['name']
                media.production_logo = data['production_companies'][0]['logo_path']
                media.in_production = data['in_production']
                media.no_of_episodes = data['number_of_episodes']
                media.no_of_seasons = data['number_of_seasons']
                media.origin_country = ', '.join(data['origin_country'])
                media.tagline = data['tagline']
                # Update more series-specific fields
            media.save()
        playlists = Playlist.objects.filter(created_by=request.user)
        payload = {
            'media': media, 
            'playlists': playlists, 
            'media_type': media_type, 
            'already_seen': request.user in media.already_seen.all(),
        }
        return render(request, 'search/details.html', payload)


class AddToPlaylistView(View):
    def get(self, request, media_type, media_id, playlist_key):
        if media_type == 'movie':
            media = Movie.objects.get(id=media_id)
        elif media_type == 'series':
            media = Series.objects.get(id=media_id)
        else:
            media = None

        if media:
            playlist, created = Playlist.objects.get_or_create(key=playlist_key)
            if media_type == 'movie':
                playlist.movies.add(media)
            elif media_type == 'series':
                playlist.series.add(media)

        return render(request, 'search/playlist.html', {'playlist': playlist})

class SubscribeUnsubscribeView(View):
    def get(self, request, action, media_type, media_id):

        if media_type == 'movie':
            media = Movie.objects.get(id=media_id)
        elif media_type == 'series':
            media = Series.objects.get(id=media_id)
        else:
            media = None

        if media:
            user = request.user  # Assuming user authentication is implemented
            if action == 'subscribe':
                Notification.objects.create(
                    user=user,
                    text=f'Subscribed to {media_type} {media.title} updates.'
                )
            elif action == 'unsubscribe':
                Notification.objects.filter(user=user, media=media).delete()

        return render(request, 'subscription.html')

class GetPlaylistView(View):
    def get(self, request, playlist_key):
        playlist = Playlist.objects.filter(key=playlist_key)
        if playlist.exists():
            playlist = playlist.first()
            context = {
                'details': playlist,
                'movies': playlist.movies.all(),
                'series': playlist.series.all(),

                'saved_by': len(playlist.saved_by.all()),
                'liked_by': len(playlist.liked_by.all()),

                'saved': request.user in playlist.saved_by.all(),
                'liked': request.user in playlist.liked_by.all(),
            }
            return render(request, 'search/playlist.html', context=context)
        return render(request, 'search/playlist.html')

class RatingFormView(View):
    def post(self, request):
        rating = request.POST.get('rating')

        media_type = request.POST.get('media_type')
        media_id = request.POST.get('media_id')
        # Process the rating value as needed

        if media_type=='movie':
            media = Movie.objects.filter(id=media_id).first()
        else :
            media = Series.objects.filter(id=media_id).first()
        
        media.vote_count += 1
        if media.vote_count != 0:
            media.vote_average = (media.vote_average*media.vote_count + int(rating))/media.vote_count
        else :
            media.vote_average = int(rating)
        
        media.save(update_fields=['vote_count', 'vote_average'])
        return redirect('media-details', media_type=media_type, media_id=media_id)

class StoryFormView(View):
    def post(self, request):
        caption = request.POST.get('caption')
        tags = request.POST.get('tags')
        date = request.POST.get('datetime')
        media_type = request.POST.get('media_type')
        media_id = request.POST.get('media_id')
        
        # Process the form data as needed
        story = Story.objects.create(
            caption=caption,
            tags=tags,
            live_till=date,
            user=request.user,
        )
        if media_type=='movie':
            media = Movie.objects.filter(id=media_id).first()
            story.movie = media
            story.save(update_fields=['movie'])
        else :
            media = Series.objects.filter(id=media_id).first()
            story.series = media
            story.save(update_fields=['series'])

        return redirect('media-details', media_type=media_type, media_id=media_id)
        

class LikeUnlikeView(View):
    def get(self, request, action, media_type, media_id):

        if media_type == 'movie':
            media = Movie.objects.get(id=media_id)
        elif media_type == 'series':
            media = Series.objects.get(id=media_id)
        else:
            media = None

        if media:
            user = request.user  # Assuming user authentication is implemented
            if action == 'lit':
                media.lit += 1
                media.save(update_fields=['lit'])
                # Notification.objects.create(
                #     user=user,
                #     text=f'Liked to {media_type} {media.title} updates.'
                # )
            elif action == 'shit':
                media.shit += 1
                media.save(update_fields=['shit'])
                # Notification.objects.filter(user=user, media=media).delete()

        return redirect('media-details', media_id=media_id, media_type=media_type)

class PlaylistSaveView(View):
    def get(self, request, slug):
        playlist = Playlist.objects.filter(key=slug).first()
        
        playlist.saved_by.add(request.user)
        playlist.save(update_fields=['saved_by'])

        return redirect('get-playlist', playlist_key=slug)


class PlaylistLikeView(View):
    def get(self, request, slug):

        playlist = Playlist.objects.filter(key=slug).first()

        playlist.liked_by.add(request.user)
        playlist.save()

        return redirect('get-playlist', playlist_key=slug)

class AlreadySeenThisView(View):
    def get(self, request, media_id, media_type, action):
        if media_type == 'movie':
            media = Movie.objects.get(id=media_id)
        elif media_type == 'series':
            media = Series.objects.get(id=media_id)
        else:
            media = None

        if action == 'seen':
            media.already_seen.add(request.user)
        else:
            media.already_seen.remove(request.user)
        media.save()

        return redirect('media-details', media_type=media_type, media_id=media_id)

class ExplorePageView(View):
    def get(self, request, format=None):
        topmovies = []
        topseries = []
        topplaylists = []

        response = execute_api_call(
            f"trending/all/week",
            {
                'language': 'en-US',
            }
        )

        results = response.get('results')
        for result in results:
            if result.get('media_type') == 'movie':
                movie = Movie.objects.filter(id=result.get('id'))
                if not Movie.objects.filter(id=result.get('id')).exists():
                    movie = Movie.objects.create(
                        id = result.get('id'),
                        title = result.get('original_title'),
                        language = result.get('original_language'),
                        overview = result.get('overview'),
                        poster = result.get('poster_path'),
                        release_date = result.get('release_date'),
                        vote_average = result.get('vote_average'),
                        vote_count = result.get('vote_count'),
                        popularity = result.get('popularity'),
                        adult = result.get('adult'),
                    )
                    topmovies.append(movie)
                else:
                    topmovies.append(movie.first())
            else :
                tv = Series.objects.filter(id=result.get('id'))
                if not Series.objects.filter(id=result.get('id')).exists():
                    tv = Series.objects.create(
                        id = result.get('id'),
                        title = result.get('original_name'),
                        language = result.get('original_language'),
                        overview = result.get('overview'),
                        poster = result.get('poster_path'),
                        release_date = result.get('release_date'),
                        vote_average = result.get('vote_average'),
                        vote_count = result.get('vote_count'),
                        popularity = result.get('popularity'),
                        adult = result.get('adult'),
                    )
                    topseries.append(tv)
                else:
                    topseries.append(tv.first())

        playlists = Playlist.objects.all().order_by('liked_by')
        topplaylists = [{
            'details': i,
            'saves': len(i.saved_by.all()),
            'likes': len(i.liked_by.all()),
            'movies': len(i.movies.all()),
            'series': len(i.series.all())
        } for i in playlists]

        payload = {
            'top_movies': topmovies,
            'top_series': topseries,
            'top_playlists': topplaylists,
        }
        return render(request, 'search/explore.html', payload)

class SearchMediaOrUser(View):
    def get(self, request, format=None):
        return render(request, 'search/search_tab.html')

    def post(self, request, format=None):
        data = request.POST
        query = data.get('query')

        users = User.objects.all()
        results = []
        for user in users:
            if query in user.username:
                results.append(user)
        
        return render(request, 'search/results.html', {'results': results, 'query': query, 'type': 'users'})