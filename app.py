# adapted from https://www.datalineo.com/post/power-bi-rest-api-with-python-and-microsoft-authentication-library-msal
# thanks for https://twitter.com/GBrueckl for the trick on how to get the client_id without registring an App.

import msal
import requests
import json
import pandas as pd
import streamlit as st
import base64
import altair as alt
col1, col2, col3 = st.columns(3)

# --------------------------------------------------
# Authentification
# --------------------------------------------------

client_id = st.secrets["client_id"]  
username =  st.secrets["username"]
password =  st.secrets["password"]
authority_url = 'https://login.microsoftonline.com/projectscontrols.com'
scope = ["https://analysis.windows.net/powerbi/api/.default"]
url_Query= 'https://api.powerbi.com/v1.0/myorg/datasets/bb37e43d-3eab-4d25-98a9-35fe7372a72a/executeQueries'

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
    granularity_Select= st.sidebar.selectbox('Select Level of Details', ['Month','day'])
        
    
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

#Download Button
def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

csv = convert_df(dd)
col2.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='large_df.csv',
            mime='text/csv',
        )
###################

col3.write("[By Mim](https://datamonkeysite.com/about/)")
st.altair_chart(c, use_container_width=True)
st.sidebar.header('DAX Query')
st.sidebar.write(DAX_Query2)
st.sidebar.write("[PowerBI Data API](https://powerbi.microsoft.com/en-us/blog/announcing-the-public-preview-of-power-bi-rest-api-support-for-dax-queries/)")
