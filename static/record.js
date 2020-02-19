//webkitURL is deprecated but nevertheless 
URL = window.URL || window.webkitURL;
var gumStream;
//stream from getUserMedia() 
var rec;
//Recorder.js object 
var input;
//MediaStreamAudioSourceNode we'll be recording 
// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext;
//new audio context to help us record 
var recordButton = document.getElementById("recordBtn");

let isRecording = false;

function startRecording() {
    console.log("recordButton clicked");
    var constraints = { audio: true, video: false }

    isRecording = true;

    recordButton.style.backgroundColor = "red";
    recordButton.style.color = "white";

    let tB = document.getElementById('textBox');
    tB.classList.remove("toggled");
    tB.placeholder = "你干嘛？";
    tB.value = "";
    window.isYoutube = false;

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        console.log("hi");
        
        audioContext = new AudioContext();

        //update the format 
        //document.getElementById("formats").innerHTML = "Format: 1 channel pcm @ " + audioContext.sampleRate / 1000 + "kHz"

        /*  assign to gumStream for later use  */
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);

        console.log(input);

        rec = new Recorder(input, { numChannels: 1 })


        //start the recording process
        rec.record()

        console.log("Recording started");

    }).catch(function (err) {
        //enable the record button if getUserMedia() fails
    });
}

function stopRecording() {
    console.log("stopButton clicked");

    //tell the recorder to stop the recording
    rec.stop();

    isRecording = false;

    recordButton.style.backgroundColor = "";
    recordButton.style.color = "";

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    //create the wav blob and pass it on to createDownloadLink
    rec.exportWAV(uploadToServer);
}

function uploadToServer(blob) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function (e) {
        if (this.readyState === 4) {
            console.log("Server returned: ", e.target.responseText);
            document.getElementById("output").value = e.target.responseText;
        }
    };
    var fd = new FormData();
    fd.append("file", blob, "test.wav");
    xhr.open("POST", "/speech", true);
    xhr.send(fd);
}