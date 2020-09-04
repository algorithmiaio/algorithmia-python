import requests


class Insights:
    # Example of correct insights = { {"insightKey":"aKey", "insightValue":"aValue"}, {"insightKey":"aKey2", "insightValue":"aValue2"} }
    def __init__(self, insights):
        # TODO should we get the URL from a config?
        requests.post("https://localhost:9000/insights", data=insights)
