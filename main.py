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

# Routes / to index.html (User interface)
@app.route("/")
def home():
    return render_template('index.html')

# The translator function. Handles the entire translation process basically.
@app.route("/text/<text>", methods=["GET", "POST"])
def translateBraille(text):
    outputBraille = ""

    # Braille has no upper or lower case so we convert everything to lower.
    text = text.lower()

    # Dictionary of braille characters to english/ascii characters.
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
        # Translate character by character.
        for i in text:

            # Handles next line characters.
            if i == "\n":
                outputBraille += "\n"
                continue
            
            # Quotations have special behaviour in braille. Single quote mark is different if it has a corresponding closing mark.
            # This function handles replacing the quotation character based on the previously stored quoteLocation
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
            
            # Numbers have a special character to denote that it is a number.
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

        # In case anything fails or an unhandleable character is present, show an error message
        return "Text contains character that is not recognised."
    return outputBraille

# Speech Recogniser API to detect words from wav audio.
@app.route("/speech", methods=["GET", "POST"])
def speechToText():
    try:
        # Relatively straight forward don't think needs explanation
        if request.method == 'POST':
            f = request.files['file']
            f.save(f.filename)
            r = sr.Recognizer()
            test = sr.AudioFile(f.filename)
            with test as source:
                audio = r.record(source)
                text = r.recognize_google(audio)
                return { "braille": translateBraille(text), "text": text }
    except:
        # Catch speech recogniser failure.
        return { "braille": "oh no something happened... maybe try that again?", "text": "" }

# Process uploaded file content to translate.
@app.route("/file", methods=["GET", "POST"])
def fileUpload():
    if request.method == 'POST':
        f = request.files['file']
        return translateBraille(f.read().decode('utf8'))

# Gets the youtube video captions using the videoID.
@app.route("/getTranscript/<videoID>", methods=["GET", "POST"])
def getTranscript(videoID):
    try:
        # Query youtube for captions
        transcription = YouTubeTranscriptApi.get_transcript(videoID, languages=["en"])
    except:
        return "Video Link Invalid"
    output = ""
    for i in transcription:
        # Translate text to Braille
        output += translateBraille(u'{}'.format(i["text"]))
        output += "\n"
    return output

# Retrieves base64 URI encoded youtube link from URL and converts to a normal link to retrieve youtube video ID.
@app.route("/youtube/<videoLink>", methods=["GET", "POST"])
def youtube(videoLink):
    try:
        # Links are base64 encoded in the url as characters such as /, :, & or % in URL conflict.
        # We did it twice as base64 does it weirdly for some reason but twice seemed to work.
        videoLink = decodeBase64(decodeBase64(videoLink))
        videoID = videoLink.split("?v=")
        videoID = videoID[1].split("&")[0]
        return getTranscript(videoID)
    except:
        return "Video Link Invalid"

# Handles file downloads
@app.route("/downloadFile/<content>", methods=["GET", "POST"])
def downloadFile(content):
    # Save translated content to file
    f = open("./output.txt", "w")
    f.write(content)
    f.close()
    # Send file as response to request.
    return send_file("./output.txt", as_attachment=True)

# Basic Base64 decode function
def decodeBase64(text):
    base64_message = text
    base64_bytes = base64_message.encode('utf8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf8')
    return message

if __name__ == "__main__":
    app.run(debug=True)