from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtCore import QThread, pyqtSignal
import speech_recognition as sr
from playsound import playsound
import pygame as pg
import datetime
import random
import openai
import gtts
import time
import sys
import os

#init recognizer and chatgpt api
speech = sr.Recognizer()
openai.api_key = "Yourapi key"
model_engine = "text-davinci-003"

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        #init
        super(Ui, self).__init__()
        uic.loadUi("ui.ui", self)
        self.show()
        
        #find all radiobuttons and buttons in ui.ui
        radiobutton1 = self.findChild(QtWidgets.QRadioButton, "radioButton")
        radiobutton2 = self.findChild(QtWidgets.QRadioButton, "radioButton_2")
        self.button = self.findChild(QtWidgets.QPushButton, "pushButton")
        self.button.clicked.connect(self.EnterPressed)
        self.button = self.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.button.clicked.connect(self.History)
        
        #language radiobutton
        radiobutton1.setChecked(True)
        radiobutton1.toggled.connect(self.Ua)
        radiobutton2.toggled.connect(self.En)
        
        #logo
        pixmap = QPixmap("icon.webp")
        self.icon.setScaledContents(True)
        self.icon.setPixmap(pixmap)
        self.icon.resize(135, 130)
        
        #text for an error and language
        self.lang1 = "uk"
        self.language1 = "uk-UK"
        self.al_uk = ["Я вас не зрозуміла", "Я вас не розумію", "Я вас не чую"]
        self.s_uk = "Говоріть"
        self.q_lang = "(Відповідай Українською мовою)"
        
        #reset all progress bars
        self.progressBar.setValue(0)
        self.progressBar_2.setValue(0)
        self.progressBar_3.setValue(0)
        self.progressBar_5.setValue(0)
        
        self.play_thread = PlayThread(self)
        
    def Ua(self):
        #text for an error and language
        self.lang1 = "uk"
        self.language1 = "uk-UK"
        self.al_uk = ["Я вас не зрозуміла", "Я вас не розумію", "Я вас не чую"]
        self.s_uk = "Говоріть"
        self.q_lang = "(Відповідай Українською мовою)"
        
    def En(self):
        #text for an error and language
        self.s_uk = "Speak"
        self.lang1 = "en"
        self.language1 = "en-En"
        self.al_uk = ["I did'nt understand", "I don't understand you", "I dont hear you"]
        self.q_lang = "(answer in english language)"
    
    def History(self):
        if os.path.exists("history.txt"):
            self.textEdit.clear()
            history_file = open("history.txt", "r")
            data = history_file.read()
            self.textEdit.append(data)
            history_file.close()
        else:
            pass
    
    def EnterPressed(self):
        #delete temp audio file
        if os.path.exists("temp.mp3"):
            os.remove("temp.mp3")
        
        #reset all progress bars
        self.progressBar.setValue(0)
        self.progressBar_2.setValue(0)
        self.progressBar_3.setValue(0)
        self.progressBar_5.setValue(0)
        
        time.sleep(1)
        
        try:
            with sr.Microphone(device_index=0) as source:
                time.sleep(1)
                wait = gtts.gTTS(self.s_uk, lang=self.lang1, slow = False)
                wait.save("temp.mp3")
                playsound("temp.mp3")
                if os.path.exists("temp.mp3"):
                    os.remove("temp.mp3")
                audio = speech.listen(source)
        
            query = speech.recognize_google(audio, language=self.language1)
            completion = openai.Completion.create(engine=model_engine, prompt=query + self.q_lang, max_tokens=2648, n=1, stop=None, temperature=0.5)
            date_string = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
            
            self.textEdit.append("\n\n"+date_string)
            self.textEdit.append(" You:  \n" + query)
            print("\n\n You:\n", query)
            
            response = completion.choices[0].text
            
            print("\n\n Bot:\n", response)
            self.textEdit.append("\n Bot:  " + response)
            
            sound = gtts.gTTS(response, lang=self.lang1)
            sound.save("temp.mp3")

            self.play_thread.play_audio("temp.mp3")
        
            history = open("history.txt", "a+")
            history.write("\n\n" + date_string)
            history.write("\n You:  \n" + query)
            history.write("\n Bot:" + response)
            history.close()
            time.sleep(1.2)
        
        except Exception:
            time.sleep(0.8)
            err = gtts.gTTS(random.choice(self.al_uk), lang=self.lang1)
            err.save("temp.mp3")
            playsound("temp.mp3")
            if os.path.exists("temp.mp3"):
                os.remove("temp.mp3")
            
class PlayThread(QThread):
    play_finished = pyqtSignal()

    def __init__(self, parent):
        super(PlayThread, self).__init__()
        self.parent = parent
        self.audio_path = ""

    def play_audio(self, audio_path):
        self.audio_path = audio_path
        self.start()

    def run(self):
        try:
            pg.mixer.init()
            pg.mixer.music.load(self.audio_path)
            pg.mixer.music.play()

            while pg.mixer.music.get_busy():
                self.parent.progressBar.setValue(random.randint(0, 100))
                self.parent.progressBar_2.setValue(random.randint(0, 100))
                self.parent.progressBar_3.setValue(random.randint(0, 100))
                self.parent.progressBar_5.setValue(random.randint(0, 100))
                time.sleep(0.2)

            pg.mixer.quit()
            self.play_finished.emit()
            if os.path.exists("temp.mp3"):
                os.remove("temp.mp3")
        
            #reset all progress bars
            self.parent.progressBar.setValue(0)
            self.parent.progressBar_2.setValue(0)
            self.parent.progressBar_3.setValue(0)
            self.parent.progressBar_5.setValue(0)
        except Exception:
            pass

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
