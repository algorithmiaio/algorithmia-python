import requests
import json
import os

class Insights:
    # Example of correct insights:
    # {"aKey":"aValue","aKey2":"aValue2"}
    def __init__(self, insights):
        headers = {}
        headers['Content-Type'] = 'application/json'
        AQR_URL = os.getenv('ALGORITHM_QUEUE_READER_URL') or "http://localhost:9000"

        requests.post(AQR_URL+"/insights", data=json.dumps(insights).encode('utf-8'), headers=headers)
