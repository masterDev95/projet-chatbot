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