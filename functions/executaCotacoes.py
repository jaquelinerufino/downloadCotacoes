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