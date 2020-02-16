# coding=utf8
from flask import Flask
from flask import render_template
from flask import request
from youtube_transcript_api import YouTubeTranscriptApi

import speech_recognition as sr

app = Flask(__name__,
        static_url_path='', 
        static_folder='static')

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/text/<text>", methods=["GET", "POST"])
def translateBraille(text):
    print(text)
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
        "“": "⠘⠦", "”": "⠘⠴", "‘": "⠄", "’": "⠄",
        "(": "⠐⠣", ")": "⠐⠜", "/": "⠸⠌", "\\": "⠸⠡",
        "-": "⠤", " ": " ", "%": "⠨⠴", "@": "⠈⠁", "$": "⠈⠎", "'": "⠄"
    }
    isNumber = False
    quoteLocation = -1
    try:
        for i in text:
            if i == "\n":
                outputBraille += "\n"
                continue
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
                if i in brailleDict:
                    outputBraille += brailleDict[i]
    except Exception:
        return "Text contains character that is not recognised."
    return outputBraille

@app.route("/speech", methods=["GET", "POST"])
def speechToText():
    try:
        if request.method == 'POST':
            f = request.files['file']
            f.save(f.filename)
            r = sr.Recognizer()
            test = sr.AudioFile(f.filename)
            with test as source:
                audio = r.record(source)
                return translateBraille(r.recognize_google(audio))
    except:
        return "sorry can record again we kinda suck :p"

@app.route("/file", methods=["GET", "POST"])
def fileUpload():
    if request.method == 'POST':
        f = request.files['file']
        return translateBraille(f.read().decode('utf8'))

@app.route("/getTranscript/<videoID>", methods=["GET", "POST"])
def getTranscript(videoID):
    transcription = YouTubeTranscriptApi.get_transcript(videoID, languages=["en"])
    output = ""
    for i in transcription:
        output += translateBraille(u'{}'.format(i["text"]))
        output += "\n"
    return output



if __name__ == "__main__":
    app.run(debug=True)