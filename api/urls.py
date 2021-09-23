from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import PostViewSet
from .views import CommentViewSet

router = routers.DefaultRouter()
router.register('posts', PostViewSet)
router.register('comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
