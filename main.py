# coding=utf8
from flask import Flask
from flask import render_template
from flask import request

import speech_recognition as sr

app = Flask(__name__,
        static_url_path='', 
        static_folder='static')

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/text/<text>", methods=["GET", "POST"])
def translateBraille(text):
    outputBraille = ""
    text = text.lower()
    brailleDict = {
        "a": "⠁", "b": "⠃", "c": "⠉", "d": "⠙",
        "e": "⠑", "f": "⠋", "g": "⠛", "h": "⠓",
        "i": "⠊", "j": "⠚", "k": "⠅", "l": "⠇",
        "m": "⠍", "n": "⠝", "o": "⠕", "p": "⠏",
        "q": "⠟", "r": "⠗", "s": "⠎", "t": "⠞",
        "u": "⠥", "v": "⠧", "w": "⠺", "x": "⠭",
        "y": "⠽", "z": "⠵", "0": "⠚", "1": "⠁",
        "2": "⠃", "3": "⠉", "4": "⠙", "5": "⠑",
        "6": "⠋", "7": "⠛", "8": "⠓", "9": "⠊",
        ",": "⠂", ";": "⠆", ":": "⠒", ".": "⠲",
        "?": "⠦", "!": "⠖", "‘": "⠄", "“": "⠄⠶",
        "“": "⠘⠦", "”": "⠘⠴", "‘": "⠄⠦", "’": "⠄⠴",
        "(": "⠐⠣", ")": "⠐⠜", "/": "⠸⠌", "\\": "⠸⠡",
        "-": "⠤", " ": " ", "%": "⠨⠴", "@": "⠈⠁", "$": "⠈⠎"
    }
    isNumber = False
    quoteLocation = -1
    try:
        for i in text:
            if i == '"':
                if quoteLocation == -1:
                    quoteLocation = len(outputBraille)
                    outputBraille += "⠠⠶"
                else:
                    tempOutput = list(outputBraille)
                    tempOutput[quoteLocation] = ""
                    tempOutput[quoteLocation + 1] = "⠦"
                    tempOutput.append("⠴")
                    outputBraille = "".join(tempOutput)
                continue
            if i.isdigit() and isNumber:
                outputBraille += brailleDict[i]
            elif i.isdigit():
                isNumber = True
                outputBraille += "⠼"
                outputBraille += brailleDict[i]
            elif isNumber:
                isNumber = False
                if i == " ":
                    outputBraille += " "
                else:
                    outputBraille += "⠰"
                    outputBraille += brailleDict[i]
            else:
                outputBraille += brailleDict[i]
    except:
        return "Text contains character that is not recognised."
    return outputBraille

@app.route("/speech", methods=["GET", "POST"])
def speechToText():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        r = sr.Recognizer()
        test = sr.AudioFile(f.filename)
        with test as source:
            audio = r.record(source)
            return translateBraille(r.recognize_google(audio))

if __name__ == "__main__":
    app.run(debug=True)