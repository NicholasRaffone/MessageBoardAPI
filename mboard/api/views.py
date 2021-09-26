from rest_framework import viewsets, status
from .models import Post
from .models import Comment
from .serializer import PostSerializer
from .serializer import CommentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import hashlib
import os
from dotenv import load_dotenv
import smtplib

load_dotenv()

'''
TODO:
    Make sure start month in react is set and count up
'''
hashval = os.getenv('HASH_VAL')
gmail_user = os.getenv('EMAIL_USER')
gmail_password = os.getenv('EMAIL_PASS')
mail_from = gmail_user
mail_to = gmail_user
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)


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
            if request.data['xpos'].isdigit() and request.data['ypos'].isdigit():
                xpos = max(min(request.data['xpos'],1400),0)
                ypos = max(min(request.data['ypos'],824),0)
            else:
                return Response({'body':'xpos and ypos have to be ints'}, status=status.HTTP_400_BAD_REQUEST)
            p = Post(
                title=request.data['title'],
                text=request.data['text'],
                is_admin=is_admin,
                xpos=xpos,
                ypos=ypos,
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

    @action(detail=False, methods=['POST'])
    def get_posts_month(self, request):
        keys = ['month','year']
        if all([key in request.data.keys() for key in keys]) and all([request.data[key].isdigit() for key in keys]):
            posts = Post.objects.filter(date__year=int(request.data['year']),date__month=int(request.data['month']))
            return Response({'posts':[PostSerializer(post).data for post in posts]}, status=status.HTTP_200_OK)
        return Response({'body':'not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def flag_post(self, request, pk):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        try:
            post = Post.objects.get(pk=pk)
            p_data = PostSerializer(post).data
            mail_subject = 'Post Has Been Flagged'
            mail_message = f'''Subject:{mail_subject}\n
                Post Information\n\n{chr(10).join(
                    f"{key}: {val}" for key,val in p_data.items()
                )}
            '''
            server.sendmail(mail_from, mail_to, mail_message)
            return Response(p_data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
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

    @action(detail=False, methods=['POST'])
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

    @action(detail=True, methods=['POST'])
    def flag_comment(self, request, pk):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        try:
            comment = Comment.objects.get(pk=pk)
            c_data = CommentSerializer(comment).data
            post = Post.objects.get(pk=c_data['post'])
            p_data = PostSerializer(post).data
            mail_subject = 'Comment Has Been Flagged'
            mail_message = f'''Subject:{mail_subject}\n
                Comment Information\n{chr(10).join(
                    f"{key}: {val}" for key,val in c_data.items()
                )}\n
                Post Information\n\n{chr(10).join(
                    f"{key}: {val}" for key,val in p_data.items()
                )}
            '''
            server.sendmail(mail_from, mail_to, mail_message)
            return Response(c_data, status=status.HTTP_200_OK)
        except (Comment.DoesNotExist, Post.DoesNotExist):
            return Response({'body':'not found'}, status=status.HTTP_404_NOT_FOUND)
