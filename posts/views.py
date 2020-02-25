from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm

def index(request):
    post_list = Post.objects.select_related('author').order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, "index.html", {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).select_related('author').order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page, 'paginator': paginator})

@login_required
def new_post(request):
    title = 'Опубликовать'
    if request.method == 'POST':
        form = PostForm(data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
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
    if request.user == post.author:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
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
