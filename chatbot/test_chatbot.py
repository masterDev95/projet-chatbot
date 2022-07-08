from cgi import print_environ
import json
import unittest
import chatbot

intents = json.loads(open('jeuDeDonne.json').read())['intents']
pbs = json.loads(open('resolutionpb.json').read())['pbs']

class TestChatbot(unittest.TestCase):
    
    def test_demarrage_camera(self):
        message = 'I have a problem with my camera'
        ints = chatbot.predict_class(message)
        res = chatbot.get_response(ints, chatbot.intents)
        self.assertEqual(res[0], 'Have you activated your camera first?')
        
    def test_pb_activation_camera(self):
        response = ''
        for p in pbs:
            if p['name'] == 'activationCamera':
                response = p['response']
        message = 'Where is the activation of the camera?'
        ints = chatbot.predict_class(message)
        res = chatbot.get_response(ints, chatbot.intents)
        self.assertEqual(res[0], response)
        
    def test_pb_windows_10_camera(self):
        response = ''
        for p in pbs:
            if p['name'] == 'utilitaireResoPbCameraWindows10':
                response = p['response']
        message = 'My PC is on Windows 10'
        ints = chatbot.predict_class(message)
        res = chatbot.get_response(ints, chatbot.intents)
        self.assertEqual(res[0], response)
        
        
if __name__ == '__main__':
    unittest.main()
