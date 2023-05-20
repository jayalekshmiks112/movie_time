from django.urls import path
#from post.views import index, NewPost, PostDetail, Tags, like, favourite
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('newpost', views.NewPost, name='newpost'),
    path('<uuid:post_id>', views.PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>', views.Tags, name='tags'),
    path('<uuid:post_id>/like', views.like, name='like'),
    path('<uuid:post_id>/favourite', views.favourite, name='favourite'),
    path('<uuid:post_id>/folder/create', views.folder_create, name='folder-create'),
    path('folders/', views.folder_list, name='folder-list'),
    path('folder/<slug:slug>', views.folder_detail, name='folder-detail'),
    path('<uuid:post_id>/add-to-folder', views.post_add_to_folder, name='post-add-to-folder'),
    path('saved/<int:user>/', views.saved_folders, name='saved-folders'),


]
