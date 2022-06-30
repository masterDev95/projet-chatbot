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
    return sentence_words   # retourner le tableau des sacs de mots : 0 ou 1 pour chaque mot du sac qui existe dans la phrase



