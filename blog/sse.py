# blog/sse.py
import time
from django.http import StreamingHttpResponse, HttpResponse


# Генератор событий для SSE
from blog.models import Notification, Message


def event_stream(user):
    while True:
        notifications = Notification.objects.filter(user=user, is_read=False)
        if notifications.exists():
            for notification in notifications:
                yield f"data: {notification.message}\n\n"
                notification.is_read = True  # Помечаем как прочитанное
                notification.save()  # Сохраняем в базе
        time.sleep(1)  # Пауза между проверками


def message_stream(request):
    def event_stream():
        while True:
            unread_messages = Message.objects.filter(receiver=request.user, is_read=False)
            if unread_messages.exists():
                for message in unread_messages:
                    yield f"data: Новое сообщение от {message.sender.username}\n\n"
                    message.is_read = True
                    message.save()
            time.sleep(1)  # Проверяем новые сообщения каждые 1 секунду

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

# Представление для SSE
def sse_view(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    return StreamingHttpResponse(event_stream(request.user), content_type='text/event-stream')

# Функция для уведомления автора поста
def notify_author(author):
    Notification.objects.create(user=author, message="У вас новый комментарий!")


from .models import Notification

def notify_comment_author(author):
    # Создаем уведомление для автора комментария
    Notification.objects.create(user=author, message="У вас новый ответ на комментарий!")

def notify_post_author(author):
    # Создаем уведомление для автора поста
    Notification.objects.create(user=author, message="У вас новый комментарий на пост!")

