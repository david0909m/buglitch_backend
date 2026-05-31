from rest_framework.routers import DefaultRouter

from .views import IssueViewSet, NotificationViewSet


router = DefaultRouter()

router.register(
    r'issues',
    IssueViewSet,
    basename='issues'
)

router.register(
    r'notifications',
    NotificationViewSet,
    basename='notifications'
)

urlpatterns = router.urls
