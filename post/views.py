from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings

from post.models import Post, Tag, Follow, Stream, Likes,Folder
from django.contrib.auth.models import User
from post.forms import NewPostform,FolderForm
from authy.models import Profile
from django.urls import resolve
from comment.models import Comment
from comment.forms import NewCommentForm
from django.core.paginator import Paginator
from django.contrib import messages

from django.db.models import Q
# from post.models import Post, Follow, Stream
import requests,os,uuid



@login_required
def index(request):
    user = request.user
    user = request.user
    all_users = User.objects.all()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    profile = Profile.objects.all()

    posts = Stream.objects.filter(user=user)
    group_ids = []

    
    for post in posts:
        group_ids.append(post.post_id)
        
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')

    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(username__icontains=query))

        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)


    context = {
        'post_items': post_items,
        'follow_status': follow_status,
        'profile': profile,
        'all_users': all_users,
        # 'users_paginator': users_paginator,
    }
    return render(request, 'index.html', context)


@login_required
def NewPost(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    tags_obj = []

    if user.username == 'movie_time':
        api_key = 'fec735dd0fe3097e55bcc4b2d09ac477'
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            movies = data['results']
            
            for movie in movies:
                new_post = Post.objects.create(
                    picture=movie['poster_path'],  
                    caption=movie['overview'],
                    user=user,
                )
                new_post.save()

        form = NewPostform(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tags')
            tag_list = list(tag_form.split(','))

            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_obj.append(t)
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user=user)
            p.tags.set(tags_obj)
            p.save()
            return redirect('profile', request.user.username)
    else:
        form = NewPostform()
    context = {
        'form': form
    }
    return render(request, 'newpost.html', context)


@login_required
def PostDetail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-date')

    if user.username=='movie_time':
                api_key='fec735dd0fe3097e55bcc4b2d09ac477'
                url=f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'

                response=requests.get(url)
                if response.status_code == 200:
                    data=response.json()
                    movies=data['results']

                    for movie in movies:
                        new_post= Post.objects.create(
                            caption=movie['overview'],
                            picture=movie['poster_path'],
                            user=user,
                        )
            
                        new_post.save()
                form = NewCommentForm(request.POST)
                if form.is_valid():
            
                    comment = form.save(commit=False)
                    comment.post = post
                    comment.user = user
                    comment.save()
                    return HttpResponseRedirect(reverse('post-details', args=[post.id]))

    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('post-details', args=[post.id]))
    else:
        form = NewCommentForm()

    

    context = {
        'post': post,
        'form': form,
        'comments': comments
    }

    return render(request, 'postdetail.html', context)

@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')

    context = {
        'posts': posts,
        'tag': tag

    }
    return render(request, 'tag.html', context)


# Like function
@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).count()

    if not liked:
        Likes.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
        
    post.likes = current_likes
    post.save()
    # return HttpResponseRedirect(reverse('post-details', args=[post_id]))
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))

@login_required
def favourite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))

@login_required
def folder_create(request,post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user
            folder.save()
            messages.success(request, 'Folder created successfully')
            return redirect('post-add-to-folder',post.pk)
    else:
        form = FolderForm()
    return render(request, 'blog/folder_create.html', {'form': form})
"""
@login_required
def post_add_to_folder(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    folders = request.user.folder_set.all()
    if request.method == 'POST':
        selected_folders = request.POST.getlist('folders')
        for folder_id in selected_folders:
            folder = Folder.objects.get(pk=folder_id)
            folder.posts.add(post)  # Add the post to the folder's posts

        messages.success(request, 'Post added to folder(s) successfully')
        return redirect('post-details', post.pk)

    return render(request, 'blog/post_add_to_folder.html', {'post': post, 'folders': folders})

@login_required
def post_add_to_folder(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    folders = request.user.folder_set.all()
    if request.method == 'POST':
        selected_folders = request.POST.getlist('folders')
        visibility = request.POST.get('visibility')

        if visibility == 'selected':
            selected_followers = request.POST.getlist('selected_followers')
            followers = User.objects.filter(pk__in=selected_followers)
        else:
            followers = []

        for folder_id in selected_folders:
            folder = Folder.objects.get(pk=folder_id)
            folder.posts.add(post)  # Add the post to the folder's posts

            # Update folder visibility and followers
            folder.is_public = visibility == 'public'
            folder.followers.set(followers)
            folder.save()

        messages.success(request, 'Post added to folder(s) successfully')
        return redirect('post-details', post.pk)

    return render(request, 'blog/post_add_to_folder.html', {'post': post, 'folders': folders})

"""
@login_required
def post_add_to_folder(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    folders = request.user.folder_set.all()

    if request.method == 'POST':
        selected_folders = request.POST.getlist('folders')
        visibility = request.POST.get('visibility')

        if visibility == 'selected':
            selected_followers = request.POST.getlist('selected_followers')
            followers = User.objects.filter(pk__in=selected_followers)
        else:
            followers = []

        for folder_id in selected_folders:
            folder = Folder.objects.get(pk=folder_id)
            folder.posts.add(post)  # Add the post to the folder's posts

            # Update folder visibility and followers
            folder.visibility = visibility
            folder.followers.set(followers)
            folder.save()

        messages.success(request, 'Post added to folder(s) successfully')
        return redirect('post-details', post.pk)

    # Retrieve the list of users you follow
    following_users = User.objects.filter(following__follower=request.user)

    return render(request, 'blog/post_add_to_folder.html', {
        'post': post,
        'folders': folders,
        'following_users': following_users,
    })


@login_required
def folder_list(request):
    folders = Folder.objects.filter(user=request.user)
    return render(request, 'blog/folder_list.html', {'folders': folders})


@login_required
def folder_detail(request, slug):
    folder = get_object_or_404(Folder, slug=slug, user=request.user)
    posts = folder.post_set.all()
    return render(request, 'blog/folder_detail.html', {'folder': folder, 'posts': posts})


@login_required
def post_remove_from_folder(request, folder_slug, post_id):
    folder = get_object_or_404(Folder, slug=folder_slug, user=request.user)
    post = get_object_or_404(Post, pk=post_id)
    folder.post_set.remove(post)
    messages.success(request, 'Post removed from folder successfully')
    return redirect('folder-detail', slug=folder_slug)


@login_required
def post_move_to_folder(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    current_folder = post.folder_set.first()
    folders = request.user.folder_set.all()
    if request.method == 'POST':
        selected_folder = request.POST.get('folder')
        if selected_folder:
            folder = Folder.objects.get(pk=selected_folder)
            post.folder_set.remove(current_folder)
            post.folder_set.add(folder)
            messages.success(request, 'Post moved to folder successfully')
        return redirect('post-detail', post.pk)
    return render(request, 'blog/post_move_to_folder.html', {'post': post, 'folder': folders, 'current_folder': current_folder})
"""
@login_required
def saved_folders(request,user):
    #print(request.user)
    selected_user=get_object_or_404(User,id=user)
    folders = Folder.objects.filter(user=selected_user)
    return render(request, 'blog/saved_folders.html', {'folders': folders})

"""
@login_required
def saved_folders(request, user):
    selected_user = get_object_or_404(User, id=user)
    folders = Folder.objects.filter(user=selected_user)

    visible_folders = []
    for folder in folders:
        
        if folder.is_visible_to_user(request.user):
            visible_folders.append(folder)

    return render(request, 'blog/saved_folders.html', {'folders': visible_folders})

