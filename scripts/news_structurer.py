import os
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
from testing import format_json 

#importando api key
load_dotenv()
key = os.getenv("DEEPSEEK_API")
print(f"El api key es:\n{key}\n")

# Configura tu API key  
client = OpenAI(
    api_key=key,
    base_url="https://api.deepseek.com"
)

# Carga el archivo Excel
archivo_excel = "./scrap_diccionario.xlsx"  # Cambia esto por la ruta a tu archivo Excel
df = pd.read_excel(archivo_excel)

# Itera sobre las entradas y utiliza la API
def estructurar_noticia(prompt):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # Cambia el modelo si necesitas otro
            messages=[
                {'role': "system", "content": "Eres un storyteller geográfico profesional que sabe como dar una noticia siguiendo los paradigmas actuales de periodismo interactivo. Tu tarea es realizar un resúmen que sea entendible por un adolescente de 15 años de la noticia en español identificando los puntos, líneas, polígonos o áreas relevantes en la misma. No uses un tono tan informal, sino más bien accesible pero de periodista"},
                {"role":"user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

prompt_base = ""

with open("./prompts/prompt_simple.txt", "r", encoding="utf-8") as archivo:  # Cambia "archivo.txt" por la ruta a tu archivo
    prompt_base = archivo.read()  # Lee todo el contenido del arch

# Concatenar datos para la entrada
df['Entrada'] = "Título: "+ df['title'] + "\n autor: " + df['author'] + "\n Fecha:" + df['date'] + "\n url:"+ df['url'] + "\n Keyword: " + df['keyword'] + '\n' + df['content']

# Itera y procesa cada fila
resultados = []
prompts = prompt_base + "\n" + df['Entrada']
# prompts = prompts[-1:]
prompts = prompts[:30]

for idx, prompt in enumerate(prompts):  # Cambia 'Columna' por el nombre de la columna que contiene las entradas
    print(f'Estructurando noticia {idx+1}/{len(prompts)}')
    resultado = estructurar_noticia(prompt)
    resultados.append(resultado)
    print(f'Noticia {idx+1}/{len(prompts)} estructurada')

# prompts = [f"{prompt_base}\n{entrada}" for entrada in df['Entrada']]

# Using ThreadPoolExecutor to make parallel requests
# with concurrent.futures.ThreadPoolExecutor() as executor:
#     results = list(executor.map(estructurar_noticia, prompts))
format_json(resultados)

# # Agrega los resultados de vuelta al dataframe
# df['Resultados'] = results

# # print(results)
# # Guarda los resultados en un nuevo archivo Excel
# df.to_excel("noticias_keywords.xlsx", index=False)
