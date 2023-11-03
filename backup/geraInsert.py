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