import streamlit as st
import requests as req
import pandas as pd
import plotly.express as px
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

st.set_page_config(layout='wide')
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

st.sidebar.title('Filtros')

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

qs = {'regiao': regiao.lower(), 'ano': ano}
url = 'https://labdados.com/produtos'
response = req.get(url, params=qs)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedor', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False,)

fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat':False, 'lon':False},
                                  title='Receita por estado',)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))[['Preço']].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal',)
fig_receita_mensal.update_layout(yaxis_title='Receita',)

fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='5 Top estados (receita)',)
fig_receita_estados.update_layout(yaxis_title='Receita')

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False).reset_index()

fig_receita_categorias = px.bar(receita_categorias,
                             x='Categoria do Produto',
                             y='Preço',
                             text_auto=True,
                             title='5 Top categorias (receita)',)
fig_receita_categorias.update_layout(yaxis_title='Receita')

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False,)
vendas_estados.rename({'Preço': 'Vendas'}, axis=1, inplace=True,)

fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Vendas',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat':False, 'lon':False,},
                                  title='Vendas por estado',)
fig_mapa_vendas.update_layout(xaxis_title='Vendas')

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))[['Preço']].count().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()
vendas_mensal.rename({'Preço': 'Vendas'}, axis=1, inplace=True,)

fig_vendas_mensal = px.line(vendas_mensal,
                             x='Mes',
                             y='Vendas',
                             markers=True,
                             range_y=(0, vendas_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal',)

receita, qtd_vendas, vendedor = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with receita:
    col1, col2 = st.columns(2)

    with col1:
        st.metric('Receita', locale.currency(dados['Preço'].sum(), grouping=True),)
        st.plotly_chart(fig_mapa_receita, use_container_width=True,)
        st.plotly_chart(fig_receita_estados, use_container_width=True,)

    with col2:
        st.metric('Quantidade de Vendas', dados.shape[0])
        st.plotly_chart(fig_receita_mensal, use_container_width=True,)
        st.plotly_chart(fig_receita_categorias, use_container_width=True,)

with qtd_vendas:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', locale.currency(dados['Preço'].sum(), grouping=True),)
        st.plotly_chart(fig_mapa_vendas, use_container_width=True,)
    with col2:
        st.metric('Quantidade de Vendas', dados.shape[0])
        st.plotly_chart(fig_vendas_mensal, use_container_width=True,)

with vendedor:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5,)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', locale.currency(dados['Preço'].sum(), grouping=True),) 
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=True).head(qtd_vendedores),
                                    x='sum',
                                    y=vendedores[['sum']].sort_values('sum', ascending=True).head(qtd_vendedores).index,
                                    text_auto=True,
                                    title=f'Top {qtd_vendedores} vendedores (receita)',)
        fig_receita_vendedores.update_layout(yaxis_title='Vendedor',xaxis_title='Valor total em vendas',)
        st.plotly_chart(fig_receita_vendedores, use_container_width=True,)
    with col2:
        st.metric('Quantidade de Vendas', dados.shape[0])
        fig_quantidade_vendas = px.bar(vendedores[['count']].sort_values('count', ascending=True).head(qtd_vendedores),
                                    x='count',
                                    y=vendedores[['count']].sort_values('count', ascending=True).head(qtd_vendedores).index,
                                    text_auto=True,
                                    title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)',)
        fig_quantidade_vendas.update_layout(yaxis_title='Vendedor', xaxis_title='Quantidade de vendas',)
        st.plotly_chart(fig_quantidade_vendas, use_container_width=True,)
    