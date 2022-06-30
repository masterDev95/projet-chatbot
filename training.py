import random
import json
import pickle
import numpy


import nltk as nl
nl.download('punkt')
nl.download('wordnet')
nl.download('omw-1.4')
from nltk.stem import WordNetLemmatizer

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD

intents = json.loads(open('JeuDeDonne.json').read())

# servira pour les différentes morphologies de chaque mots
lemmatizer = WordNetLemmatizer()

# listes
words = [] # pour chaque mots
classes = [] # pour chaque classe de mots
documents = []
ignore_letters = ['?', '!', '.', ',']

# parcourir avec une boucle For toutes les intentions
# tokéniser chaque pattern et ajouter les tokens à la liste words, les patterns et
# le tag associé à l'intention sont ajoutés aux listes correspondantes
for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nl.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        
        # ajouter le tag aux classes s'il n'est pas déjà là 
        if intent['tag'] not in classes:
            classes.append(intent['tag'])
        
# lemmatiser tous les mots du vocabulaire et les convertir en minuscule
# si les mots n'apparaissent pas dans la ponctuation    
words = [lemmatizer.lemmatize(word)
         for word in words if word not in ignore_letters]
words = sorted(set(words))

print(words)
