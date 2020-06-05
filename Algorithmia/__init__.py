'Algorithmia API Client (python)'

from Algorithmia.client import Client
from Algorithmia.handler import Handler
import os

apiKey = None
apiAddress = None

# Get reference to an algorithm using a default client
def algo(algoRef):
    # Return algorithm reference using default client
    return getDefaultClient().algo(algoRef)

def file(dataUrl):
    return getDefaultClient().file(dataUrl)

def dir(dataUrl):
    return getDefaultClient().dir(dataUrl)

def client(api_key=None, api_address=None):
    return Client(api_key, api_address)

def handler(apply_func, load_func=lambda: None):
    return Handler(apply_func, load_func)

# The default client to use, assuming the user does not want to construct their own
defaultClient = None

# Used internally to get default client
def getDefaultClient():
    global defaultClient
    # Check for default client, and ensure default API key has not changed
    if defaultClient is None or defaultClient.apiKey is not apiKey:
        # Construct default client
        defaultClient = Client(apiKey)
    return defaultClient

# Used internally to get default api client
def getApiAddress():
    global apiAddress
    if apiAddress is not None:
        # First check for user setting Algorithmia.apiAddress = "XXX"
        return apiAddress
    elif 'ALGORITHMIA_API' in os.environ:
        # Then check for system environment variable
        return os.environ['ALGORITHMIA_API']
    else:
        # Else return default
        return "https://api.algorithmia.com"
