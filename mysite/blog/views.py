from django.db.models import Count
from django.db.models.functions import Greatest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.contrib.postgres.search import TrigramSimilarity
from taggit.models import Tag
from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            A = 1.0
            B = 0.4
            results = Post.published.annotate(
                similarity=(A/(A+B) * TrigramSimilarity('title', query) +
                            B/(A+B) * TrigramSimilarity('body', query)
                            ),
            ).filter(similarity__gt=0.03).order_by('-similarity')
    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results})


class PostDetailView(View):
    def get(self, request, year, month, day, post):
        post = get_object_or_404(Post, slug=post,
                                 status='published',
                                 publish__year=year,
                                 publish__month=month,
                                 publish__day=day)
        comments = post.comments.filter(active=True)
        comment_form = CommentForm()

        # List of similar posts
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                            .order_by('-same_tags', '-publish')[:4]

        return render(request, 'blog/post/detail.html',
                      {'post': post,
                       'comments': comments,
                       'comment_form': comment_form,
                       'similar_posts': similar_posts})

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
