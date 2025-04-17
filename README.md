# 🌿 Proyecto de Scraping y Estructuración de Noticias Ambientales

Este repositorio contiene un flujo de trabajo diseñado para **extraer noticias desde portales ambientales**, estructurarlas mediante modelos de lenguaje natural y **asignarles un componente geoespacial** para su visualización en plataformas como ArcGIS.

## 📂 Estructura del Proyecto

```
scrapping/
├── outputs/                # Resultados generados (Excel con noticias)
├── prompts/                # Prompts utilizados para estructuración con LLM
├── scripts/
│   ├── scraping.ipynb      # Notebook para realizar el web scraping
│   └── news_structurer.py  # Script para estructurar y geolocalizar noticias
├── .env                    # Variables de entorno (ej. API key de DeepSeek)
├── .gitignore
└── Contexto.txt            # Descripción general del proyecto
```



## 🔁 Flujo de Trabajo

1. **Extracción de Noticias (Scraping)**  
   Ejecuta el notebook `scraping.ipynb` ubicado en `scripts/`. Este archivo usa `selenium` y `webdriver-manager` para automatizar la navegación web y realizar scraping.  
   > **Importante**: asegúrate de tener instalado Google Chrome y su correspondiente driver actualizado.

2. **Estructuración y Georreferenciación**  
   Corre el siguiente script para estructurar semánticamente las noticias y extraer entidades geográficas:
   ```bash
   python ./scripts/news_structurer.py

Este script se conecta a la API de DeepSeek para estructurar el contenido. Asegúrate de tener un archivo .env con la siguiente variable:

DEEPSEEK_API=tu_api_key_aquí

Dependencias:

Puedes instalar todas las dependencias ejecutando:

```
    pip install -r requirements.txt
```


## 🎯 Objetivos
- Convertir texto no estructurado en información útil para análisis geoespacial.

- Exportar resultados que puedan ser visualizados en dashboards de ArcGIS Online o ArcGIS Pro.

## 🚧 Next Steps


 - [ ] Modificar `guardar_noticias` para hacer guardado parcial

 - [ ] Exponer función scrapping e implementar main.py

 - [ ] Modificar el prompt para que arme un storymap

 - [ ] Hacer el scrap con la nueva lista de las palabras claves


