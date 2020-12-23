import requests
import pandas as pd
from pandas.io.json import json_normalize

url = 'https://4o8d0ft32f.execute-api.us-east-2.amazonaws.com/test/glld/name/%7Bname-search%7D?name=mead'

r = requests.get(url)
json_decode = r.json()
df = pd.DataFrame().from_records(json_decode, columns = ['id_No', 'lake_name', 'source', 'metadata'])
meta_series = df['metadata'].map(eval).apply(pd.Series)
df_unpacked = pd.merge(left = df,
                       right = meta_series.drop(['source', 'lake_name'],
                        axis = 1),
                       left_index = True,
                       right_index = True,
                       how = 'outer').drop('metadata', axis = 1)
# %%