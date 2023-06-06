from django.urls import path
#from post.views import index, NewPost, PostDetail, Tags, like, favourite
from .views import *

urlpatterns = [
    path('search/', SearchView.as_view(), name='search-movie'),
    path('details/<str:media_type>/<int:media_id>/', MediaDetailView.as_view(), name='media-details'),
    path('already-seen/<str:media_type>/<int:media_id>/<str:action>/', AlreadySeenThisView.as_view(), name='already-seen'),
    path('playlist/<str:playlist_key>/', GetPlaylistView.as_view(), name='get-playlist'),

    path('submit-rating/', RatingFormView.as_view(), name='submit-rating'),
    path('create-story/', StoryFormView.as_view(), name='create-story'),

    path('<str:action>/<str:media_type>/<str:media_id>/', LikeUnlikeView.as_view(), name='media-action'),
    path('<str:action>/<str:media_type>/<str:media_id>/', SubscribeUnsubscribeView.as_view(), name='media-subscribe'),

    path('playlist-save/<str:slug>/', PlaylistSaveView.as_view(), name='save-playlist'),
    path('playlist-like/<str:slug>/', PlaylistLikeView.as_view(), name='like-playlist'),

    path('explore/', ExplorePageView.as_view(), name='explore'),
    path('search-tab/', SearchMediaOrUser.as_view(), name='search-tab')
]
