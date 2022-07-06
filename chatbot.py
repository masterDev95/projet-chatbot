import random
import json
import pickle
import numpy
import time

import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())
pbs = json.loads(open('resolutionpb.json').read())

words = pickle.load(open('words.pk1', 'rb'))
classes = pickle.load(open('classes.pk1', 'rb'))
model = load_model('chatbotmodel.h5')
last_question_tag = '' # Sera la dernière question posé par le bot
pb_resolu_count = 0
wait = False
end = False

def clean_up_sentence(sentence):    
    sentence_words = nltk.word_tokenize(sentence) # diviser les mots dans un tableau 
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words] # créer une forme courte pour chaque mot
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence) # identifier les mots
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = i # attribuer 1 si le mot courant est dans la position de vocabulaire
    return numpy.array(bag) # retourner le tableau des sacs de mots : 0 ou 1 pour chaque mot du sac qui existe dans la phrase

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(numpy.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])}) # trier par force de probabilité
    return return_list

def get_response(intents_list, intents_json):
    global last_question_tag
    global wait
    global pb_resolu_count
    global end
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']    

    # Parcours de la liste d'intention
    for i in list_of_intents:
        # On a trouvé l'intention
        if i['tag'] == tag:
            # Si la dernière réponse met fin à la conversation
            if 'end' in i.keys():
                end = True
            # Si on attend une suite de question
            if 'follow' in i.keys():
                last_question_tag = tag
            # Si l'intention est une affirmation ou une negation
            if 'ouiNon' in i.keys():
                # Si l'on vient d'une question du bot
                # pour savoir si le pb est resolu
                if wait:
                    if tag == 'reponseUtilisateurAffirmative':
                        if 'end' in i['wait'].keys():
                            end = True
                        #Selectionne aléatoirement un élément parmit la liste
                        return random.choice(i['wait']['responses'])
                    # Selon le niveau de conversation un objet "wait" différent sera sélectionner
                    wait_string = 'wait'+str(pb_resolu_count)
                    wait = False
                    # Si la conversation est cloturé car pas de réponse (appel d'un assistant)
                    if 'end' in i[wait_string].keys():
                        end = True
                    # Si on est dans un cas ou on doit attendre le bot lancera un message avec une attente de 5 secs
                    if 'wait' in i[wait_string].keys():
                        return resolution_pb_wait[wait_string]['wait'], (i[wait_string]['pb'])
                    # Dans le cas ou il n'y a pas d'attente ou de cloture de conversation le bot répond aléatoire en rapport avec la derniere demande de l'utilisateur
                    return random.choice(i[wait_string]['responses'])
                if 'end' in i[last_question_tag].keys():
                    end = True
                # Attendre 5 secondes et demander si le pbm est résolu
                if 'wait' in i[last_question_tag].keys():
                    if 'emptyPb' in i[last_question_tag]:
                        return resolution_pb_wait(i[last_question_tag]['wait'])
                    return resolution_pb_wait(i[last_question_tag]['wait'], i[last_question_tag]['pb'])
                # Dans le cas ou i n'y a pas de wait renvoyer une réponse aléatoire en rapport avec la derniere demande
                return random.choice(i[last_question_tag]['responses'])
            # Le bot attend 5 secondes puis renvoie un message
            if 'wait' in i.keys():
                return resolution_pb_wait(i['wait'], i['pb'])
            return random.choice(i['responses'])

# Fonction résolution qui a pour parametre un problème précis (attente en cas de relance)
def resolution_pb_wait(wait_inc, pb_name=None):
    global wait
    global pb_resolu_count
    global pbs
    
    # Si le problème a pas de nom attendre sinon mettre la solution du problème
    if pb_name != None:
        for p in pbs['pbs']:
            if p['name'] == pb_name:
                print(p['response'])

    # Variable pour la solution souhaitée
    pb_resolu_count += wait_inc
    #Attendre de 5 secondes
    time.sleep(5)
    # Variable requise pour l'attente des 5 secondes et sa réponse
    wait = True
    # Message apres les 5 secondes
    return 'Avez-vous résolu votre problème?'

#Message de départ
print('Bonjour!')

# Mettre tout le texte entrée par l'utilisateur en minuscule
# Variable entrée utilisateur et la réponse du bot
while True:
    message = input('> ').lower()
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(res)
    if end: quit()