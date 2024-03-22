import streamlit as st
import requests as req
import pandas as pd
import plotly.express as px
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
response = req.get(url)

dados = pd.DataFrame.from_dict(response.json())

col1, col2 = st.columns(2)

with col1:
    st.metric('Receita', locale.currency(dados['Preço'].sum(), grouping=True),)

with col2:
    st.metric('Quantidade de Vendas', dados.shape[0])

st.dataframe(dados)