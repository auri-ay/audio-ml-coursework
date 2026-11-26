from audioml.shared.misc import normalise_volume
import io
import flask
import librosa
from flask import Flask, request
import soundfile
from pedalboard_native.io import AudioFile
import numpy as np
import pickle

from .data import DataURL, PostRequest, parse_request, convert_response, Response
from ..shared.misc import to_tensor
from ..shared.data import SharedCollection, AmpSetting
from ..shared.features import calculate_classical_features


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.secret_key = "4"

    try:
        from processing import process_audio
    except ImportError:
        print("\033[31mERROR: Failed to import VST processing, effects will not be applied\033[0m")

        def process_audio(setting: AmpSetting, x: np.ndarray, sr: int) -> np.ndarray:
            return x

    with open("dump/classical.pickel", "rb") as f:
        classical: SharedCollection = pickle.load(f)

    @app.route('/')
    def index():
        return flask.send_file("../../web/index.html")

    @app.route('/ab-testing')
    def ab_testing():
        return flask.send_file("../../web/ab-testing.html")

    @app.route('/<path:path>')
    def serve(path):
        return flask.send_from_directory("../../web/", path)

    @app.route('/api/applyVst', methods=['POST'])
    def thing():
        body: PostRequest[DataURL] = parse_request(request.get_json())

        # Pedalboard can load mp3
        with AudioFile(io.BytesIO(body["dataUrl"]["data"])) as f:
            x_stereo = f.read(f.frames)
            original_sr = f.samplerate

        x_mono = librosa.to_mono(x_stereo)
        sr = 22050
        x = librosa.resample(x_mono, orig_sr=original_sr, target_sr=sr)  # librosa default sample rate

        normalised_x = normalise_volume(x)

        original = io.BytesIO()
        soundfile.write(original, normalised_x, sr, format="ogg")

        x = process_audio(body["setting"], x, sr)

        ground_truth = io.BytesIO()
        soundfile.write(ground_truth, normalise_volume(x), sr, format="ogg")

        result = classical.model(
            to_tensor(classical.scaler.transform(calculate_classical_features(x, sr).to_numpy().reshape(1, -1))))[0]
        pred = AmpSetting(gain=result[0].item(), low=result[1].item(), mid=result[2].item(), treble=result[3].item())

        predicted_x = process_audio(pred, normalised_x, sr)

        predicted = io.BytesIO()
        soundfile.write(predicted, predicted_x, sr, format="ogg")

        response = Response(original=DataURL(data=original.getvalue(), media_type="audio/ogg"),
                            groundTruth=DataURL(data=ground_truth.getvalue(), media_type="audio/ogg"),
                            prediction=DataURL(data=predicted.getvalue(), media_type="audio/ogg"), setting=pred)

        return convert_response(response)

    return app
