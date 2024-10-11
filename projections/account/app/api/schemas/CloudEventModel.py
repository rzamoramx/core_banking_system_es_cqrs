
from pydantic import BaseModel


class CloudEventModel(BaseModel):
    datacontenttype: str
    source: str
    topic: str
    pubsubname: str
    data: str
    id: str
    specversion: str
    tracestate: str
    type: str
    traceid: str
