import base64
import io
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, cast, overload, Any, Unpack, NamedTuple, ReadOnly
import flask
from flask import Flask, request
import soundfile


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


def process_audio(setting: AmpSetting, x, sr):
    # code to process X using the setting
    print(setting)
    return x


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

    x, sr = soundfile.read(io.BytesIO(body["dataUrl"]["data"]))

    # modify x as needed here
    x = process_audio(body["setting"], x, sr)

    output = io.BytesIO()
    soundfile.write(output, x, sr, format="ogg")

    response = PostRequest(dataUrl=DataURL(data=output.getvalue(), media_type="audio/ogg"),
                           setting=body["setting"])

    return convert_response(response)


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8081)
