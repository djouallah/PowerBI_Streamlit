# adapted from https://www.datalineo.com/post/power-bi-rest-api-with-python-and-microsoft-authentication-library-msal

import msal
import requests
import json
import pandas as pd
import streamlit as st
import base64
import altair as alt
col1, col2 = st.beta_columns(2)
col1.write("[PowerBI Data API](https://powerbi.microsoft.com/en-us/blog/announcing-the-public-preview-of-power-bi-rest-api-support-for-dax-queries/)")
col2.write("[By Mim](https://datamonkeysite.com/about/)")
st.markdown(tmp_download_link, unsafe_allow_html=True)

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


url_Query= 'https://api.powerbi.com/v1.0/myorg/datasets/5ae65cd5-b8f1-4d0f-aba6-2e6bdb64c005/executeQueries'
DAX_Query1=  """ "EVALUATE
                  SUMMARIZECOLUMNS(
                  Generator_list[StationName],
                  KEEPFILTERS( FILTER( ALL( Generator_list[StationName] ), NOT( ISBLANK( Generator_list[StationName] )))),
                  \\"GWh\\", [GWh])" """



Query_text='{ "queries": [{"query":'+DAX_Query1+'}], "serializerSettings":{"incudeNulls": true}}'


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
    jj = j['results'][0]['tables'][0]['rows']
    df = pd.DataFrame(jj)
    catalogue_Select= st.sidebar.selectbox('Select Station', df['Generator_list[StationName]'])
    tt = '\\\"'+catalogue_Select+'\\'
    
    
    DAX_Query2=  """ "EVALUATE
       SUMMARIZECOLUMNS(
       Generator_list[StationName],
       MstDate[Month],
       KEEPFILTERS( TREATAS( {"""+tt+""""}, Generator_list[StationName] )),
       KEEPFILTERS( TREATAS( {\\"TUNIT\\"}, unit[unit] )),
       \\"GWh\\", [GWh])" """
    Query_text='{ "queries": [{"query":'+DAX_Query2+'}], "serializerSettings":{"incudeNulls": true}}'
    
    api_out = requests.post(url=url_Query,data=Query_text, headers=header)
    api_out.encoding='utf-8-sig'
    j = api_out.json()
    jj = j['results'][0]['tables'][0]['rows']
    df = pd.DataFrame(jj)
    df.columns = ['station', 'date','Gwh']
    #st.write(df)
    c = alt.Chart(df).mark_area().encode(
        x='date', y='Gwh',tooltip=['date', 'Gwh', 'station'])
    st.altair_chart(c, use_container_width=True)
    st.header('DAX Query')
    st.write(DAX_Query2)
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


# Examples
tmp_download_link = download_link(df, 'YOUR_DF.csv', 'Download')




