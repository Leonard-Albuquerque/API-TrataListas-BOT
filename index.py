from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import re
import os

app = FastAPI()

def clean_name(name):
  
    return re.sub(r'[^\w\s]', '', name) if isinstance(name, str) else ""

def format_phone(phone):
    
    if pd.notnull(phone):
        phone = re.sub(r'\D', '', str(int(phone)) if isinstance(phone, float) else str(phone))
        if len(phone) == 11:  
            return f"55{phone}"
    return ""

@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    etiqueta_nome: str = Form(...),
    num_grupos: int = Form(...)
):
    try:
      
        print("Iniciando leitura do arquivo...")
        df = pd.read_excel(file.file)
        print("Arquivo lido com sucesso. Colunas disponíveis:", df.columns)

      
        if 'NOME' not in df.columns or 'TELEFONE' not in df.columns:
            raise HTTPException(status_code=400, detail="O arquivo precisa conter as colunas 'NOME' e 'TELEFONE'.")

       
        print("Selecionando colunas necessárias...")
        df = df[['NOME', 'TELEFONE']].copy()
        
       
        print("Limpando a coluna NOME e formatando a coluna TELEFONE...")
        df['NOME'] = df['NOME'].apply(clean_name)
        df['TELEFONE'] = df['TELEFONE'].apply(format_phone)

      
        print("Adicionando a coluna ETIQUETA com agrupamento...")
        etiquetas = [f"{etiqueta_nome}_G{(i // num_grupos) + 1}" for i in range(len(df))]
        df['ETIQUETA'] = etiquetas
        
        
        original_filename = file.filename
        treated_filename = f"[TRATADO]{original_filename}"
        
       
        print(f"Salvando o arquivo processado como '{treated_filename}'...")
        df.to_excel(treated_filename, index=False)
        print("Arquivo processado e salvo com sucesso.")

        return FileResponse(treated_filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=treated_filename)
    
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar o arquivo: {e}")
