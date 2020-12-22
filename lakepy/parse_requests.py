import requests
import pandas as pd
from pandas.io.json import json_normalize

url = 'https://4o8d0ft32f.execute-api.us-east-2.amazonaws.com/test/lakename?name=mead'

r = requests.get(url)
json_decode = r.json()
df = pd.DataFrame(json_decode)
# %%