# adapted from https://www.datalineo.com/post/power-bi-rest-api-with-python-and-microsoft-authentication-library-msal

import msal
import requests
import json
import pandas as pd
import streamlit as st
import base64
import altair as alt
col1, col2, col3 = st.columns(3)


# --------------------------------------------------
# Set local variables
# --------------------------------------------------

username = st.secrets["username"]
password = st.secrets["password"]
authority_url = st.secrets["authority_url"]


client_id = '7f67af8a-fedc-4b08-8b4e-37c4d127b6cf'

scope = ["https://analysis.windows.net/powerbi/api/.default"]
url_Query= 'https://api.powerbi.com/v1.0/myorg/datasets/dd9ede3e-58bc-4097-8790-88bc0cfd41ea/executeQueries'

@st.cache
def Run_Query(DAX_Query_Value,header_value,url_Query_value):
      Query_text='{ "queries": [{"query":'+DAX_Query_Value+'}], "serializerSettings":{"incudeNulls": true}}'
      api_out = requests.post(url=url_Query_value,data=Query_text, headers=header_value)
      api_out.encoding='utf-8-sig'
      out = api_out.json()
      jj = out['results'][0]['tables'][0]['rows']
      df = pd.DataFrame(jj)
      return df


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
    
    DAX_Query1=  """ "EVALUATE
                  SUMMARIZECOLUMNS(
                  Generator_list[StationName],
                  KEEPFILTERS( FILTER( ALL( Generator_list[StationName] ), NOT( ISBLANK( Generator_list[StationName] )))),
                  \\"GWh\\", [GWh])" """

    dd= Run_Query(DAX_Query1,header,url_Query)
    catalogue_Select= st.sidebar.multiselect('Select Station', dd['Generator_list[StationName]'])
    granularity_Select= st.sidebar.selectbox('Select Level of Details', ['Month','Year'])
        
    
    if len(catalogue_Select) != 0 :
       xxxx = '\\",\\"'.join(catalogue_Select)
       tt = '\\\"'+xxxx+'\\'
       DAX_Query2=  """ "EVALUATE
       SUMMARIZECOLUMNS(
       Generator_list[StationName],
       MstDate["""+granularity_Select+"""],
       KEEPFILTERS( TREATAS( {"""+tt+""""}, Generator_list[StationName] )),
       KEEPFILTERS( TREATAS( {\\"DUNIT\\"}, unit[unit] )),
       \\"GWh\\", [GWh])" """
    else:
       DAX_Query2=  """ "EVALUATE
       SUMMARIZECOLUMNS(
       Generator_list[FuelSourceDescriptor],
       MstDate["""+granularity_Select+"""],
       KEEPFILTERS( FILTER( ALL( Generator_list[StationName] ), NOT( ISBLANK( Generator_list[StationName] )))),
       KEEPFILTERS( TREATAS( {\\"DUNIT\\"}, unit[unit] )),
       \\"GWh\\", [GWh])" """
    
    dd= Run_Query(DAX_Query2,header,url_Query)
    dd.columns = ['station', 'date','Gwh']
    c = alt.Chart(dd).mark_bar().encode(
        x=alt.X('date', axis=alt.Axis(labels=False)),
        y='Gwh',color='station',tooltip=['date', 'Gwh', 'station'])
    
else:
    print(result.get("error"))
    print(result.get("error_description"))
#download
def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.
    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')
    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'



