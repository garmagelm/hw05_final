from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.decorators.cache import cache_page
from .models import Follow, Post, Group
from .forms import CommentForm, PostForm

User = get_user_model()


@cache_page(60 * 15)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {"page": page, "paginator": paginator}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {"group": group, "page": page, "paginator": paginator}
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    post_user = get_object_or_404(User, username=username)
    posts = post_user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user).filter(
                author=post_user).exists()
    else:
        following = True
    return render(request, 'profile.html',
                  {'page': page,
                   'paginator': paginator,
                   'author': post_user,
                   'follower_count': post_user.following.count(),
                   'following_count': post_user.follower.count,
                   'following': following,
                   })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm()
    comments = post.comments.all()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user).filter(
                author=post.author).exists()
    else:
        following = True
    return render(request, 'post.html', {
        'post': post,
        'count': post.author.posts.count(),
        'post_user': post.author,
        'form': form,
        'comments': comments,
        'follower_cnt': post.author.following.count(),
        'following_cnt': post.author.follower.count(),
        'following': following
    })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username
    )
    if request.user != post.author:
        return redirect('post', post_id=post.id, username=post.author.username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', post_id=post.id, username=post.author.username)
    return render(request, 'new.html', {
        'form': form,
        'post': post,
        'edit': True
    })


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, post_id, username):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page,
                                           'paginator': paginator})


@login_required
def profile_follow(request, username):
    if request.user.get_username() == username:
        return redirect(reverse('profile', kwargs={'username': username}))
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(reverse('profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    if request.user.get_username() == username:
        return redirect(reverse('profile', kwargs={'username': username}))
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(reverse('profile', kwargs={'username': username}))
