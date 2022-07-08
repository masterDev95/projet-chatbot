from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from chatbot.chatbot import Chatbot
from chatbot.models import Conversation, Message

# Create your views here.

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def chatbot(request: HttpRequest):
    cb = Chatbot()
    if request.POST:
        user_msg = Message()
        user_msg.sender = request.POST.get('sender')
        user_msg.text = request.POST.get('text')
    data = {}
    if is_ajax(request):
        user_msg.save()
        data['user'] = {'text': getattr(Message.objects.last(), 'text')}
        response = cb.send_msg_to_chatbot(user_msg.text)
        for t in response['text']:
            bot_msg = Message()
            bot_msg.sender = 'bot'
            bot_msg.text = t
            bot_msg.save()
        data['bot'] = {'text': response['text'], 'extra': response['extra']}
        return JsonResponse(data)
    msgs = Message.objects.all()
    return render(request, 'chatbot.html', {'msgs': msgs})
