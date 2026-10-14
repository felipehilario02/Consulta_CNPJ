import pandas as pd
import pyodbc

# Função para criar conexão com SQL Server usando autenticação do Windows
def create_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=10.67.99.10\\MSSQLSERVER2019;'
            'DATABASE=DATA_WAREHOUSE;'
            'Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

# Função para executar query e retornar DataFrame
def df_func(query_param):
    conn = create_connection()
    if conn:
        try:
            df = pd.read_sql(query_param, conn)
            return df
        except Exception as e:
            print(f"Erro ao executar a query: {e}")
            return None
        finally:
            conn.close()  # Fecha a conexão sempre
    else:
        print("Conexão não estabelecida.")
        return None

