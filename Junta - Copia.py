from pathlib import Path
import pandas as pd

# === Parâmetros ===
pasta = Path(r"C:\Users\jcostaya\Johnson Controls\ADT - Equipe Financeiro - Documentos\Zenvia\Relatório de Envios\WhatsApp Atualizado")
saida = Path(r"C:\Users\jcostaya\Johnson Controls\ADT - Equipe Financeiro - Documentos\Zenvia\Envios Zenvia .csv")
padrao = "*.csv"
sep = ";"                     
tem_header = True            
add_origem = True             
encodings_para_tentar = ["utf-8-sig", "cp1252", "latin1"] 

arquivos = sorted(pasta.glob(padrao))
if not arquivos:
    raise FileNotFoundError(f"Nenhum arquivo encontrado em {pasta} com padrão {padrao}")

dfs = []
for arq in arquivos:
    lido = False
    ultimo_erro = None
    for enc in encodings_para_tentar:
        try:
            df = pd.read_csv(
                arq, sep=sep, encoding=enc,
                header=0 if tem_header else None
            )
            lido = True
            break
        except UnicodeDecodeError as e:
            ultimo_erro = e
    if not lido:
        df = pd.read_csv(
            arq, sep=sep, encoding="cp1252",
            encoding_errors="replace",
            header=0 if tem_header else None
        )
        print(f"⚠️  {arq.name}: não foi possível decodificar perfeitamente. Caracteres problemáticos foram substituídos.")

    if add_origem:
        df["arquivo_origem"] = arq.name
    dfs.append(df)

resultado = pd.concat(dfs, ignore_index=True)
resultado.to_csv(saida, sep=sep, index=False, encoding="utf-8-sig")

print(f"✅ {len(arquivos)} arquivos unidos em: {saida}")