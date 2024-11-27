from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import re
from tempfile import NamedTemporaryFile
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()


# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite requisições de qualquer origem. Para maior segurança, você pode especificar o IP e porta do seu front-end.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_name(name):
    return re.sub(r'[^\w\s]', '', name) if isinstance(name, str) else ""

def format_phone(phone):
    if pd.notnull(phone):
        phone = re.sub(r'\D', '', str(int(float(phone))) if isinstance(phone, (float, int)) else str(phone))
        if len(phone) == 13 and phone.startswith("55"):
            return phone
        if len(phone) == 11:
            return f"55{phone}"
        if len(phone) == 8:
            return f"55859{phone}"
        if len(phone) == 9:
            return f"5585{phone}"
    return ""

def find_column(df, options):
    for option in options:
        if option in df.columns:
            return option
    return None

def distribuir_aquecimento(total_pessoas, etiqueta_nome):
    # Definir o limite para cada grupo de aquecimento
    limites = [30, 30, 60, 60, 90, 90, 180]
    etiquetas = []
    grupo_index = 1
    pessoas_contadas = 0
    
    for i in range(total_pessoas):
        # Se o limite do grupo atual for atingido, passa para o próximo
        if pessoas_contadas >= limites[min(grupo_index - 1, len(limites) - 1)]:
            grupo_index += 1
            pessoas_contadas = 0
        
        etiquetas.append(f"{etiqueta_nome}_G{grupo_index}")
        pessoas_contadas += 1
    
    return etiquetas

@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    etiqueta_nome: str = Form(...),
    num_grupos: int = Form(...),
    aquecimento: bool = Form(False)  # Parâmetro adicional para ativar o aquecimento
):
    try:
        # Carregar o arquivo Excel
        df = pd.read_excel(file.file)

        # Buscar as colunas necessárias
        nome_column = find_column(df, ["NOME", "Nome", "Cliente", "CLIENTE"])
        telefone_column = find_column(df, ["TELEFONE", "Telefone", "Celular"])

        if nome_column is None or telefone_column is None:
            raise HTTPException(
                status_code=400,
                detail="O arquivo precisa conter uma coluna para o nome (NOME, Nome, Cliente, CLIENTE) e para o telefone (TELEFONE, Telefone, Celular)."
            )

        # Processar as colunas encontradas
        df = df[[nome_column, telefone_column]].copy()
        df['NOME'] = df[nome_column].apply(clean_name)
        df['TELEFONE'] = df[telefone_column].apply(format_phone)

        # Remover duplicatas com base na coluna TELEFONE
        df = df.drop_duplicates(subset='TELEFONE')

        # Aplicar a lógica de etiquetas
        if aquecimento:
            # Usar a função de distribuição de aquecimento
            df['ETIQUETA'] = distribuir_aquecimento(len(df), etiqueta_nome)
        else:
            # Usar a lógica padrão de agrupamento
            etiquetas = [f"{etiqueta_nome}_G{(i // num_grupos) + 1}" for i in range(len(df))]
            df['ETIQUETA'] = etiquetas

        # Selecionar as colunas finais
        df = df[['NOME', 'TELEFONE', 'ETIQUETA']]

        # Salvar o arquivo tratado em um arquivo temporário
        with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            df.to_excel(tmp.name, index=False)
            treated_filename = tmp.name

        return FileResponse(
            treated_filename, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            filename=f"[TRATADO]{file.filename}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
