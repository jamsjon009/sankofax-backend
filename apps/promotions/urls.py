from django.urls import path
from .views import (
    StoryPackageListView, StorySubmissionListCreateView, StorySubmissionDetailView,
)

urlpatterns = [
    path('promotions/packages/', StoryPackageListView.as_view(), name='promotion-packages'),
    path('promotions/submissions/', StorySubmissionListCreateView.as_view(), name='promotion-submissions'),
    path('promotions/submissions/<str:reference>/', StorySubmissionDetailView.as_view(), name='promotion-submission-detail'),
]
