
import requests

class Insights(object):

    def __init__(self):
        # todo how does state work in Python?
        self.insightsCollection = None

    def collectInsights(self, insights):
        self.insightsCollection.append(insights)

    def reportInsights(self):
        # todo How will these metrics leave the python algorithm and get to the algorithm-queue-reader? Request post here as place holder
        # Post to queue-reader?
        requests.post("algorithm/queue/reader/base/url/insights","",self.insightsCollection)