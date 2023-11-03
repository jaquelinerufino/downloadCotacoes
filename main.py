# from functions import geraCotacoes as func
from functions.classCotacoes import Cotacoes as classCotacoes

mes = '10'
ano = '2023'
caminho = '/Users/jaquelinerufino/Desktop/Estudos/cotacoes/data'

caminho += chr(47)

from datetime import datetime
import pandas as pd
import glob
    
datas = classCotacoes.removeDataInvalida(ano=ano, mes=mes)


erro = classCotacoes.validacaoData(datas).erro
mensagemErro = classCotacoes.validacaoData(datas).mensagemErro

print('Iniciando download: ' + str(datetime.now()))
    
if erro:
    raise(mensagemErro)
else:
    for data in datas:
    
        dataString = data.strftime("%d%m%Y")
        
        erro = downloadCotacoes(dataString, diretorio).erro
        mensagemResultado = downloadCotacoes(dataString, diretorio).mensagemResultado
    
        if erro:
            raise(mensagemResultado)
        else:
            print(mensagemResultado)
    
print('baixaCotacoes executado: ' + str(datetime.now()) )
    
arquivo = open(caminho + "cotacoes_" + ano + mes + ".sql", "w")

caminhoExtensao = caminho + '*.csv'
arquivos = []
arquivo = ''
dados = pd.DataFrame(columns=['COT_DATA','COT_ID', 'tipo', 'moeda', 'COT_COMPRA', 'COT_VENDA', 'COT_COMPRA_USD', 'COT_VENDA_USD'])

caminhoArquivos = glob.glob(caminhoExtensao)

for i in caminhoArquivos:
    arquivos.append(i) 
    
arquivos.sort()

while len(arquivos) > 0:
    arquivo = arquivos[0]
    aux = pd.read_csv(arquivo, delimiter=';', index_col=None, decimal=',',names=['COT_DATA','COT_ID', 'tipo', 'moeda', 'COT_COMPRA', 'COT_VENDA', 'COT_COMPRA_USD', 'COT_VENDA_USD'], dtype={'COT_DATA':str,'COT_ID':str, 'tipo':str, 'moeda':str, 'COT_COMPRA':float, 'COT_VENDA':float, 'COT_COMPRA_USD':float, 'COT_VENDA_USD':float})
    arquivos.remove(arquivo)
    dados["COT_ID"] = dados["COT_ID"].astype(str).str.zfill(3)
    dados = pd.concat([dados, aux], ignore_index=True)
    
for i in dados.index:
    dataFormatada = dados['COT_DATA'][i]
    dataFormatada = dataFormatada[-4:] + dataFormatada[2:4] + dataFormatada[:2]
    dados.at[i, 'COT_DATA'] = dataFormatada
    
dadosFinal = dados[['COT_ID','COT_DATA','COT_COMPRA','COT_VENDA','COT_COMPRA_USD', 'COT_VENDA_USD']]

import re
insert = "INSERT INTO {tabela} (".format(tabela = tabela)
colunas = str(list(dataframe.columns))[1:-1]
colunas = re.sub(r"\'", "", colunas)
valores = ""
for linha in dataframe.itertuples(index=False, name=None):
    valores += insert + colunas + ") values "
    valores += re.sub(r"nan", "null", str(linha))
    valores += "\n"

arquivo.write(valores[:-2])
    
arquivo.close()