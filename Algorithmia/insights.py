
import requests

class Insights(object):

    def __init__(self):
        self.insightsCollection = None

    def collectInsights(self, insights):
        self.insightsCollection.append(insights)

    def reportInsights(self):
        requests.post("","",self.insightsCollection)