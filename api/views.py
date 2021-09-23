from rest_framework import viewsets, status
from .models import Post
from .models import Comment
from .serializer import PostSerializer
from .serializer import CommentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import hashlib

'''
TODO:
    Make request for when post is flagged
        - send an email? probs good for notification, implement google smth

    Make sure start month in react is set and count up

    Make Comments
        - Flag comment -> same as flag comment
        - Get Comments from post id
'''
hashval = '20f0cfdc8935408bb8940b47de8838a8da6fa20c98b4931fefcb59febdb23976f8b1239706b70219b46d65945fc4b6620a97dd028faf7ae2a79dfe915912cb44'

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    @action(detail=False, methods=['POST'])
    def make_post(self, request):
        is_admin = False
        token = "Token" in request.headers and request.headers["Token"]
        if token:
            hashed = hashlib.sha512(token.encode()).hexdigest()
            is_admin = (hashed == hashval)
        if all([key in request.data.keys() for key in ['title','text','xpos','ypos','color']]):
            p = Post(
                title=request.data['title'],
                text=request.data['text'],
                is_admin=is_admin,
                xpos=request.data['xpos'],
                ypos=request.data['ypos'],
                color=request.data['color']
            )
            p.save()
        else:
            return Response({'body':'not all values submitted'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PostSerializer(p).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['DELETE'])
    def remove_post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            token = "Token" in request.headers and request.headers["Token"]
            if token:
                hashed = hashlib.sha512(token.encode()).hexdigest()
                if hashed==hashval:
                    post.delete()
                    return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
            return Response({'body':'invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Post.DoesNotExist:
            return Response({'body':'not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'])
    def get_posts_month(self, request):
        keys = ['month','year']
        if all([key in request.data.keys() for key in keys]) and all([request.data[key].isdigit() for key in keys]):
            posts = Post.objects.filter(date__year=int(request.data['year']),date__month=int(request.data['month']))
            return Response({'posts':[PostSerializer(post).data for post in posts]}, status=status.HTTP_200_OK)
        return Response({'body':'not found'}, status=status.HTTP_404_NOT_FOUND)

class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @action(detail=False, methods=['POST'])
    def make_comment(self,request):
        if all([key in request.data.keys() for key in ['text','post']]):
            try:
                post = Post.objects.get(pk=request.data['post'])
            except (Post.DoesNotExist, ValueError):
                return Response({'body':'post not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            is_admin = False
            token = "Token" in request.headers and request.headers["Token"]
            if token:
                hashed = hashlib.sha512(token.encode()).hexdigest()
                is_admin = (hashed == hashval)
            c = Comment(
                text=request.data['text'],
                is_admin=is_admin,
                post=post
            )
            c.save()
        else:
            return Response({'body':'not all values submitted'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CommentSerializer(c).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'])
    def remove_comment(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            token = "Token" in request.headers and request.headers["Token"]
            if token:
                hashed = hashlib.sha512(token.encode()).hexdigest()
                if hashed==hashval:
                    comment.delete()
                    return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)
            return Response({'body':'invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Comment.DoesNotExist:
            return Response({'body':'not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'])
    def get_comments_post(self, request):
        keys = ['post']
        if all([key in request.data.keys() for key in keys]) and all([request.data[key].isdigit() for key in keys]):
            try:
                post = Post.objects.get(pk=request.data['post'])
            except (Post.DoesNotExist, ValueError):
                return Response({'body':'post not found'}, status=status.HTTP_400_BAD_REQUEST)
            comments = Comment.objects.filter(post=post.id)
            return Response({'comments':[CommentSerializer(comment).data for comment in comments]}, status=status.HTTP_200_OK)
        return Response({'body':'not found'}, status=status.HTTP_404_NOT_FOUND)
