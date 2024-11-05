from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import re
import numpy as np

app = FastAPI()

def clean_name(name):
    # Converte para string e remove caracteres especiais e emojis, caso seja uma string
    if isinstance(name, str):
        return re.sub(r'[^\w\s]', '', name)
    return ""  # Retorna vazio se não for string

def format_phone(phone):
    # Converte para string se for um número, remove tudo que não é número e aplica o código do país
    if pd.notnull(phone):
        phone = re.sub(r'\D', '', str(int(phone)) if isinstance(phone, float) else str(phone))
        if len(phone) == 11:  # se já estiver no formato com 11 dígitos
            return f"55{phone}"
    return ""  # Retorna vazio se for nulo ou não for possível formatar

@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    etiqueta_nome: str = Form(...),
    num_grupos: int = Form(...)
):
    try:
        # Lê o arquivo Excel
        print("Iniciando leitura do arquivo...")
        df = pd.read_excel(file.file)
        print("Arquivo lido com sucesso. Colunas disponíveis:", df.columns)

        # Verifica se as colunas necessárias estão presentes
        if 'NOME' not in df.columns or 'TELEFONE' not in df.columns:
            raise HTTPException(status_code=400, detail="O arquivo precisa conter as colunas 'NOME' e 'TELEFONE'.")

        # Seleciona as colunas necessárias e renomeia-as
        print("Selecionando colunas necessárias...")
        df = df[['NOME', 'TELEFONE']].copy()
        
        # Limpa a coluna NOME e TELEFONE
        print("Limpando a coluna NOME e formatando a coluna TELEFONE...")
        df['NOME'] = df['NOME'].apply(clean_name)
        df['TELEFONE'] = df['TELEFONE'].apply(format_phone)

        # Adiciona a coluna ETIQUETA com grupos
        print("Adicionando a coluna ETIQUETA...")
        etiquetas = [f"{etiqueta_nome}_G{i+1}" for i in range(num_grupos)]
        df['ETIQUETA'] = etiquetas * (len(df) // num_grupos) + etiquetas[:len(df) % num_grupos]
        
        # Salva o arquivo processado
        output_file = "processed_file.xlsx"
        print("Salvando o arquivo processado...")
        df.to_excel(output_file, index=False)
        print("Arquivo processado e salvo com sucesso.")

        return FileResponse(output_file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=output_file)
    
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar o arquivo: {e}")
