from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import generics, serializers, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from blog.filter import PostFilter
from blog.models import Post, Comment, Message, Category, Tag
from blog.serializers import PostSerializer, CommentSerializer, MessageSerializer, CategorySerializer, TagSerializer
from blog.sse import notify_comment_author, notify_post_author


class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]
    filterset_fields = ['category', 'tags']
    filterset_class = PostFilter
    search_fields = ['title', ]


class PostCreateAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.request.data.get('post'))
        parent_id = self.request.data.get('parent')  # Получаем ID родительского комментария
        parent = None

        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)

            # Проверка, что пользователь не отвечает на свой собственный комментарий
            if parent.author == self.request.user:
                raise serializers.ValidationError("Вы не можете отвечать на свой собственный комментарий.")

        comment = serializer.save(author=self.request.user, post=post, parent=parent)

        # Уведомляем автора родительского комментария, если это ответ
        if parent:
            notify_comment_author(parent.author)

        # Уведомляем автора поста
        notify_post_author(post.author)

class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer


# Представление для детального просмотра поста
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post_detail.html', {'post': post})


# Представление для главной страницы с постами
def post_list(request):
    posts = Post.objects.all().prefetch_related('comments')
    return render(request, 'post_list.html', {'posts': posts})


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Возвращаем все сообщения, отправленные или полученные текущим пользователем
        return Message.objects.filter(receiver=self.request.user) | Message.objects.filter(sender=self.request.user)


# Отправка нового сообщения
from rest_framework import generics, serializers, permissions
from django.contrib.auth.models import User


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Устанавливаем отправителя сообщения как текущего пользователя
        serializer.save(sender=self.request.user)


class MessageUpdateView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        message = self.get_object()

        # Проверяем, что только отправитель может обновить сообщение
        if message.sender != self.request.user:
            raise PermissionDenied("Вы не можете редактировать чужое сообщение.")

        serializer.save()


class MessageDeleteView(generics.DestroyAPIView):
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        # Проверяем, что только отправитель или получатель могут удалить сообщение
        if instance.sender != self.request.user and instance.receiver != self.request.user:
            raise PermissionDenied("Вы не можете удалить это сообщение.")

        instance.delete()


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer