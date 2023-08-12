import streamlit as st
import bs4
import requests
import pandas as pd
from pymongo import MongoClient
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
import edge_tts
import asyncio
import base64

def m_db_init(coll):

    #atlas
    MONGO_DB = "cluster0"

    MONGO_ID = st.secrets["mongo"]["id"]
    MONGO_PW = st.secrets["mongo"]["pw"]

    connection = MongoClient(f'mongodb://{MONGO_ID}:{MONGO_PW}@cluster0-shard-00-00-k5utu.mongodb.net:27017,cluster0-shard-00-01-k5utu.mongodb.net:27017,cluster0-shard-00-02-k5utu.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin')

    db = connection[MONGO_DB]
    collection = db[coll]

    return collection

def autoplay_audio(data: str):
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio controls autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )

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

df_hn = hnsummary.sort_values('_id', ascending=False)[['Content', 'URL']]

# st.dataframe(df_hn,
#              use_container_width=True,
#              hide_index=True)


gb = GridOptionsBuilder.from_dataframe(df_hn)
# configure selection
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_pagination(enabled=True, paginationPageSize=5)
gb.configure_side_bar()
gridOptions = gb.build()

data = AgGrid(df_hn,
              height=300,
              gridOptions=gridOptions,
              enable_enterprise_modules=True,
              allow_unsafe_jscode=True,
              update_mode=GridUpdateMode.SELECTION_CHANGED,
              columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
              custom_css={"#gridToolBar": {"padding-bottom": "0px !important"}}, 
              )


VOICE = "ko-KR-SunHiNeural"
OUTPUT_FILE = "test.mp3"

VOICE_dict = {"male": "ko-KR-InJoonNeural",
              "female": "ko-KR-SunHiNeural"}


async def create_tts(TEXT_inp, gender) -> None:

    communicate = edge_tts.Communicate(TEXT_inp, VOICE_dict[gender])
    await communicate.save(OUTPUT_FILE)


async def amain(TEXT_inp) -> None:

    gender = "female"

    await create_tts(TEXT_inp, gender)

    audio_file = open(OUTPUT_FILE,'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/ogg')

    autoplay_audio(audio_bytes)

selected_rows = data["selected_rows"]

if st.button("Re-run"):
    st.experimental_rerun()



if len(selected_rows) != 0:
    contents = selected_rows[0]['Content']
    content = contents.splitlines()
    url = selected_rows[0]['URL']

    st.markdown("##### Subject")
    st.markdown(f":orange[{content[0]}]")
    # st.markdown(f":orange[{selected_rows[0]['Subject']}]")
    st.markdown("##### Content")
    st.markdown(f":orange[{content[1]}]")

    st.markdown("##### URL")
    st.markdown(f'<a href="{url}" target="_blank">{url}</a>', unsafe_allow_html=True)

    if st.button("Text-to-Speech"):
        asyncio.run(amain(contents))
