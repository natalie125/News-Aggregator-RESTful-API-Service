from django.urls import path
from .views import login_view, logout_view, StoriesView, DeleteStoryView

urlpatterns = [
    path('api/login', login_view, name='api-login'),
    path('api/logout', logout_view, name='api-logout'),
    path('api/stories', StoriesView.as_view(), name='stories'),  # Handles both GET and POST requests
    path('api/stories/<int:key>/', DeleteStoryView.as_view(), name='delete_story'),
]
