from django.urls import path
from .views import BlogPostListView, BlogPostDetailView, BlogCategoryListView

urlpatterns = [
    path('blog/', BlogPostListView.as_view(), name='blog-list'),
    path('blog/categories/', BlogCategoryListView.as_view(), name='blog-categories'),
    path('blog/<slug:slug>/', BlogPostDetailView.as_view(), name='blog-detail'),
]