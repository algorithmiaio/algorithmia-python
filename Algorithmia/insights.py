import requests
import json
from json import JSONEncoder

class Insights:
    # Sends a list of insights to the algorthm queue reader endpoint
    def __init__(self, insights):
        # TODO should we get the URL from a config?
        requests.post("https://localhost:9000/insights", data=json.dumps(insights.__dict__))
