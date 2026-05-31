from django.urls import path
from .views import MeView, RegisterView, UserSearchView

urlpatterns = [
    path('me/', MeView.as_view()),
    path('register/', RegisterView.as_view()),
    path('search/', UserSearchView.as_view()),
]
