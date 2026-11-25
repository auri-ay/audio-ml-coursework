import base64
import io
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, cast, overload, Any, Unpack, NamedTuple, ReadOnly
import flask
import librosa
import pedalboard
import torch
from flask import Flask, request
import soundfile
from pedalboard_native.io import AudioFile
import numpy as np
import pickle
from shared import SharedCollection, NaiveModel, calculate_classical_features, flatten, to_tensor
from vst import process_audio


with open("dump/classical.pickel", "rb") as f:
    classical: SharedCollection = pickle.load(f)


class DataURL(TypedDict):
    media_type: str | None
    data: bytes


class AmpSetting(TypedDict):
    gain: float
    low: float
    mid: float
    treble: float


class PostRequest[D: str | DataURL](TypedDict):
    setting: AmpSetting
    dataUrl: D


def parse_request(r: PostRequest[str]) -> PostRequest[DataURL]:
    n = cast(PostRequest[DataURL], r)
    n["dataUrl"] = parse_data_url(r["dataUrl"])
    return n


def convert_response(r: PostRequest[DataURL]) -> PostRequest[str]:
    n = cast(PostRequest[str], r)
    n["dataUrl"] = dataurl_to_str(r["dataUrl"])
    return n


def parse_data_url(s: str) -> DataURL:
    s = s.split(":")[1]
    optional, data = s.split(",")
    try:
        media_type, b64 = optional.split(";")
    except ValueError:
        media_type = None
        b64 = None

    if b64 == "base64":
        data = base64.b64decode(data)
    else:
        raise Exception(f"Invalid data url, expected base64: {data}")

    return DataURL(media_type=media_type, data=data)


def dataurl_to_str(s: DataURL) -> str:
    return f"data:{s["media_type"]};base64,{base64.b64encode(s["data"]).decode("ascii")}"



app = Flask(__name__)


@app.route('/')
def index():
    return flask.send_file("web/index.html")


@app.route('/<path:path>')
def serve(path):
    return flask.send_from_directory("web/", path)


@app.route('/api/applyVst', methods=['POST'])
def thing():
    body: PostRequest[DataURL] = parse_request(request.get_json())

    # Pedalboard can load mp3
    with AudioFile(io.BytesIO(body["dataUrl"]["data"])) as f:
        x_stereo = f.read(f.frames)
        original_sr = f.samplerate

    x_mono = librosa.to_mono(x_stereo)
    sr = 22050
    x = librosa.resample(x_mono, orig_sr=original_sr, target_sr=sr) # librosa default sample rate

    # modify x as needed here
    x = process_audio(body["setting"], x, sr)

    result = classical.model.to("cpu")(to_tensor(classical.scaler.transform(calculate_classical_features(x, sr).to_numpy().reshape(1, -1))))[0]
    pred = AmpSetting(gain=result[0].item(),low=result[1].item(), mid=result[2].item(),treble=result[3].item())

    output = io.BytesIO()
    soundfile.write(output, x, sr, format="ogg")

    response = PostRequest(dataUrl=DataURL(data=output.getvalue(), media_type="audio/ogg"),
                           setting=pred)

    return convert_response(response)


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8081)
