import streamlit as st
import requests as req
import pandas as pd
import time

st.set_page_config(layout='wide')

@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False,)

def msg_sucesso():
    msg = st.success('Arquivo baixado com sucesso')
    time.sleep(10)
    msg.empty()

url = 'https://labdados.com/produtos'
response = req.get(url,)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns),)

query = ''
with st.sidebar:
    st.title('Filtros')

    with st.expander('Nome do produto'):
        produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique(),)
    with st.expander('Preço do produto'):
        preco = st.slider('Selecione o preço', 0, 5000, (0, 5000),)
    with st.expander('Data da compra'):
        data_compra = st.date_input('Selecione a data', value=(dados['Data da Compra'].min(), dados['Data da Compra'].max()), min_value=dados['Data da Compra'].min(), max_value=dados['Data da Compra'].max(),)

query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''

dados_filtrados = dados.query(query)[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'Total de :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas.')

st.markdown('Escreva um nome para o arquivo')
col1, col2 = st.columns(2)
with col1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados_filtrados')
    nome_arquivo += '.csv'
with col2:
    st.download_button('Download CSV', data=converte_csv(dados_filtrados), file_name=nome_arquivo, on_click=msg_sucesso, mime='text/csv',)