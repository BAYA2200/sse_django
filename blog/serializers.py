# blog/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Comment, Message, Category, Tag


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    replies = serializers.SerializerMethodField()  # Поле для получения всех ответов на комментарий

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'text', 'parent', 'replies', 'created_at']

    def get_replies(self, obj):
        replies = obj.replies.all()  # Получаем все ответы
        return CommentSerializer(replies, many=True).data  # Рекурсивная сериализация ответов




class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')  # Отправитель — только для чтения
    receiver = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')  # Получатель указывается по username

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'text', 'created_at', 'is_read']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class PostSerializer(serializers.ModelSerializer):
    # category = CategorySerializer()  # Вложенный сериализатор для категории
    # tags = TagSerializer(many=True)  # Вложенный сериализатор для тегов
    # comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'category', 'tags', 'created_at']
        # read_only_fields = ['author', ]