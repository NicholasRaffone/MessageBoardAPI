from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import PostViewSet

router = routers.DefaultRouter()
router.register('posts', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
