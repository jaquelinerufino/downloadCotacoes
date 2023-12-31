def leArquivos(mes, ano, caminho):

    from functions import geraInsert as func
    import pandas as pd
    import glob

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
    
    texto = func.geraInsert(dadosFinal, 'tp_master.dbo.I_COTACOES' )
        
    return texto