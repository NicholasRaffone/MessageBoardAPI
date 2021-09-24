from rest_framework import serializers
from .models import Post
from .models import Comment
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'text', 'is_admin', 'date', 'xpos', 'ypos', 'color')
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'text', 'is_admin', 'date', 'post')
