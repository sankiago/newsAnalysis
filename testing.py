import re
import json
import pandas as pd

def format_json(jsons):
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
        

text = '```json\n{\n\t"title": "Agricultura regenerativa: críticas y preocupaciones",\n\t"subtitle": "¿Puede la agricultura regenerativa salvar el clima o es solo otra promesa vacía de las grandes corporaciones?",\n    "author": "Sharon Kelly",\n    "date": "2020-09-11",\n    "keyword": "Agricultura regenerativa",\n    "url": "https://www.desmog.com/2020/09/11/regenerative-agriculture-criticisms-and-concerns/",\n\t"coordinate_system": "WGS84",\n    "latitude": 47.6062,\n    "longitude": -122.3321,\n    "location_label": "Estados Unidos, Seattle",\n    "content": "Contexto: La agricultura regenerativa se ha promocionado como una solución clave para combatir el cambio climático. Esta práctica se enfoca en mejorar la salud del suelo mediante técnicas como cultivos de cobertura, rotación de cultivos y labranza mínima. Grandes empresas agroindustriales han adoptado este discurso, pero surgen dudas sobre su verdadero impacto. Conflicto: A pesar de sus beneficios ambientales, hay preocupaciones sobre la exageración de sus capacidades para secuestrar carbono y su adopción por parte de corporaciones que mantienen prácticas dañinas, como el uso excesivo de pesticidas. Hecho Central: Investigadores y agricultores cuestionan la falta de evidencia científica sólida que respalde las afirmaciones sobre el potencial de la agricultura regenerativa para mitigar el cambio climático. Además, prácticas como la labranza cero a menudo se abandonan después de unos años, reduciendo sus beneficios. ¿Por qué es importante? Porque si bien estas técnicas pueden mejorar la salud del suelo, su promoción excesiva sin regulación clara podría distraer de soluciones más efectivas y permitir que las grandes empresas continúen con modelos insostenibles. Conclusión: La agricultura regenerativa tiene potencial, pero necesita más investigación, estándares definidos y transparencia para no convertirse en otra herramienta de \'greenwashing\' corporativo."\n}\n```'

aja = [text,text,text,text]
format_json(aja)
