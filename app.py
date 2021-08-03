# adapted from https://www.datalineo.com/post/power-bi-rest-api-with-python-and-microsoft-authentication-library-msal

import msal
import requests
import json
import pandas as pd
import streamlit as st


# --------------------------------------------------
# Set local variables
# --------------------------------------------------
# you need to register your app to get the client id, if microsft is reading this please find a better way
client_id = st.secrets["client_id"]
username = st.secrets["username"]
password = st.secrets["password"]
#using personal domain projectscontrols, replace with your domain
authority_url = 'https://login.microsoftonline.com/projectscontrols.com'
scope = ["https://analysis.windows.net/powerbi/api/.default"]
url_Query= 'https://api.powerbi.com/v1.0/myorg/datasets/74dd6816-3c74-4c18-91bd-086669c4d749/executeQueries'
#DAX Query reritun 5 rows from a table suburb
Query_text='{ "queries": [{"query":"evaluate topn(2,suburb)"}], "serializerSettings":{"incudeNulls": true}}'

# --------------------------------------------------
# Use MSAL to grab a token
# --------------------------------------------------
app = msal.PublicClientApplication(client_id, authority=authority_url)
result = app.acquire_token_by_username_password(username=username,password=password,scopes=scope)

# --------------------------------------------------
# Check if a token was obtained, grab it and call the
# Power BI REST API, otherwise throw up the error message
# --------------------------------------------------
if 'access_token' in result:
    access_token = result['access_token']
    header = {'Content-Type':'application/json','Authorization': f'Bearer {access_token}'}
    api_out = requests.post(url=url_Query,data=Query_text, headers=header)
    api_out.encoding='utf-8-sig'
    j = api_out.json()
    df = pd.DataFrame.from_dict(j)
    st.write(json.dumps(j))
else:
    print(result.get("error"))
    print(result.get("error_description"))
