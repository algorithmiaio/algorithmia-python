
import requests

class Insights(object):

    def __init__(self, insights):
        # todo: pull this from a config.py file?
        requests.post("https://localhost:9000/insights", insights)
