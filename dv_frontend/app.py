import streamlit as st
from routes.index import get_nav 

pg = get_nav()

pg.run()