# from functions import geraCotacoes as func
from functions import Quotations
from datetime import datetime
from environs import Env
import pandas as pd
import glob
import re
import os

env = Env()
env.read_env()

quot = Quotations()

month = '12'
year = '2023'
directory = env("DEF_DIRECTORY")

directory += chr(47)

error, errorMessage = quot.validatingDates(year, month)
    
dates = quot.removeInvalidDates(year, month, error)
    
if error:
    print(errorMessage)
else:
    
    for date in dates:
    
        dateStr = date.strftime("%d%m%Y")
        
        error, message = quot.downloads(dateStr, directory)
    
        print(message)
        
    files = quot.readFiles(directory)
        
    quot.writeSQL(files)

    quot.clearFiles(directory)