from datetime import datetime, timedelta
import calendar

class Cotacoes:
    def __init__(self):
        pass
    
    def removeDataInvalida(self, ano, mes):
        import holidays
        
        feriados = holidays.BR()
        
        erro = False
        mensagemErro= ""
        datas = []
        mesAno = "/" + mes + "/" + ano

        ano = int(ano)
        mes = int(mes)
        
        hoje = datetime.now().date()
        if hoje.year < ano:
            mensagemErro = "Erro: Não é possível baixar cotações de anos futuros."
            erro = True
        elif hoje.year == ano and hoje.month < mes:
            mensagemErro = "Erro: Não é possível baixar cotações de meses futuros."
            erro = True
        
        if not erro:

            calendario = calendar.monthcalendar(ano, mes)
            
            for i in calendario:
                for j in i:
                    if (j > 0):
                        data = str(j) + mesAno
                        data = datetime.strptime(data,"%d/%m/%Y").date()
                
                        if (data.weekday() != 5) and (data.weekday() != 6) and (data not in feriados) and (data < hoje): 
                            datas.append(data)
                    
        return erro, mensagemErro, datas
    
    
    def validacaoData(self, datas):
        
        hoje = datetime.now().date()
        diaInicial = datas[0]
        erro = False
        
        if hoje.year < ano:
            mensagemErro = "Erro: Não é possível baixar cotações de anos futuros."
            erro = True
        elif hoje.year == ano and hoje.month < mes:
            mensagemErro = "Erro: Não é possível baixar cotações de meses futuros."
            erro = True
        else:
            mensagemErro = "Data inválida"
            erro = True
            
        if erro:
            return erro, mensagemErro
        
    def downloadCotacoes(self, data, diretorio):
        
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.edge import options as EdgeOptions
        import time
        import os.path
        
        options = EdgeOptions.Options()
    
        options.add_argument("--headless=new")
            
        options.use_chromium = True
            
        options.add_experimental_option("prefs", {"download.default_directory": diretorio})
        
        driver = webdriver.Edge(options= options)
        
        # baixa o arquivo
        try:
            driver.get("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes")
            
            botaoCookies = "/html/body/app-root/bcb-cookies/div/div/div/div/button[2]"

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, botaoCookies))).click()
            
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
            driver.switch_to.frame(iframe)
            
            radioButton = driver.find_element(By.XPATH,"//input[@type='radio'][@value='2']")

            botao = driver.find_element(By.XPATH,"//input[@type='submit']")
            
            radioButton.click()
            
            datainicial = driver.find_element(By.ID, "DATAINI")
            datainicial.clear()
            datainicial.send_keys(data)
            
            driver.implicitly_wait(0.5)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(botao)).click()
            
            link = driver.find_element(By.PARTIAL_LINK_TEXT, "CSV")
            link.click()
            
            diretorioArquivo = caminho + "cotacaoTodasAsMoedas_" + data + ".csv"

            while not os.path.exists(diretorioArquivo):
                time.sleep(1)
                
            driver.quit()
        except Exception as e:
            mensagemResultado = "Ocorreu um erro com a data {}: {}".format(data, e)
            erro = True
        else:
            mensagemResultado = "Dados do dia {} salvos com sucesso no diretorio {}".format(data, diretorioArquivo)
            erro = False
            
        return erro, mensagemResultado

    def leituraArquivos(self, diretorio):
        import pandas as pd
        import glob

        diretorioExtensao = diretorio + '*.csv'
        arquivos = []
        arquivo = ''
        dados = pd.DataFrame(columns=['COT_DATA','COT_ID', 'tipo', 'moeda', 'COT_COMPRA', 'COT_VENDA', 'COT_COMPRA_USD', 'COT_VENDA_USD'])
        
        caminhoArquivos = glob.glob(caminhoExtensao)
        
        for i in caminhoArquivos:
            #arquivos.append(i.replace(caminho[:caminho[:-1].rfind('/')+ 1] , '')) 
            arquivos.append(i) 
            
        arquivos.sort()
        
        while len(arquivos) > 0:
            arquivo = arquivos[0]
            aux = pd.read_csv(arquivo, delimiter=';', index_col=None, decimal=',',names=['COT_DATA','COT_ID', 'tipo', 'moeda', 'COT_COMPRA', 'COT_VENDA', 'COT_COMPRA_USD', 'COT_VENDA_USD'], dtype={'COT_DATA':str,'COT_ID':str, 'tipo':str, 'moeda':str, 'COT_COMPRA':float, 'COT_VENDA':float, 'COT_COMPRA_USD':float, 'COT_VENDA_USD':float})
            arquivos.remove(arquivo)
            dados["COT_ID"] = dados["COT_ID"].astype(str).str.zfill(3)
            dados = pd.concat([dados, aux], ignore_index=True)