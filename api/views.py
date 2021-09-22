from rest_framework import viewsets, status
from .models import Post
from .serializer import PostSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import hashlib

'''
TODO:
    Make request for when post is flagged
        - send an email? probs good for notification, implement google smth
        - Make sure start month in react is set and count up
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
        if all([key in request.data.keys() for key in keys]) and all([request.data[key].isdigit() for key in request.data.keys()]):
            posts = Post.objects.filter(date__year=int(request.data['year']),date__month=int(request.data['month']))
            return Response({'posts':[PostSerializer(post).data for post in posts]}, status=status.HTTP_200_OK)
        return Response({'body':'not found'}, status=status.HTTP_404_NOT_FOUND)
