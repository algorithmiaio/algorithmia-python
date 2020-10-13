import requests
import json
import os

class Insights:
    # Example of correct insights:
    # {"aKey":"aValue","aKey2":"aValue2"}
    def __init__(self, insights):
        headers = {}
        headers['Content-Type'] = 'application/json'
        AQR_URL = os.getenv('ALGORITHMIA_API') or "http://localhost:9000"
        insight_payload=[{"insight_key": key, "insight_value": insights[key]} for key in insights.keys()]

        requests.post(AQR_URL+"/v1/insights", data=json.dumps(insight_payload).encode('utf-8'), headers=headers)
