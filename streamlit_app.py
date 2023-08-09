import streamlit as st
import bs4
import requests
import pandas as pd
from pymongo import MongoClient


def m_db_init(coll):

    #atlas
    MONGO_DB = "cluster0"

    MONGO_ID = st.secrets["mongo"]["id"]
    MONGO_PW = st.secrets["mongo"]["pw"]

    connection = MongoClient(f'mongodb://{MONGO_ID}:{MONGO_PW}@cluster0-shard-00-00-k5utu.mongodb.net:27017,cluster0-shard-00-01-k5utu.mongodb.net:27017,cluster0-shard-00-02-k5utu.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin')

    db = connection[MONGO_DB]
    collection = db[coll]

    return collection


st.title("Hacker News Summary (Korean)")

coll = 'hnsummary'

collection = m_db_init(coll)

hnsummary = pd.DataFrame(list(collection.find()))
# hnsummary.drop(['_id'], axis='columns', inplace=True)

st.write(hnsummary.sort_values('_id', ascending=False))
