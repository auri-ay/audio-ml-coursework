import base64
from typing import TypedDict, cast

from shared import AmpSetting


class DataURL(TypedDict):
    media_type: str | None
    data: bytes


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
