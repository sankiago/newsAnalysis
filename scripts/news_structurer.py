import sys
import os
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
from json_utils import concat_df,export_json_to_df

#importando api key
load_dotenv()
key = os.getenv("DEEPSEEK_API")
print(f"El api key es:\n{key}\n")

# Configura tu API key  
client = OpenAI(
    api_key=key,
    base_url="https://api.deepseek.com"
)

def file_in_sibling_folder(folder:str, file:str):
    base_dir = os.path.dirname(__file__)  # Directorio del script actual
    result = os.path.join(base_dir, "..", folder, file)
    result = os.path.abspath(result)
    return result

label = '25-abr'
archivo_excel = file_in_sibling_folder('outputs', f'{label}_extraction.xlsx') 
context_prompt = file_in_sibling_folder('prompts', 'context_noticia.txt') 
user_prompt = file_in_sibling_folder('prompts', 'prompt_simple.txt') 
output_path = file_in_sibling_folder('outputs', f'{label}_structured.xlsx') 
log_path = file_in_sibling_folder('outputs', f'{label}_structured_progress.txt') 

# Carga el archivo Excel
df = pd.read_excel(archivo_excel)

# Carga el contexto y el prompt
prompt_base = ""
contexto = ""
with open(context_prompt, "r", encoding="utf-8") as archivo:  
    contexto = archivo.read()
    
with open(user_prompt, "r", encoding="utf-8") as archivo:  
    prompt_base = archivo.read()


# Itera sobre las entradas y utiliza la API
def estructurar_noticia(prompt):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {'role': "system", "content": contexto},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# Concatenar datos para la entrada
df['Entrada'] = "Título: "+ df['title'] + "\n autor: " + df['author'] + "\n Fecha:" + df['date'] + "\n url:"+ df['url'] + "\n Keyword: " + df['keyword'] + '\n' + df['content']

# Itera y procesa cada fila
resultados = []
prompts = prompt_base + "\n" + df['Entrada']
# prompts = prompts[-1:]
# prompts = prompts[:30]


# Leer el índice de progreso
if os.path.exists(log_path):
    with open(log_path, "r") as f:
        start_index = int(f.read().strip())
else:   
    start_index = 0
    
# Si ya hay resultados parciales, cargarlos
if os.path.exists(output_path):
    df_noticias = pd.read_excel(output_path)
else:
    df_noticias = pd.DataFrame()

for idx in range(start_index, len(prompts)):
    print(f'Estructurando noticia {idx+1}/{len(prompts)}')
    prompt = prompts[idx]
    try:
        noticia = estructurar_noticia(prompt)
        df_noticia = export_json_to_df(noticia)
        df_noticias = concat_df(df_noticias, df_noticia)
        print(df_noticias)
        df_noticias.to_excel(output_path, index=False)
        print(f'Noticia {idx+1}/{len(prompts)} estructurada con éxito.\nResultados parciales en {output_path}')
    except Exception as e:
        sys.exit(f"Error al estructurar la noticia {idx} :\n    {e}")
        
print(f'\n{len(prompts)} noticias estructuradas con éxito, las noticias estructuradas se encuentran en: {output_path}')