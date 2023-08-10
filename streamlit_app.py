import streamlit as st
import bs4
import requests
import pandas as pd
from pymongo import MongoClient
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode


def m_db_init(coll):

    #atlas
    MONGO_DB = "cluster0"

    MONGO_ID = st.secrets["mongo"]["id"]
    MONGO_PW = st.secrets["mongo"]["pw"]

    connection = MongoClient(f'mongodb://{MONGO_ID}:{MONGO_PW}@cluster0-shard-00-00-k5utu.mongodb.net:27017,cluster0-shard-00-01-k5utu.mongodb.net:27017,cluster0-shard-00-02-k5utu.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin')

    db = connection[MONGO_DB]
    collection = db[coll]

    return collection

st.set_page_config(
    page_title="Hacker News Summary",
    page_icon="random",
    layout="wide",
    initial_sidebar_state="expanded"
    )

st.title("Hacker News Summary (Korean)")

coll = 'hnsummary'

collection = m_db_init(coll)

hnsummary = pd.DataFrame(list(collection.find()))
# hnsummary.drop(['_id'], axis='columns', inplace=True)

df_hn = hnsummary.sort_values('_id', ascending=False)[['Subject', 'Content']]

st.dataframe(df_hn,
             use_container_width=True,
             hide_index=True)


gb = GridOptionsBuilder.from_dataframe(df_hn)
# configure selection
gb.configure_selection(selection_mode="single", use_checkbox=True)
gb.configure_pagination(enabled=True, paginationAutoPageSize=True, paginationPageSize=10)
gb.configure_side_bar()
gridOptions = gb.build()

data = AgGrid(df_hn,
              gridOptions=gridOptions,
              enable_enterprise_modules=True,
              allow_unsafe_jscode=True,
              update_mode=GridUpdateMode.SELECTION_CHANGED,
              columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
              custom_css={"#gridToolBar": {"padding-bottom": "0px !important"}}
              )

selected_rows = data["selected_rows"]

if len(selected_rows) != 0:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Subject")
        st.markdown(f":orange[{selected_rows[0]['Subject']}]")
    with col2:
        st.markdown("##### Content")
        st.markdown(f":orange[{selected_rows[0]['Content']}]")
