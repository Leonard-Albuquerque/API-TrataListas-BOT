from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import re
from tempfile import NamedTemporaryFile

app = FastAPI()

def clean_name(name):
    # Remove caracteres especiais, mantendo letras e espaços
    return re.sub(r'[^\w\s]', '', name) if isinstance(name, str) else ""

def format_phone(phone):
    if pd.notnull(phone):
        # Converte para string e remove caracteres não numéricos
        phone = re.sub(r'\D', '', str(int(float(phone))) if isinstance(phone, (float, int)) else str(phone))
        
        # Se o número já está no formato correto (13 dígitos com o código do país e DDD)
        if len(phone) == 13 and phone.startswith("55"):
            return phone  # Retorna o número como está
        
        # Caso contrário, aplica a formatação padrão para números com 11 dígitos (DDD + número)
        if len(phone) == 11:
            return f"55{phone}"
    
    # Retorna uma string vazia caso o número não esteja no formato adequado
    return ""

@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    etiqueta_nome: str = Form(...),
    num_grupos: int = Form(...)
):
    try:
        # Carregar o arquivo Excel e validar colunas
        df = pd.read_excel(file.file)
        if 'NOME' not in df.columns or 'TELEFONE' not in df.columns:
            raise HTTPException(status_code=400, detail="O arquivo precisa conter as colunas 'NOME' e 'TELEFONE'.")

        # Processar colunas e tratar os dados
        df = df[['NOME', 'TELEFONE']].copy()
        df['NOME'] = df['NOME'].apply(clean_name)
        df['TELEFONE'] = df['TELEFONE'].apply(format_phone)

        # Adiciona a coluna ETIQUETA com agrupamento por grupos
        etiquetas = [f"{etiqueta_nome}_G{(i // num_grupos) + 1}" for i in range(len(df))]
        df['ETIQUETA'] = etiquetas

        # Salvar o arquivo tratado em um arquivo temporário
        with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            df.to_excel(tmp.name, index=False)
            treated_filename = tmp.name

        # Retorna o arquivo processado e salva no diretório temporário
        return FileResponse(
            treated_filename, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            filename=f"[TRATADO]{file.filename}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
