# coding=utf8
from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
import base64
from youtube_transcript_api import YouTubeTranscriptApi

import speech_recognition as sr

app = Flask(__name__,
        static_url_path='', 
        static_folder='static')

# uwu do you like my clothes?
@app.route("/")
def home():
    return render_template('index.html')

# owO? whats this? i see you're looking through my code uwu.
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

# uwu this is how we listen to your beautiful voice
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
        return "oh no something happened... maybe try that again?"

# uwu thats a BiG FiLe you got there owO
@app.route("/file", methods=["GET", "POST"])
def fileUpload():
    if request.method == 'POST':
        f = request.files['file']
        return translateBraille(f.read().decode('utf8'))

# owO thats a pretty obscene video, does mc-kun like that type of stuff?
@app.route("/getTranscript/<videoID>", methods=["GET", "POST"])
def getTranscript(videoID):
    try:
        transcription = YouTubeTranscriptApi.get_transcript(videoID, languages=["en"])
    except:
        return "Video Link Invalid"
    output = ""
    for i in transcription:
        output += translateBraille(u'{}'.format(i["text"]))
        output += "\n"
    return output

# uwu thats a LONG link you got there owO
@app.route("/youtube/<videoLink>", methods=["GET", "POST"])
def youtube(videoLink):
    try:
        videoLink = decodeBase64(decodeBase64(videoLink))
        videoID = videoLink.split("?v=")
        videoID = videoID[1].split("&")[0]
        return getTranscript(videoID)
    except:
        return "Video Link Invalid"

# uwu fill my file up with your content baby
@app.route("/downloadFile/<content>", methods=["GET", "POST"])
def downloadFile(content):
    f = open("./output.txt", "w")
    f.write(content)
    f.close()
    return send_file("./output.txt", as_attachment=True)

# uwu are you trying to hide from me????
def decodeBase64(text):
    base64_message = text
    base64_bytes = base64_message.encode('utf8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf8')
    return message

if __name__ == "__main__":
    app.run(debug=True)