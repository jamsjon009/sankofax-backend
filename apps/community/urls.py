from django.urls import path
from .views import (
    ForumCategoryListView, ThreadListCreateView, ThreadDetailView, ReplyListCreateView,
)

urlpatterns = [
    path('community/categories/', ForumCategoryListView.as_view(), name='forum-categories'),
    path('community/threads/', ThreadListCreateView.as_view(), name='forum-threads'),
    path('community/threads/<slug:slug>/', ThreadDetailView.as_view(), name='forum-thread-detail'),
    path('community/threads/<slug:slug>/replies/', ReplyListCreateView.as_view(), name='forum-thread-replies'),
]
