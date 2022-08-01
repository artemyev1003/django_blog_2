from django.urls import path
from .views import PostDetailView, ShareView, SuccessView, post_list, post_search
from .feeds import LatestPostFeed


app_name = 'blog'

urlpatterns = [
    # path('', PostListView.as_view(), name='post_list'),
    path('', post_list, name='post_list'),
    path('tag/<slug:tag_slug>', post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/share/', ShareView.as_view(), name='post_share'),
    path('success/', SuccessView.as_view(), name='success'),
    path('feed/', LatestPostFeed(), name='post_feed'),
    path('search/', post_search, name='post_search'),
]
