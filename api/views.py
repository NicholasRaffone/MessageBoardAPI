from rest_framework import viewsets, status
from .models import Post
from .serializer import PostSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
