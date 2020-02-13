from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from .models import Post, Group, User
from .forms import PostForm

def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, "index.html", {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})

@login_required
def new_post(request):
    title = 'Опубликовать'
    if request.method == 'POST':
        form = PostForm(data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post', post_id=post.pk, username=post.author)
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form, 'title':title})

def post_view(request, post_id, username):
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author=user_profile).count()
    return render(request, 'post_view.html', {'post':post, 'profile':user_profile, 'post_count':post_count})

def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user_profile).order_by("-pub_date")
    post_count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {'profile':user_profile, 'post_count':post_count, 'page':page, 'paginator':paginator})

@login_required
def post_edit(request, username, post_id):
    title = 'Редактировать'
    post = get_object_or_404(Post, pk=post_id)
    user_profile = request.user
    if user_profile.username == username:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = user_profile
                post.pub_date = timezone.now()
                post.save()
                return redirect('post', post_id=post.pk, username=post.author)
        else:
            form = PostForm(instance=post)
    else:
        return HttpResponseForbidden()
    return render(request, "new_post.html", {'form': form, 'title':title})
