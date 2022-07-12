import os
import secrets
import json
import pickle
import numpy
import time

import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import load_model

from eliblue.settings import BASE_DIR, CB_DIR


class Chatbot:
    lemmatizer = WordNetLemmatizer()

    intents_data = os.path.join(CB_DIR, 'static', 'JeuDeDonne.json')
    pbs_data = os.path.join(CB_DIR, 'static', 'resolutionpb.json')
    words_data = os.path.join(CB_DIR, 'static', 'words.pk1')
    classes_data = os.path.join(CB_DIR, 'static', 'classes.pk1')
    model_data = os.path.join(CB_DIR, 'static', 'chatbotmodel.h5')

    intents = json.loads(open(intents_data).read())
    pbs = json.loads(open(pbs_data).read())

    words = pickle.load(open(words_data, 'rb'))
    classes = pickle.load(open(classes_data, 'rb'))
    model = load_model(model_data)
    last_question_tag = ''  # Sera la dernière question posé par le bot
    pb_resolu_count = 0
    wait = False
    end = False

    def clean_up_sentence(self, sentence):
        # diviser les mots dans un tableau
        sentence_words = nltk.word_tokenize(sentence)
        # créer une forme courte pour chaque mot
        sentence_words = [self.lemmatizer.lemmatize(
            word) for word in sentence_words]
        return sentence_words


    def bag_of_words(self, sentence):
        sentence_words = self.clean_up_sentence(sentence)  # identifier les mots
        bag = [0] * len(self.words)
        for w in sentence_words:
            for i, word in enumerate(self.words):
                if word == w:
                    # attribuer 1 si le mot courant est dans la position de vocabulaire
                    bag[i] = i
        # retourner le tableau des sacs de mots : 0 ou 1 pour chaque mot du sac qui existe dans la phrase
        return numpy.array(bag)


    def predict_class(self, sentence):
        bow = self.bag_of_words(sentence)
        res = self.model.predict(numpy.array([bow]), verbose=0)[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            # trier par force de probabilité
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list


    def get_response(self, intents_list, intents_json):
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']

        # Parcours de la liste d'intention
        for i in list_of_intents:
            # On a trouvé l'intention
            if i['tag'] == tag:
                # Si la dernière réponse met fin à la conversation
                if 'end' in i.keys():
                    self.end = True
                # Si on attend une suite de question
                if 'follow' in i.keys():
                    self.last_question_tag = tag
                # Si l'intention est une affirmation ou une negation
                if 'ouiNon' in i.keys():
                    # Si l'on vient d'une question du bot
                    # pour savoir si le pb est resolu
                    if self.wait:
                        if tag == 'reponseUtilisateurAffirmative':
                            if 'end' in i['wait'].keys():
                                self.end = True
                            # Selectionne aléatoirement un élément parmit la liste
                            return [secrets.choice(i['wait']['responses'])]
                        # Selon le niveau de conversation un objet "wait" différent sera sélectionner
                        wait_string = 'wait'+str(self.pb_resolu_count)
                        self.wait = False
                        # Si la conversation est cloturé car pas de réponse (appel d'un assistant)
                        if 'end' in i['waits'][self.last_question_tag][wait_string].keys():
                            self.end = True
                        # Si on est dans un cas ou on doit attendre le bot lancera un message avec une attente de 5 secs
                        if 'wait' in i['waits'][self.last_question_tag][wait_string].keys():
                            return self.resolution_pb_wait(i['waits'][self.last_question_tag][wait_string]['wait'], i['waits'][self.last_question_tag][wait_string]['pb'])
                        # Dans le cas ou il n'y a pas d'attente ou de cloture de conversation le bot répond aléatoire en rapport avec la derniere demande de l'utilisateur
                        return [secrets.choice(i['waits'][self.last_question_tag][wait_string]['responses'])]
                    if 'end' in i[self.last_question_tag].keys():
                        self.end = True
                    # Attendre 5 secondes et demander si le pbm est résolu
                    if 'wait' in i[self.last_question_tag].keys():
                        if 'emptyPb' in i[self.last_question_tag]:
                            return self.resolution_pb_wait(i[self.last_question_tag]['wait'])
                        return self.resolution_pb_wait(i[self.last_question_tag]['wait'], i[self.last_question_tag]['pb'])
                    # Dans le cas ou i n'y a pas de wait renvoyer une réponse aléatoire en rapport avec la derniere demande
                    return [secrets.choice(i[self.last_question_tag]['responses'])]
                # Le bot attend 5 secondes puis renvoie un message
                if 'wait' in i.keys():
                    if i['wait'] == True:
                        return self.resolution_pb_wait(i['wait'], i['pb'])
                if 'multiWait' in i.keys():
                    return self.resolution_pb_wait(1, i['pbs'][self.last_question_tag])
                return [secrets.choice(i['responses'])]

    # Fonction résolution qui a pour parametre un problème précis (attente en cas de relance)
    def resolution_pb_wait(self, wait_inc, pb_name=None):
        response = []

        # Si le problème a pas de nom attendre sinon mettre la solution du problème
        if pb_name != None:
            for p in self.pbs['pbs']:
                if p['name'] == pb_name:
                    response.append(p['response'])

        # Variable pour la solution souhaitée
        self.pb_resolu_count += wait_inc
        # Variable requise pour l'attente des 5 secondes et sa réponse
        self.wait = True
        response.append('Did you solve your problem?')
        return response

    def send_msg_to_chatbot(self, msg: str):
        response = {}
        response['text'] = []
        response['extra'] = ''
        msg = msg.lower()
        
        if msg == 'no' or msg == 'yes':
            if msg == 'no':
                res = self.get_response(
                    [{'intent': 'reponseUtilisateurNegative'}], self.intents)
            if msg == 'yes':
                res = self.get_response(
                    [{'intent': 'reponseUtilisateurAffirmative'}], self.intents)
        else:
            ints = self.predict_class(msg)
            res = self.get_response(ints, self.intents)
            
        i = 0
        for r in res:
            if i > 0:
                response['extra'] = 'wait'
            response['text'].append(r)
            i += 1
        if self.end: response['extra'] = 'end'
        response['last_question_tag'] = self.last_question_tag
        response['pb_resolu_count'] = self.pb_resolu_count
        response['wait'] = self.wait
        return response
