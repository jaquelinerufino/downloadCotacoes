def geraCotacoes(mes, ano, caminho):

    from functions import executaCotacoes, leArquivos

    caminho += chr(47)

    executaCotacoes.executaCotacoes(mes, ano, caminho)
    
    arquivo = open(caminho + "cotacoes_" + ano + mes + ".sql", "w")

    arquivo.write(leArquivos.leArquivos(mes, ano, caminho))
    
    arquivo.close()