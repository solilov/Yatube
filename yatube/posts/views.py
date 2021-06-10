"""Запросы к БД"""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POST_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.all()
    paginator = Paginator(posts, settings.POST_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "posts/group.html", {"group": group, "page": page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    posts_count = author_posts.count()
    paginator = Paginator(author_posts, settings.POST_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/profile.html', {'author': author,
                                                  'count': posts_count,
                                                  'page': page})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    posts_count = author.posts.count()
    post = author.posts.get(pk=post_id)
    form = CommentForm
    comments = post.comments.all()
    return render(request, 'posts/post.html', {'author': author,
                                               'count': posts_count,
                                               'post': post,
                                               'form': form,
                                               'comments': comments})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'posts/new.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('post', username, post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'posts/new.html', {'form': form,
                                              'edit': True})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
        return redirect('post', username, post_id)
    return render(
        request, 'posts/comments.html', {
            'form': form,
            'post': post
        }
    )


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.POST_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, "misc/404.html", {"path": request.path}, status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
