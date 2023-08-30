def geraCotacoes(mes, ano, caminho):

    caminho += chr(47)

    executaCotacoes(mes, ano, caminho)
    
    arquivo = open(caminho + "cotacoes_" + ano + mes + ".sql", "w")

    arquivo.write(leArquivos(mes, ano, caminho))
    
    arquivo.close()