from functions.classCotacoes import removeDataInvalida, validacaoData

def executaCotacoes(mes, ano, caminho):
    
    from functions import baixaCotacoes as func
    from datetime import datetime
    
    datas = classCotacoes.removeDataInvalida(ano, mes)

    erro = classCotacoes.validacaoData(datas).erro
    mensagemErro = classCotacoes.validacaoData(datas).mensagemErro

    print('Iniciando download: ' + str(datetime.now()))
    
    if erro:
        raise(mensagemErro)
    else:
        for data in datas:
    
            dataString = data.strftime("%d%m%Y")
            try:
                func.baixacotacoes(dataString, caminho)
            except Exception as e:
                print('Ocorreu um erro: ' + str(e))
            else:
                print('Arquivo finalizado com sucesso: {}'.format(data))
    
    print('baixaCotacoes executado: ' + str(datetime.now()) )
    