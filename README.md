
# API para Tratamento de Listas de Contatos em Excel

Esta API permite o processamento de listas de contatos em arquivos Excel (.xlsx) para adequar os dados ao uso com bots de WhatsApp. Ela realiza as seguintes funções:

- Extrai e limpa as colunas **NOME**, **TELEFONE**, e **ETIQUETA**.
- Remove caracteres especiais e emojis dos nomes.
- Formata os números de telefone para o formato `5585XXXXXXXX`.
- Agrupa os contatos por etiquetas, conforme o número de grupos especificado.
- Retorna o arquivo tratado em formato `.xlsx` com o nome original precedido de `[TRATADO]`.

## Requisitos

Para executar esta API, você precisará ter o Python instalado (versão 3.7 ou superior) e instalar as seguintes bibliotecas:

```bash
pip install fastapi pandas openpyxl uvicorn python-multipart
```

## Como Executar a API

1. **Clone o repositório** e navegue até a pasta onde o projeto está localizado:

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <PASTA_DO_PROJETO>
   ```

2. **Instale as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

   > **Nota**: Caso o arquivo `requirements.txt` não esteja presente, use o comando acima para instalar manualmente as dependências listadas.

3. **Execute o servidor FastAPI com o Uvicorn**:

   ```bash
   uvicorn index:app --reload
   ```

4. **Acesse a documentação interativa**:

   Após iniciar o servidor, acesse `http://127.0.0.1:8000/docs` no seu navegador para ver a documentação interativa (Swagger UI). Isso permitirá que você teste os endpoints diretamente.

## Como Utilizar a API

### Endpoint `/process`

- **Método**: `POST`
- **Descrição**: Recebe um arquivo Excel (.xlsx) e retorna um arquivo tratado com as colunas e formatos específicos.

#### Parâmetros

1. `file`: Arquivo `.xlsx` contendo a lista de contatos. Este arquivo deve incluir as colunas `NOME` e `TELEFONE`.
2. `etiqueta_nome`: Nome base para as etiquetas, que será seguido por um número de grupo (exemplo: `Clientes`).
3. `num_grupos`: Número de contatos por grupo. Por exemplo, se você informar `25`, os primeiros 25 contatos receberão a etiqueta `Clientes_G1`, os próximos 25 `Clientes_G2`, e assim por diante.

#### Exemplo de Uso

1. Acesse `http://127.0.0.1:8000/docs` para abrir a interface interativa.
2. No endpoint `/process`, clique em "Try it out".
3. Faça upload do arquivo `.xlsx` em `file`.
4. Preencha `etiqueta_nome` com o nome da etiqueta desejado (ex.: `Clientes`).
5. Preencha `num_grupos` com o número de contatos por grupo (ex.: `25`).
6. Clique em "Execute" para processar o arquivo.

Após a execução, você receberá um link para baixar o arquivo tratado, que terá o mesmo nome do arquivo original, precedido de `[TRATADO]`.

### Estrutura Esperada do Arquivo de Entrada

O arquivo `.xlsx` de entrada deve conter pelo menos as seguintes colunas:

- **NOME**: Nome do contato. A API remove caracteres especiais e emojis desta coluna.
- **TELEFONE**: Número de telefone do contato. A API formata este número para o padrão `5585XXXXXXXX`.

### Exemplo de Nome de Arquivo Retornado

Se o arquivo enviado for `lista_contatos.xlsx`, o arquivo retornado será `[TRATADO]lista_contatos.xlsx`.

## Exemplo de Requisição com `curl`

Caso prefira testar a API usando `curl`, veja um exemplo de requisição:

```bash
curl -X 'POST'   'http://127.0.0.1:8000/process'   -H 'accept: application/json'   -H 'Content-Type: multipart/form-data'   -F 'file=@caminho/para/o_arquivo.xlsx'   -F 'etiqueta_nome=Clientes'   -F 'num_grupos=25'
```

## Erros Comuns

- **400 - Bad Request**: Este erro ocorre se o arquivo enviado não contém as colunas `NOME` e `TELEFONE`.
- **500 - Internal Server Error**: Um erro interno indica problemas com o processamento do arquivo. Verifique o formato do arquivo e os dados contidos nas colunas.

