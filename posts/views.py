from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm

def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post', post_id=post.pk, username=post.author)
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def view_post(request, post_id, username):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'view_post.html', {'post':post, 'profile':profile})
