import requests
import urllib3
import time
import sys
import sys
import pandas as pd
import datetime
import openpyxl
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Adiciona um diretório ao sys.path para permitir importação de módulos externos
sys.path.append(r"C:\Users\jcostaya\OneDrive - Johnson Controls\Documentos\App CPNJ\Code")

# Importa a função personalizada para executar consultas no banco e retornar DataFrame
from banco_de_dados import df_func

# Define a consulta SQL para buscar clientes com CNPJ completo e situação ativa
query = '''
WITH Base_CNPJ AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY IdCliente) AS ID
        ,IdCliente
        ,NrCNPJ_CPF
    FROM Clientes
    WHERE LEN(NrCNPJ_CPF) = 18 
    AND IdSituacao IN (1, 11, 17, 20)
    )
SELECT * FROM Base_CNPJ
WHERE ID BETWEEN 4001 AND 5000
'''

# Executa a consulta e armazena os resultados em um DataFrame
df = df_func(query)
# Desabilita avisos SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuração da sessão HTTP para reaproveitar conexões
session = requests.Session()

retry_strategy = Retry(
    total=3,
    backoff_factor=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)
session.mount("http://", adapter)

# Lista para armazenar resultados
resultados = []

# Total de registros
total_registros = len(df)

# Itera sobre cada cliente
for indice, (_, row) in enumerate(df.iterrows(), start=1):

    id_cliente = row["IdCliente"]

    cnpj_ = (
        row["NrCNPJ_CPF"]
        .replace(".", "")
        .replace("/", "")
        .replace("-", "")
    )

    url_cnpja = f"https://open.cnpja.com/office/{cnpj_}"

    print(f"[{indice}/{total_registros}] Consultando CNPJ: {cnpj_}")

    try:

        response = session.get(
            url_cnpja,
            verify=False,
            timeout=30
        )

        if response.status_code == 200:

            dados = response.json()

            cnpj_formatado = dados.get(
                "taxId",
                "CNPJ não encontrado"
            )

            situacao_cnpj = dados.get(
                "status",
                {}
            ).get(
                "text",
                "Desconhecida"
            )

            print(f"CNPJ: {cnpj_formatado}")
            print(f"Situação: {situacao_cnpj}")

            resultados.append({
                "IdCliente": id_cliente,
                "CNPJ": cnpj_formatado,
                "Situação": situacao_cnpj
            })

        elif response.status_code == 429:

            print(
                "Erro 429 - Limite de requisições atingido. "
                "Aguardando 60 segundos..."
            )

            time.sleep(60)

            resultados.append({
                "IdCliente": id_cliente,
                "CNPJ": cnpj_,
                "Situação": "Erro 429"
            })

        else:

            resultados.append({
                "IdCliente": id_cliente,
                "CNPJ": cnpj_,
                "Situação": f"Erro {response.status_code}"
            })

    except Exception as e:

        resultados.append({
            "IdCliente": id_cliente,
            "CNPJ": cnpj_,
            "Situação": f"Erro inesperado: {str(e)}"
        })

# Fecha a sessão HTTP
session.close()

# Converte resultados em DataFrame
df_resultados = pd.DataFrame(resultados)

# Nome do Excel
data_hora = datetime.datetime.now()

arquivo_excel = (
    f"cnpj_{data_hora.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
)

# Exporta para Excel
df_resultados.to_excel(
    arquivo_excel,
    index=False,
    engine="openpyxl"
)

print(f"\nPlanilha gerada com sucesso: {arquivo_excel}")
print(f"Total processado: {len(df_resultados)} registros")