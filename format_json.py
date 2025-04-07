import json
import re
import pandas as pd

def format_json(json_txt):
    json_text = json_txt[8:-3]
    texto_sin_comentarios = re.sub('\/\/.*', '', json_text, flags=re.MULTILINE)
    my_dict =  json.loads(texto_sin_comentarios)
    return(my_dict)


# def str_to_df(str):
#     structured_data = {}
#     data = format_json(str)
    
#     structured_data.update({
#         'Sección': 'Resumen',
#         'Contenido': data['abstract']['details'],
#         'Ubicación': data['abstract']['location']['label'],
#         'Tipo Geométrico': data['abstract']['location']['type'],
#         'Coordenadas': '; '.join([f"{lat}, {lon}" for lat, lon in data['abstract']['location']['coordinates']])
#     })
    
#     # Agregar cuerpo
#     for section in data['body']:
#         structured_data.update({
#             'Sección': section['section'],
#             'Contenido': section['content'],
#             'Ubicación': section['location']['label'],
#             'Tipo Geométrico': section['location']['type'],
#             'Coordenadas': '; '.join([f"{lat}, {lon}" for lat, lon in section['location']['coordinates']])
#         })

#     # Crear DataFrame
#     df = pd.DataFrame(structured_data)

#     return df

def str_to_df(json_str):
    data = format_json(json_str)  # Asumo que esta función parsea el JSON
    
    # Diccionario base con el resumen
    row = {
        'Título': data['title'],
        'Subtítulo': data['subtitulo'],
        'Sistema_Coordenadas': data['coordinate_system'],
        'Resumen_Contenido': data['abstract']['details'],
        'Resumen_Ubicación': data['abstract']['location'].get('label',''),
        'Resumen_Tipo_Geométrico': data['abstract']['location'].get('type',''),
        # 'Resumen_Coordenadas': '; '.join([f"{lat},{lon}" for lat, lon in data['abstract']['location']['coordinates']]),
        'Resumen_Coordenadas': data['abstract']['location'].get('coordinates',''),
    }
    
    # Procesar cada sección del cuerpo
    for i, section in enumerate(data['body'], 1):
        prefix = f"Sección_{i}_"
        if section is not None:
            row.update({
                prefix + 'Nombre': section['section'],
                prefix + 'Contenido': section['content'],
                prefix + 'Ubicación': section.get('location', {}).get('label', ''),
                # prefix + 'Ubicación': section['location'].get('label', ''),
                prefix + 'Tipo_Geométrico': section.get('location',{}).get('type',''),
                # prefix + 'Coordenadas': '; '.join([f"{lat},{lon}" for lat, lon in section['location']['coordinates']])
                'Resumen_Coordenadas': data['abstract'].get('location',{}).get('coordinates',''),
            })
    
    return pd.DataFrame([row])  # Notar el [row] para crear un DataFrame de 1 fila

# # Ejemplo de uso
# df_final = pd.DataFrame()
# nuevo_registro = str_to_df(json_str)
# df_final = pd.concat([df_final, nuevo_registro], ignore_index=True)


    
# def main():
#     df = pd.read_excel('noticias_estructuradas_pipelines.xlsx')
#     print(type(df))
#     jsons = df['Resultados'].to_list()
#     for json_str in jsons:
#         new_row = str_to_df(json_str)
#         # df.append(row
#         pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
#     df.to_excel('excel_friendly')

def main():
    # Leer el archivo existente
    df = pd.read_excel('noticias_estructuradas_pipelines.xlsx')
    
    # Lista para almacenar todos los nuevos registros
    nuevos_registros = []
    
    # Procesar cada JSON
    for json_str in df['Resultados'].tolist():
        nuevo_df = str_to_df(json_str)
        nuevos_registros.append(nuevo_df)
    
    # Concatenar todos los nuevos registros
    if nuevos_registros:
        df_final = pd.concat(nuevos_registros, ignore_index=True)
        df_final.to_excel('excel_friendly.xlsx', index=False)
    else:
        print("No se encontraron registros para procesar")
    

if __name__ == "__main__":
    main()