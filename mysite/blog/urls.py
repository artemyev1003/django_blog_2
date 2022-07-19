from django.urls import path
from .views import PostListView, PostDetailView, ShareView, SuccessView


app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/share/', ShareView.as_view(), name='post_share'),
    path('success/', SuccessView.as_view(), name='success'),
]
