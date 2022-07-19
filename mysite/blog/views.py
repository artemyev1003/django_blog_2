from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


class PostDetailView(View):
    def get(self, request, year, month, day, post):
        post = get_object_or_404(Post, slug=post,
                                     status='published',
                                     publish__year=year,
                                     publish__month=month,
                                     publish__day=day)
        comments = post.comments.filter(active=True)
        comment_form = CommentForm()
        return render(request, 'blog/post/detail.html',
                      {'post': post,
                       'comments': comments,
                       'comment_form': comment_form})

    def post(self, request, year, month, day, post):
        post = get_object_or_404(Post, slug=post,
                                     status='published',
                                     publish__year=year,
                                     publish__month=month,
                                     publish__day=day)
        comments = post.comments.filter(active=True)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return HttpResponseRedirect(request.path)
        return render(request, 'blog/post/detail.html',
                      {'post': post,
                       'comments': comments,
                       'comment_form': comment_form})


class ShareView(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, status='published')
        form = EmailPostForm()
        return render(request, 'blog/post/share.html', {'post': post,
                                                        'form': form})

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, status='published')
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']} comment: {cd['comment']}"
            send_mail(subject, message, 'artemyev93@gmail.com', [cd['to']])
            return HttpResponseRedirect(reverse('blog:success'))
        return render(request, 'blog/post/share.html', {'post': post,
                                                        'form': form})


class SuccessView(View):
    def get(self, request):
        return render(request, 'blog/post/success.html')
