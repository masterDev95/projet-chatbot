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