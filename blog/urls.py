# blog/urls.py
from django.urls import path

from . import views
from .views import post_list, post_detail, MessageUpdateView, MessageDeleteView, CategoryListCreateView, \
    TagListCreateView, PostListView
from .sse import sse_view

urlpatterns = [
    path('', post_list, name='post-list'),
    path('p/', views.PostListView.as_view()),
    path('post/', views.PostCreateAPIView.as_view()),
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('tags/', TagListCreateView.as_view(), name='tag-list'),
    path('posts/', PostListView.as_view(), name='post-list'),  # Спи
    path('posts/<int:post_id>/', post_detail, name='post-detail'),  # Детальный просмотр поста

    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-create'),
    path('events/', sse_view, name='sse'),  # SSE для уведомлений
    path('messages/', views.MessageListView.as_view(), name='message-list'),  # Просмотр сообщений
    path('messages/new/', views.MessageCreateView.as_view(), name='message-create'),  # Отправка сообщения
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message-update'),  # Обновление сообщения
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message-delete'),  # Удаление сообщения

]
