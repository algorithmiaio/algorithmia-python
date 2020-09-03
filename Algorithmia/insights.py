
import requests

class Insights(object):

    def __init__(self, insights):
        requests.post("https://localhost:9000/insights", insights)
