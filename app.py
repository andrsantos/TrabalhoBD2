from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os

# Importe as bibliotecas necessárias
import openai
import psycopg2

# Defina aqui o nome do repositório e a branch
repo_name = "andrsantos/API-Rest-/blob"
branch = "main"

# receber o código do repositório através da API do github
code = open(f"https://github.com/{repo_name}/{branch}/README.md", "r").read()

# agora seŕa necessário usar a API da openAI para gerar o embedding do código
embeddings = openai.Embeddings()
embedding = embeddings.embed_text(code)

# estabelencendo conexão com o banco de dados pgvector
conn = psycopg2.connect("host=localhost dbname=pgvector user=postgres password=test")

# criando uma tabela para armazenar embeddings
cur = conn.cursor()
cur.execute("""
CREATE TABLE embeddings (
 id serial PRIMARY KEY,
 repo_name text NOT NULL,
 branch text NOT NULL,
 embedding jsonb NOT NULL
);
""")

# fazendo o insert do embedding na tabela
cur.execute("""
INSERT INTO embeddings (repo_name, branch, embedding)
VALUES (%s, %s, %s);
""", (repo_name, branch, embedding))

# salvando as alterações no banco
conn.commit()

# fechando a conexão
conn.close()

# este é o método para fazer query
# deve ser passada uma conexão e uma consulta em sql
def query(conn, sql):  
  cur = conn.cursor()
  cur.execute(sql)
  return cur

# este é método que permite fazer queries por métodos
def query_by_method(conn, method):
  sql = """
    SELECT *
    FROM embeddings
    WHERE embedding @> '{method}'
  """.format(method=method)

  cur = conn.cursor()
  cur.execute(sql)
  return cur


# exemplo de como fazer a query
cur = query(conn, "SELECT * FROM embeddings")

# itere sobre os resultados
for row in cur:
  print(row[0], row[1], row[2])

# fecha a conexão
conn.close()


# faça uma query para pesquisar com o método "getFatorial()" por exemplo
cur = query_by_method(conn, "getFatorial()")

# itere sobre os resultados
for row in cur:
  print(row[0], row[1], row[2])

# fecha a conexão
conn.close()

