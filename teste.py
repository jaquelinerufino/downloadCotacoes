data = '01092023'
caminho = '/Users/jaquelinerufino/Desktop/Estudos/cotacoes/data'

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
    
options.add_argument("--headless=new")
        
options.use_chromium = True
        
options.add_experimental_option("prefs", {"download.default_directory": caminho})
    
driver = webdriver.Edge(options = options)
    
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