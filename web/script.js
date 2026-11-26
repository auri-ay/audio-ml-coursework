const uploadButton = document.getElementById("upload-button");
const resetButton = document.getElementById("reset-button");
const fileUpload = document.getElementById("file-upload");
const originalAudioPlayer = document.getElementById("original-audio-player");
const groundTruthAudioPlayer = document.getElementById("ground-truth-audio-player");
const predictionAudioPlayer = document.getElementById("prediction-audio-player");
const gainSliderInput = document.getElementById("gain-slider-input");
const lowSliderInput = document.getElementById("low-slider-input");
const midSliderInput = document.getElementById("mid-slider-input");
const trebleSliderInput = document.getElementById("treble-slider-input");
const gainSliderOutput = document.getElementById("gain-slider-output");
const lowSliderOutput = document.getElementById("low-slider-output");
const midSliderOutput = document.getElementById("mid-slider-output");
const trebleSliderOutput = document.getElementById("treble-slider-output");
const predictionResetButton = document.getElementById("prediction-reset-button")


fileUpload.onchange = () => {
    uploadButton.disabled = fileUpload.files.length !== 1;
}

class Setting {
    constructor(gain, low, mid, treble) {
        this.gain = gain;
        this.low = low;
        this.mid = mid;
        this.treble = treble
    }
}

let uploadedFile = null;
const uploadedFileReader = new FileReader();
uploadedFileReader.onload = (e) => {
    uploadedFile = e.target.result;
    sendPost();
}

uploadButton.onclick = () => {
    uploadButton.disabled = true;
    uploadedFileReader.readAsDataURL(fileUpload.files[0]);
    originalAudioPlayer.src = "";
    groundTruthAudioPlayer.src = "";
    predictionAudioPlayer.src = "";
    gainSliderOutput.value = 0;
    lowSliderOutput.value = 0;
    midSliderOutput.value = 0;
    trebleSliderOutput.value = 0;
}

resetButton.onclick = () => {
    uploadButton.disabled = true;
    uploadedFileReader.abort();
    originalAudioPlayer.src = "";
    groundTruthAudioPlayer.src = "";
    predictionAudioPlayer.src = "";
    gainSliderInput.value = 0;
    lowSliderInput.value = 0;
    midSliderInput.value = 0;
    trebleSliderInput.value = 0;
    gainSliderOutput.value = 0;
    lowSliderOutput.value = 0;
    midSliderOutput.value = 0;
    trebleSliderOutput.value = 0;
    fileUpload.value = ""
}
predictionResetButton.onclick = () => {
    predictionAudioPlayer.src = "";
    gainSliderOutput.value = 0;
    lowSliderOutput.value = 0;
    midSliderOutput.value = 0;
    trebleSliderOutput.value = 0;
}


function sendPost() {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/applyVst");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        dataUrl: uploadedFile,
        setting: new Setting(gainSliderInput.value, lowSliderInput.value, midSliderInput.value, trebleSliderInput.value)
    }))
    xhr.onreadystatechange = () => {
        if (xhr.readyState !== 4) return;
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            console.log(data)
            originalAudioPlayer.src = data["original"];
            groundTruthAudioPlayer.src = data["groundTruth"];
            predictionAudioPlayer.src = data["prediction"];
            gainSliderOutput.value = data["setting"]["gain"];
            lowSliderOutput.value = data["setting"]["low"];
            midSliderOutput.value = data["setting"]["mid"];
            trebleSliderOutput.value = data["setting"]["treble"];
            uploadButton.disabled = false;
        }else{
            alert("Server   responded with a non 200 response")
            uploadButton.disabled = false;
        }
    }
}