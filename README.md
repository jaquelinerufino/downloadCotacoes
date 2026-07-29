# Download de Cotações

Aplicação Python que baixa as cotações diárias de todas as moedas publicadas
pelo Banco Central do Brasil (BCB), consolida os arquivos CSV e gera comandos
SQL `INSERT`.

## Funcionalidades

- Validação de ano e mês, incluindo entradas inválidas e períodos futuros.
- Seleção apenas de dias úteis anteriores à data atual.
- Exclusão de fins de semana e feriados brasileiros.
- Download automatizado com Microsoft Edge e Selenium.
- Timeout e novas tentativas em downloads com falha.
- Encerramento garantido do navegador.
- Consolidação e formatação dos CSVs com pandas.
- Geração de SQL transacional com tratamento de `NULL` e textos com aspas.
- Limpeza somente dos CSVs processados na execução.
- Preservação dos arquivos quando ocorre uma falha.
- Logs e interface de linha de comando.
- Testes automatizados e análise estática.

## Estrutura

```text
.
├── src/
│   └── download_cotacoes/
│       ├── __init__.py       # Interface pública do pacote
│       ├── __main__.py       # Execução com python -m
│       ├── cli.py            # CLI e orquestração
│       ├── config.py         # Configurações e validação do ambiente
│       └── quotations.py     # Datas, download, CSV e geração de SQL
├── main.py                   # Entrada compatível para execução local
├── tests/                    # Testes automatizados
├── notebooks/                # Notebooks históricos
├── legacy/                   # Implementações antigas
├── .github/
│   ├── dependabot.yml        # Atualizações automáticas de dependências
│   └── workflows/security.yml # Testes e auditoria no GitHub Actions
├── .env.example              # Exemplo de configuração
├── pyproject.toml            # Pacote, CLI, pytest e Ruff
├── requirements.txt          # Dependências da aplicação
└── requirements-dev.txt      # Dependências de desenvolvimento
```

## Pré-requisitos

- Python 3.10 ou superior.
- Microsoft Edge instalado.
- Acesso à internet.

Versões recentes do Selenium utilizam o Selenium Manager para localizar ou
obter um driver compatível. Se isso não funcionar no ambiente, instale o Edge
WebDriver correspondente e deixe-o disponível no `PATH`.

## Instalação

```bash
git clone <URL_DO_REPOSITORIO>
cd downloadCotacoes
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows, ative o ambiente com:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Configuração

Copie o exemplo:

```bash
cp .env.example .env
```

Configuração padrão:

```dotenv
DEF_DIRECTORY=./downloads
EDGE_ARGUMENTS=--headless=new
DOWNLOAD_TIMEOUT=60
DOWNLOAD_RETRIES=2

CSV_FILE_NAME=cotacaoTodasAsMoedas_
FILE_NAME=cotacoes_
TABLE=tp_master.dbo.I_COTACOES

DF_COLUMNS=COT_DATA,COT_ID,TIPO,MOEDA,COT_COMPRA,COT_VENDA,COT_COMPRA_USD,COT_VENDA_USD
FINAL_COLUMNS=COT_ID,COT_DATA,COT_COMPRA,COT_VENDA,COT_COMPRA_USD,COT_VENDA_USD
```

| Variável | Descrição |
| --- | --- |
| `DEF_DIRECTORY` | Diretório dos CSVs e do SQL; é criado automaticamente |
| `EDGE_ARGUMENTS` | Argumentos do Edge separados por vírgula |
| `DOWNLOAD_TIMEOUT` | Limite em segundos para cada tentativa |
| `DOWNLOAD_RETRIES` | Novas tentativas após a primeira |
| `CSV_FILE_NAME` | Prefixo esperado nos CSVs do BCB |
| `FILE_NAME` | Prefixo do arquivo SQL |
| `TABLE` | Tabela de destino dos comandos `INSERT` |
| `DF_COLUMNS` | Colunas do CSV, na ordem de leitura |
| `FINAL_COLUMNS` | Colunas incluídas no SQL, na ordem desejada |

O `.env` está ignorado pelo Git. Não coloque credenciais nele sem também
proteger adequadamente o ambiente onde a aplicação será executada.

## Uso

Passe o período na linha de comando:

```bash
python main.py --ano 2024 --mes 1
```

Depois de instalar o projeto com `pip install -e .`, também é possível usar:

```bash
download-cotacoes --ano 2024 --mes 1
```

Ou executar o pacote diretamente:

```bash
PYTHONPATH=src python -m download_cotacoes --ano 2024 --mes 1
```

Ou execute sem argumentos para responder às perguntas:

```bash
python main.py
```

Para preservar os CSVs depois da geração:

```bash
python main.py --ano 2024 --mes 1 --manter-csv
```

Para logs detalhados:

```bash
python main.py --ano 2024 --mes 1 --verbose
```

O resultado segue o padrão `cotacoes_AAAAMM.sql` e é salvo em
`DEF_DIRECTORY`. Exemplo:

```text
downloads/cotacoes_202401.sql
```

Se qualquer data falhar, a geração do SQL é interrompida e os CSVs já baixados
são preservados para diagnóstico ou uma nova execução. Arquivos válidos já
existentes são reutilizados.

## Desenvolvimento

Instale as dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Execute os testes:

```bash
pytest
```

Execute a análise estática:

```bash
ruff check .
ruff format --check .
```

Audite as dependências:

```bash
pip-audit -r requirements.txt
```

Os diretórios `legacy/` e `notebooks/` guardam código histórico e não fazem
parte da análise do Ruff.

O workflow `Qualidade e segurança` executa testes, Ruff e `pip-audit` em cada
pull request, atualização da branch principal e semanalmente. O Dependabot
também verifica, toda semana, dependências Python e GitHub Actions.

## Fluxo

1. `Settings.from_env()` carrega, valida e normaliza as configurações.
2. `business_dates()` identifica os dias que podem ser consultados.
3. `download()` baixa cada CSV com timeout e novas tentativas.
4. `read_files()` consolida os dados e formata datas e códigos.
5. `write_sql()` cria um arquivo entre `BEGIN` e `COMMIT`.
6. `clear_files()` remove apenas os CSVs utilizados, salvo quando
   `--manter-csv` é informado.

## Fonte dos dados

Os arquivos são obtidos no
[Histórico de Cotações do Banco Central do Brasil](https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes).

O download ainda depende da página e de seus elementos HTML. Mudanças no site
do BCB podem exigir atualização dos seletores Selenium.

## Licença

Este repositório não possui uma licença definida.
