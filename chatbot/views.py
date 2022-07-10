from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from chatbot.chatbot import Chatbot
from django.views.decorators.http import require_http_methods

def is_ajax(request: HttpRequest):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

# @require_http_methods(["POST"])
def chatbot(request: HttpRequest):
    cb = Chatbot()
    data = {}

    # L'utilisateur envoie un msg au chatbot (côté front)
    if request.POST:
        # Nécessaire pour les futures questions
        cb.last_question_tag = request.POST.get('last_question_tag')
        cb.pb_resolu_count = int(request.POST.get('pb_resolu_count'))
        if request.POST.get('wait') == 'true':
            cb.wait = True
        else:
            cb.wait = False

        # Requête Ajax pour l'actualisation du chatbot
        if is_ajax(request):
            # Envoie du msg au chatbot (côté back)
            response = cb.send_msg_to_chatbot(request.POST.get('text'))

            # Renvoie des données nécessaire à l'actualisation
            data['user'] = {'text': request.POST.get('text')}
            data['bot'] = {'text': response['text'], 'extra': response['extra']}
            data['vars'] = {'last_question_tag': response['last_question_tag'],
                            'pb_resolu_count': response['pb_resolu_count'], 'wait': response['wait']}
            return JsonResponse(data)

    return render(request, 'chatbot.html')
