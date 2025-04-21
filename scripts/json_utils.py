import re
import json
import pandas as pd

def export_json_to_df(json_txt:str):
    # Eliminar los marcadores ```json y ```
        json_text = re.sub(r'^```json|```$', '', json_txt, flags=re.MULTILINE).strip()
        
        # Eliminar comentarios (líneas que comienzan con //)
        texto_sin_comentarios = re.sub(r'^\s*\/\/.*', '', json_text, flags=re.MULTILINE)
        
        # Reemplazar caracteres problemáticos (tabulaciones y otros)
        texto_limpio = texto_sin_comentarios.replace('\t', ' ').replace('\r', '').replace('\n', ' ')
        
        # Eliminar múltiples espacios
        texto_limpio = re.sub(r' +', ' ', texto_limpio)
        print(texto_limpio)
        try:
            my_dict = json.loads(texto_limpio)
            return pd.DataFrame([my_dict])
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            err_start = max(e.pos-30, 0)
            err_end = min(e.pos-30, len(texto_limpio)-1)
            print(f"Texto problemático: '{texto_limpio[err_start:err_end]}'")
            return pd.DataFrame([{}])

def concat_df(current_df:pd.DataFrame, new_df: pd.DataFrame):
    return pd.concat([current_df, new_df])


def export_jsons_to_excel(jsons):
    result = []
    
    # with open("output.txt", "w") as txt_file:
    #     for line in jsons:
    #         txt_file.write(line + "!!!!!!") # works with any number of elements in a line
    
    for json_txt in jsons:
        # Eliminar los marcadores ```json y ```
        json_text = re.sub(r'^```json|```$', '', json_txt, flags=re.MULTILINE).strip()
        
        # Eliminar comentarios (líneas que comienzan con //)
        texto_sin_comentarios = re.sub(r'^\s*\/\/.*', '', json_text, flags=re.MULTILINE)
        
        # Reemplazar caracteres problemáticos (tabulaciones y otros)
        texto_limpio = texto_sin_comentarios.replace('\t', ' ').replace('\r', '').replace('\n', ' ')
        
        # Eliminar múltiples espacios
        texto_limpio = re.sub(r' +', ' ', texto_limpio)
        
        try:
            my_dict = json.loads(texto_limpio)
            result.append(my_dict)
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            print(f"Texto problemático: {texto_limpio[e.pos-30:e.pos+30]}")
            result.append({})
    df = pd.DataFrame(result)
    df.to_excel('estructuracion_keywords.xlsx', index=False)

