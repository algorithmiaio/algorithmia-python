import requests
import json
import os

class Insights:
    # Example of correct insights:
    # {"aKey":"aValue","aKey2":"aValue2"}
    # TODO add this env variable to the deploy config in stage tools?
    def __init__(self, insights):
        AQR_URL = os.getenv('ALGORITHM_QUEUE_READER_URL') or "https://localhost:9000"
        requests.post(AQR_URL+"/insights", data=json.dumps(insights).encode('utf-8'))
