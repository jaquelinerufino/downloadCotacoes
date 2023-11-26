from datetime import datetime, timedelta
from environs import Env
import glob
import os

env = Env()

env.read_env()

class Quotations:
    def __init__(self):
        pass
    
    def removeInvalidDates(self, year, month, error):
        import holidays
        import calendar
        
        holidays = holidays.BR()
        
        errorMessage = ""
        dates = []
        monthYear = "/" + month + "/" + year
        
        if not error:
            year = int(year)
            month = int(month)
            
            today = datetime.now().date()

            calendar = calendar.monthcalendar(year, month)
            
            for i in calendar:
                for j in i:
                    if (j > 0):
                        date = str(j) + monthYear
                        date = datetime.strptime(date,"%d/%m/%Y").date()
                
                        if (date.weekday() != 5) and (date.weekday() != 6) and (date not in holidays) and (date < today): 
                            dates.append(date)
                    
        return dates
    
    
    def validatingDates(self, year, month):
        year = int(year)
        month = int(month)
        
        today = datetime.now().date()
        
        error = False
        errorMessage = ""
        
        if today.year < year:
            errorMessage = "Erro: Não é possível baixar cotações de anos futuros."
            error = True
        elif today.year == year and today.month < month:
            errorMessage = "Erro: Não é possível baixar cotações de meses futuros."
            error = True
        else:
            error = False
            
        return error, errorMessage
        
    def downloads(self, date, directory):
        
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.edge import options as EdgeOptions
        import time
        import os.path
        
        options = EdgeOptions.Options()
    
        options.add_argument(env("EDGE_ARGUMENTS"))
            
        options.use_chromium = True
            
        options.add_experimental_option("prefs", {"download.default_directory": directory})
        
        driver = webdriver.Edge(options= options)
        
        # baixa o arquivo
        try:
            driver.get("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes")
            
            cookiesButton = "/html/body/app-root/bcb-cookies/div/div/div/div/button[2]"

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, cookiesButton))).click()
            
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
            driver.switch_to.frame(iframe)
            
            radioButton = driver.find_element(By.XPATH,"//input[@type='radio'][@value='2']")

            button = driver.find_element(By.XPATH,"//input[@type='submit']")
            
            radioButton.click()
            
            beginDate = driver.find_element(By.ID, "DATAINI")
            beginDate.clear()
            beginDate.send_keys(date)
            
            driver.implicitly_wait(0.5)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button)).click()
            
            link = driver.find_element(By.PARTIAL_LINK_TEXT, "CSV")
            link.click()
            
            fileDirectory = directory + env("CSV_FILE_NAME") + date + ".csv"

            while not os.path.exists(fileDirectory):
                time.sleep(1)
                
            driver.quit()
            
        except Exception as e:
            message = "Ocorreu um erro com a data {}: {}".format(date, e)
            error = True
        else:
            message = "Dados do dia {} salvos com sucesso no diretorio {}".format(date, fileDirectory)
            error = False
            
        return error, message

    def readFiles(self, directory):
        import pandas as pd
        import glob

        directoryExt = directory + '*.csv'
        files = []
        file = ''
        csvColumns = env.list("DF_COLUMNS")
        csvDtypes = env.dict("DF_DICT")
        finalColumns = env.list("FINAL_COLUMNS")
        
        data = pd.DataFrame(columns=csvColumns)
        
        fileDirectory = glob.glob(directoryExt)
        
        for i in fileDirectory:
            files.append(i) 
            
        files.sort()
        
        while len(files) > 0:
            file = files[0]
            df = pd.read_csv(file, delimiter=';', index_col=None, decimal=',', names=csvColumns, dtype=csvDtypes)
            files.remove(file)
            
            if data.empty:
                data = df.copy()
            else:
                data = pd.concat([data, df], ignore_index=True)
        for i in data.index:    
            
            formatedDate = data["COT_DATA"][i]
            formatedDate = formatedDate[-4:] + formatedDate[2:4] + formatedDate[:2]
            data.at[i, "COT_DATA"] = formatedDate
            
            countryCode = data["COT_ID"][i]
            countryCode = countryCode.zfill(3)
            data.at[i, "COT_ID"] = countryCode
        
        data = data[finalColumns]    
            
        return data
    
    def writeSQL(self, data):
        dbTable = env("TABLE")
        fileName = env("FILE_NAME")

        file = open(directory + fileName + year + month + ".sql", "w")

        insert = "INSERT INTO {} (".format(dbTable)
        columns = str(list(files.columns))[1:-1]
        columns = re.sub(r"\'", "", columns)
        values = ""

        for row in data.itertuples(index=False, name=None):
            values += insert + columns + ") values "
            values += re.sub(r"nan", "null", str(row))
            values += "\n"

        file.write(values[:-2])

        file.close()
    
    def clearFiles(self, directory):
        
        directoryExt = directory + '*.csv'
        
        fileDirectory = glob.glob(directoryExt)
        
        for file in fileDirectory:
            os.remove(file)