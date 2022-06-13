from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User
from .utils import paginate


@cache_page(settings.CACHE_TIMEOUT, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('group', 'author')
    page_obj = paginate(post_list, request.GET.get('page'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginate(post_list, request.GET.get('page'))
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if not request.user.is_authenticated:
        following = False
    else:
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
        else:
            following = False
    post_list = author.posts.all()
    page_obj = paginate(post_list, request.GET.get('page'))
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(), pk=post_id)
    comment_list = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': comment_list,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post.objects.select_related(), pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f'/profile/{str(post.author)}/')
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post.objects.select_related(), pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Вывести посты авторов из подписки"""
    authors = Follow.objects.select_related('author').filter(
        user=request.user).values('author')
    post_list = Post.objects.select_related('group', 'author').filter(
        author__in=authors)
    page_obj = paginate(post_list, request.GET.get('page'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    if request.user.username == username:
        return redirect('posts:follow_index')
    author = User.objects.get(username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        follow_link = Follow.objects.create(
            user=request.user,
            author=author,
        )
        follow_link.save()
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect('posts:follow_index')
