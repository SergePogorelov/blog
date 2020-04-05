from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail

from .forms import EmailPostForm
from .models import Post


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3) #3 posts on 1 page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page' : page, 'posts' : posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {'post' : post})


class PostListView(ListView):

    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            comments = form.cleaned_data['comments']
            to = form.cleaned_data['to']
            #...send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(name, email, post.title)
            if comments:
                message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, name, comments)
            else:
                message = 'Read "{}" at {}\n'.format(post.title, post_url, name)
            send_mail(subject, message, 'admin@myblog.com', [to])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post' : post, 'form' : form, 'sent' : sent})