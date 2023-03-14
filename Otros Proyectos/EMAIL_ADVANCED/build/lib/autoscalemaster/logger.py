import os

import httpx as httpx
import msgpack
import structlog


def send_to_logtail(logger, method_name, event_dict):
    # Your Logtail API Key
    # Beware: Do not hardcode your API key in your code. Instead, use an environment variable.
    headers = {
        "Authorization": "Bearer %s" % os.environ["LOGTAIL_KEY"],
        "Content-Type": "application/msgpack",
    }

    # Our log message and all the event context is sent as a JSON string
    # in the POST body
    # https://docs.logtail.com/integrations/rest-api
    payload = {
        "message": event_dict["event"],
        "level": method_name,
        "context": event_dict,
    }

    httpx.post("https://in.logtail.com", data=msgpack.packb(payload), headers=headers)

    return event_dict


def init_logger():
    structlog.configure(
        processors=[
            #send_to_logtail,
            structlog.processors.JSONRenderer(),
        ],
    )
