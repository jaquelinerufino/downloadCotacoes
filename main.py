def baixacotacoes(data, caminho):
    
    # importação de bibliotecas
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.edge import options as EdgeOptions
    import time
    import os.path

    # configura navegador
    options = EdgeOptions.Options()
        
    options.use_chromium = True
        
    options.add_experimental_option("prefs", {"download.default_directory": caminho})
    
    driver = webdriver.Edge(options= options)
    
    driver.minimize_window()
    
    # baixa o arquivo
    driver.get("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes")
    
    botao_cookies = "/html/body/app-root/bcb-cookies/div/div/div/div/button[2]"

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, botao_cookies))).click()
    
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
    driver.switch_to.frame(iframe)
    
    radio = driver.find_element(By.XPATH,"//input[@type='radio'][@value='2']")

    botao = driver.find_element(By.XPATH,"//input[@type='submit']")
    
    radio.click()
    
    datainicial = driver.find_element(By.ID, "DATAINI")
    datainicial.clear()
    datainicial.send_keys(data)
    
    driver.implicitly_wait(0.5)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(botao)).click()
    
    link = driver.find_element(By.PARTIAL_LINK_TEXT, "CSV")
    link.click()
    
    file_path = caminho + "cotacaoTodasAsMoedas_" + data + ".csv"

    while not os.path.exists(file_path):
        time.sleep(1)
        
    driver.quit()

def executaCotacoes(mes, ano, caminho):
    
    import holidays
    from datetime import datetime, timedelta
    import calendar
    
    feriados = holidays.BR()
    datatexto = '01/'+ mes + '/' + ano
    erro = 0

    dataInicial = datetime.strptime(datatexto,"%d/%m/%Y").date()

    hoje = datetime.now().date()

    _, lastday = calendar.monthrange(dataInicial.year, dataInicial.month)
    fimMes = datetime(dataInicial.year, dataInicial.month, lastday).date()

    if hoje.year < dataInicial.year:
        print ('Erro: Não é possível baixar cotações de anos futuros.')
        erro = 1
    elif hoje.year == dataInicial.year and hoje.month < dataInicial.month:
        print ('Erro: Não é possível baixar cotações de meses futuros.')
        erro = 1
    elif hoje == fimMes:
        dataFinal = hoje - timedelta(days = 1)
    elif hoje.year == dataInicial.year and hoje.month == dataInicial.month and hoje < fimMes:
        dataFinal = datetime(dataInicial.year, dataInicial.month, hoje.day).date()
    else:
        dataFinal = fimMes.date() + timedelta(days = 1)

    if erro == 0:

        while dataInicial < dataFinal:
    
            aux = 0
    
            while aux == 0:
                if dataInicial.weekday() == 5:
                    dataInicial = dataInicial + timedelta(days = 2)
                elif dataInicial.weekday() == 6:
                    dataInicial = dataInicial + timedelta(days = 1)
                elif dataInicial in feriados:
                    dataInicial = dataInicial + timedelta(days = 1)
                else:
                    aux = 1
    
            dataString = dataInicial.strftime("%d%m%Y")
            try:
                baixacotacoes(dataString, caminho)
            except Exception as e:
                print('Finalizado com erro: ' + e)
            else:
                print('Arquivo finalizado com sucesso: ' + dataInicial.strftime("%d/%m/%y"))
            
            dataInicial = dataInicial + timedelta(days = 1)

def geraInsert(dataframe, tabela):
    
    import re

    insert = "INSERT INTO {tabela} (".format(tabela = tabela)

    colunas = str(list(dataframe.columns))[1:-1]
    colunas = re.sub(r"\'", "", colunas)

    valores = ""

    for linha in dataframe.itertuples(index=False, name=None):
        valores += insert + colunas + ") values "
        valores += re.sub(r"nan", "null", str(linha))
        valores += ",\n"

    return valores[:-2]

def leArquivos(mes, ano, caminho):

    import pandas as pd
    import glob

    caminhoExtensao = caminho + '*.csv'
    arquivos = []
    arquivo = ''
    dados = pd.DataFrame(columns=['COT_DATA','COT_ID', 'tipo', 'moeda', 'COT_COMPRA', 'COT_VENDA', 'COT_COMPRA_USD', 'COT_VENDA_USD'])
    
    caminhoArquivos = glob.glob(caminhoExtensao)
    
    for i in caminhoArquivos:
        arquivos.append(i.replace(caminho[:caminho[:-1].rfind('/')+ 1] , '')) 
        
    arquivos.sort()
    
    while len(arquivos) > 0:
        arquivo = arquivos[0]
        aux = pd.read_csv(arquivo, delimiter=';', index_col=None, decimal=',',names=['COT_DATA','COT_ID', 'tipo', 'moeda', 'COT_COMPRA', 'COT_VENDA', 'COT_COMPRA_USD', 'COT_VENDA_USD'], dtype={'COT_DATA':str,'COT_ID':str, 'tipo':str, 'moeda':str, 'COT_COMPRA':float, 'COT_VENDA':float, 'COT_COMPRA_USD':float, 'COT_VENDA_USD':float})
        arquivos.remove(arquivo)
        dados = pd.concat([dados, aux], ignore_index=True)
        
    for i in dados.index:
        dataFormatada = dados['COT_DATA'][i]
        dataFormatada = dataFormatada[-4:] + dataFormatada[2:4] + dataFormatada[:2]
        dados.at[i, 'COT_DATA'] = dataFormatada
        
    dadosFinal = dados[['COT_ID','COT_DATA','COT_COMPRA','COT_VENDA','COT_COMPRA_USD', 'COT_VENDA_USD']]
    
    texto = geraInsert(dadosFinal, 'tp_master.dbo.I_COTACOES' )
        
    return texto

def geraCotacoes(mes, ano, caminho):

    caminho += chr(47)

    executaCotacoes(mes, ano, caminho)
    
    arquivo = open(caminho + "cotacoes_" + ano + mes + ".sql", "w")

    arquivo.write(leArquivos(mes, ano, caminho))
    
    arquivo.close()
    
mes = '08'
ano = '2023'
caminho = 'c:\cotacoes\download'