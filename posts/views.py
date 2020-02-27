from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post, Group, User, Comment, Favorite
from .forms import PostForm, CommentForm

def index(request):
    post_list = Post.objects.select_related('author', 'group').\
                            annotate(comment_count=Count('commented_post')).\
                            order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    index_page = True
    return render(request, "index.html", {'page': page,
                                          'paginator': paginator,
                                          'index_page':index_page})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).\
                            select_related('author', 'group').\
                            annotate(comment_count=Count('commented_post')).\
                            order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    post_count = Post.objects.filter(group=group).count()
    return render(request, "group.html", {"group": group,
                                          "page": page,
                                          'paginator': paginator,
                                          'post_count':post_count})

@login_required
def new_post(request):
    title = 'Опубликовать'
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form, 'title':title})

@login_required
def post_view(request, post_id, username):
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post.objects.annotate(comment_count=Count('commented_post')).\
                             select_related('author'),
                             pk=post_id)
    post_count = Post.objects.filter(author=user_profile).count()
    post_comment = Comment.objects.filter(post=post_id).select_related('author').all()
    follower_count = Favorite.objects.filter(author=user_profile).count()
    following_count = Favorite.objects.filter(user=user_profile).count()
    form = CommentForm()
    return render(request, 'post_view.html', {'post':post,
                                              'profile':user_profile,
                                              'post_count':post_count,
                                              'comments': post_comment,
                                              'form':form,
                                              'follower_count':follower_count,
                                              'following_count':following_count})

def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user_profile).\
                            select_related('group', 'author').\
                            annotate(comment_count=Count('commented_post')).\
                            order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    follower_count = Favorite.objects.filter(author=user_profile).count()
    following_count = Favorite.objects.filter(user=user_profile).count()
    if request.user.is_authenticated:
        if Favorite.objects.filter(author=user_profile, user=request.user).count():
            following = True
    return render(request, "profile.html", {'profile':user_profile,
                                            'page':page,
                                            'paginator':paginator,
                                            'following':following,
                                            'follower_count':follower_count,
                                            'following_count':following_count})

@login_required
def post_edit(request, username, post_id):
    title = 'Редактировать'
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        if request.method == "POST":
            form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.pub_date = timezone.now()
                post.save()
                return redirect('post', post_id=post.pk, username=username)
        else:
            form = PostForm(instance=post)
    else:
        return redirect('post', post_id=post.pk, username=post.author)
    return render(request, "new_post.html", {'form': form, 'title':title, 'post':post})

@login_required
def post_delete(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        post.delete()
        return redirect('profile', username=username)
    return redirect('post', post_id=post.pk, username=post.author)

def page_not_found(request, exception): # noqa, pylint: disable=unused-argument
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)

def server_error(request):
    return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post', post_id=post_id, username=username)
    return redirect('post', post_id=post_id, username=username)

@login_required
def follow_index(request):
    follow_page = True
    following = False
    if Favorite.objects.filter(user=request.user).count():
        favorites = Favorite.objects.filter(user=request.user).select_related('author')
        favorite_authors = []
        for item in favorites:
            favorite_authors.append(item.author.id)
        post_list = Post.objects.filter(author__in=favorite_authors).\
                                select_related('group', 'author').\
                                annotate(comment_count=Count('commented_post')).\
                                order_by("-pub_date").all()
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        following = True
        return render(request, "follow.html", {'page': page,
                                               'paginator': paginator,
                                               'following': following,
                                               'follow_page':follow_page})
    return render(request, "follow.html", {'following':following, 'follow_page':follow_page})

@login_required
def profile_follow(request, username):
    followed_author = get_object_or_404(User, username=username)
    if followed_author == request.user:
        return redirect('profile', username=username)
    Favorite.objects.create(author=followed_author, user=request.user)
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    followed_author = get_object_or_404(User, username=username)
    follover = Favorite.objects.filter(author=followed_author, user=request.user)
    follover.delete()
    return redirect('profile', username=username)
