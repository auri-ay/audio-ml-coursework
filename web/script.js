const uploadButton = document.getElementById("upload-button")
const fileUpload = document.getElementById("file-upload");
const audioPlayer = document.getElementById("audio-player");


class Setting{
    constructor(gain, low, mid, treble) {
        this.gain = gain;
        this.low = low;
        this.mid = mid;
        this.treble = treble
    }
}

let uploadedFile = null;
const uploadedFileReader =  new FileReader();
uploadedFileReader.onload = (e) =>{
    uploadedFile = e.target.result;
    sendPost();
}

let resultFile = null;
const resultFileReader = new FileReader();
resultFileReader.onload = (e) => {
    resultFile = e.target.result;
}

uploadButton.onclick = () => {
    uploadButton.disabled = true;
    uploadedFileReader.readAsDataURL(fileUpload.files[0]);
}

function sendPost(){
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/thing");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        dataUrl: uploadedFile,
        setting: new Setting(0,0,0,0)
    }))
    xhr.onreadystatechange = () => {
        if (xhr.readyState !== 4) return;
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            console.log(data)
            audioPlayer.src = data["dataUrl"]
            audioPlayer.style.display = "default"
        }
    }
}