import msal
import requests
import json
import pandas as pd
import streamlit as st


# --------------------------------------------------
# Set local variables
# --------------------------------------------------
# https://www.datalineo.com/post/power-bi-rest-api-with-python-and-microsoft-authentication-library-msal
Query_text='{ "queries": [{"query":"evaluate topn(5,suburb)"}], "serializerSettings":{"incudeNulls": true}}'

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
    #api_out = requests.get(url=url_groups, headers=header)
    j = api_out.json()
    df = pd.DataFrame.from_dict(j)
    #print(df)
    st.write(df)
else:
    print(result.get("error"))
    print(result.get("error_description"))
