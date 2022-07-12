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
from keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD

intents = json.loads(open('static/JeuDeDonne.json').read())

# servira pour les différentes morphologies de chaque mots
lemmatizer = WordNetLemmatizer()

# listes
words = [] # pour chaque mots
classes = [] # pour chaque classe de mots
documents = [] # documents associants classes et mots
ignore_letters = ['?', '!', '.', ','] # charactères à ignorer

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
classes = sorted(set(classes))

# on garde les mots et classes dans un fichier
pickle.dump(words, open('words.pk1', 'wb'))
pickle.dump(classes, open('classes.pk1', 'wb'))

# liste pour le jeu de données
training = []
output_empty = [0] * len(classes)

# création du modèle du jeu de données
for document in documents:
    bow = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(
        word.lower()) for word in word_patterns]
    for word in words:
        bow.append(1) if word in word_patterns else bow.append(0)
        
    # association du pattern à la classe correspondante
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bow, output_row])
    
# mélange du jeu de données et convertion en array
random.shuffle(training)
training = numpy.array(training)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

# définition du modèle du Deep Learning
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# compilation du modèle en SGD
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
print(model.summary())

# training du modèle et sauvegarde
hist = model.fit(numpy.array(train_x), numpy.array(train_y), epochs=200, verbose=1)
model.save('chatbotmodel.h5', hist)
