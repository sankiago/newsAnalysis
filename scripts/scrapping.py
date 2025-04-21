from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import time
import pandas as pd

# CONFIGURACIÓN DEL DRIVER
DIRECTORIO = "noticias_desmog"
ARCHIVO_CONSOLIDADO = os.path.join(DIRECTORIO, 'desmog_news.txt')
SEPARADOR = "\n" + "-" * 80 + "\n"
BASE_URL = "https://www.desmog.com/sitesearch/?q={query}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

# Crear directorio si no existe
os.makedirs(DIRECTORIO, exist_ok=True)

# Configurar Selenium con Chrome Headless
options = Options()
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def close_popups():
    """Cierra pop-ups de suscripción y cookies si aparecen."""
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]"))
        ).click()
        print("    Pop-up de cookies cerrado.")
        time.sleep(2)
    except:
        print("    No se encontró pop-up de cookies.")
    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Close')]")
        ))
        close_button.click()
        print("    Pop-up de suscripción cerrado.")
        time.sleep(2)
    except:
        print("    No se encontró el botón de cierre del pop-up. Intentando cerrar con ESCAPE...")
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            print("    Pop-up cerrado con tecla ESCAPE.")
            time.sleep(2)
        except:
            print("    No se pudo cerrar el pop-up de suscripción.")


def scroll_and_load_results():
    """Desplaza la página para cargar más resultados."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
def next_page():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cursor_box = soup.find('div', class_='gsc-cursor-box gs-bidi-start-align')
    if cursor_box is not None:
        length = len(cursor_box.find_all()) - 1
    else:
        length = 0
    if cursor_box:
        # Encuentra el número de la página actual
        current_page = cursor_box.find('div', class_='gsc-cursor-current-page')
        if current_page:
            current_page_number = int(current_page.get_text(strip=True))
            next_page_number = current_page_number + 1
            
            # Limitar a 10 páginas
            print(f'    longitud: {length}\n')
            if next_page_number > min(length, 10):
                return False
            
            # Encuentra el botón de la siguiente página
            next_page_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[@class='gsc-cursor-page' and text()='{next_page_number}']"))
            )
            driver.execute_script("arguments[0].click();", next_page_div)
            time.sleep(2)  # Espera a que cargue la siguiente página
            return True
    return False

def scan_page(keyword):
    time.sleep(1)
    scroll_and_load_results()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    articles = soup.find_all('div', class_='gsc-webResult') or soup.find_all('div', class_='gsc-result')
    
    noticias = []
    for article in articles:
        title_tag = article.find('a', class_='gs-title')
        if title_tag and title_tag.get('href'):
            title = title_tag.text.strip()
            link = title_tag['href']
            noticias.append({"title": title, "link": link, "keyword": keyword})
    return noticias

def obtener_resultados_busqueda(query):
    """Obtiene los enlaces y títulos de los resultados de búsqueda, manejando ventanas emergentes si aparecen."""
    url = BASE_URL.format(query=query)
    driver.get(url)
    time.sleep(5)
    close_popups()
    noticias = scan_page(query)
    i=1
    print(f'EXPLORACIÓN - {query}')
    while(next_page()):
        print(f'    Explorando página {i} de resultados')
        noticias = noticias + scan_page(query)  
        i += 1
        break
        
    return noticias

def obtener_contenido_noticia(url, keyword):
    """Extrae el contenido, autor, fecha y título de una noticia."""
    driver.get(url) 
    time.sleep(2.5)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Extraer título
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "Título no disponible"
    
    # Extraer autor
    # author_tag = soup.find('span', class_='author-name')
    # author_tag = soup.find(class_='jet-listing-dynamic-meta__item-val molongui-disabled-link')
    author_tag = soup.select("div.jet-listing-dynamic-meta__author a")
    # print(f'el autor está en {author_tag}')
    author = author_tag[0].get_text(strip=True) if author_tag else "Autor no disponible"
    
    # Extraer fecha
    date_tag = soup.find('time')
    date = date_tag.get_text(strip=True) if date_tag else "Fecha no disponible"
    
    # Extraer contenido
    paragraphs = soup.find_all(['p', 'h2', 'h3'])
    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    content = content if content else "Contenido no disponible."
    
    # return f"Título: {title}\nAutor: {author}\nFecha: {date}\n\n{content}"
    return {
        'title': title,
        'author': author,
        'date': date,
        'content': content,
        'url': url,
        'keyword': keyword,
    }
    
def guardar_noticias(noticias, docTitle, keyword):
    datos = []
    print("PROCESAMIENTO")
    
    for idx, noticia in enumerate(noticias):
        print(f'Procesando noticia {idx + 1}/{len(noticias)}')
        contenido = obtener_contenido_noticia(noticia['link'], noticia['keyword'])
        datos.append(contenido)  # Agregamos el contenido al DataFrame

    # Convertimos la lista de datos en un DataFrame
    df = pd.DataFrame(datos)
    
    # Guardamos el DataFrame en un archivo Excel
    file_name = f'scrap_{docTitle}.xlsx'
    df.to_excel(file_name, index=False)
    print(f"Noticias guardadas en {file_name}")
    
def keywords_news(label, keyword_list):
    output_path = rf'.\outputs\{label}_links.xlsx'
    log_path = rf'.\outputs\{label}_links_progress.txt'

    # Leer el índice de progreso
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            start_index = int(f.read().strip())
    else:
        start_index = 0

    # Si ya hay resultados parciales, cargarlos
    if os.path.exists(output_path):
        df_link_noticias = pd.read_excel(output_path)
    else:
        df_link_noticias = pd.DataFrame()
    
    for idx in range(start_index, len(keyword_list)):
        keyword = keyword_list[idx]
        print(f"Buscando noticias para: {keyword} - {idx+1}/{len(keyword_list)}")
        try:
            search_results = obtener_resultados_busqueda(keyword)
            results_dfs = [pd.DataFrame([result]) for result in search_results]
            results_df = pd.concat(results_dfs)
            df_link_noticias  = pd.concat([df_link_noticias,results_df])
            
            # Guardado parcial, si i==len(keyword_list)-1 entones será el guardado total
            df_link_noticias.to_excel(output_path, index=False)
            
            # Guardar progreso
            with open(log_path, "w") as f:
                f.write(str(idx + 1))  # Guarda el próximo índice a procesar

            print(f"Noticias de '{keyword}' guardadas correctamente")
        except Exception as e:
            print(f'Error al procesar la keyword {idx} ({keyword}): {e}')
    
    df_link_noticias = df_link_noticias.drop_duplicates(subset='title', keep='first')
    return df_link_noticias    

def scrap_news_links(label:str, links:pd.DataFrame):
    output_path = rf'.\outputs\{label}_extraction.xlsx'
    log_path = rf'.\outputs\{label}_extraction_progress.txt'

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
    
    print()
    for i in range(start_index, len(links)):
        _, link, keyword = links.iloc[i].to_dict().values()
        # print(f'los parámetros son {link} {keyword}')
        try:
            new = obtener_contenido_noticia(link, keyword)
            new_df = pd.DataFrame([new])
            df_noticias = pd.concat([df_noticias, new_df])
            df_noticias.to_excel(output_path, index=False)
            
            # Guardar progreso
            with open(log_path, "w") as f:
                f.write(str(i + 1))  # Guarda el próximo índice a procesar
            print(f"Noticia {i+1}/{len(links)} guardada correctamente")
            
        except Exception as e:
            print(f'Error al procesar la noticia {i}\n    link: {link}\n    keyword: {keyword}\n\n{e}')
    
    return df_noticias

def cargar_palabras_desde_txt(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        palabras = [line.strip() for line in f if line.strip()]
    return palabras


def main():
    climate_keywords = cargar_palabras_desde_txt('keywords.txt')
    #procure no usar caracteres especiales ni espacios en el label, se va a usar el label en alguna ruta
    label = '25-abr'
    if os.path.exists(rf'./outputs/{label}_extraction_progress.txt'):
        print(f'Se reanuda el scrapping: {label}')
    
    
    links = keywords_news(label, climate_keywords)
    if len(links.index) != 0:
        news = scrap_news_links(label, links)
        print(rf'Se procesaron las {len(news)} noticias de manera existosa, los resultados se encuentran en .\output\{label}_extraction.xlsx')
    else:
        print("No se encontraron noticias.")
    driver.quit()

if __name__ == "__main__":
    main()
    
    
    
'''

climate_keywords = [
    "Regenerative agriculture",
    "Eco-anxiety",
    "Tipping point",
    "Mitigation",
    "Adaptation",
    "Resilience",
    "Carbon footprint",
    "Water footprint",
    "Climate justice",
    "Nature-based solutions (NbS)",
    "Loss and damage",
    "Net zero emissions",
    "Decarbonization",
    "Carbon sink",
    "Carbon sequestration",
    "Rewilding",
    "Circular economy",
    "Greenwashing",
    "Nature crisis",
    "Biodiversity crisis",
    "Planetary boundaries",
    "Land degradation",
    "Biodiversity hotspot",
    "Environmental justice",
    "Ecocide",
    "Indigenous knowledge",
    "Traditional ecological knowledge",
    "Green economy",
    "Blue economy",
    "Reforestation and afforestation",
    "Debt-for-nature swaps",
    "Access and benefit sharing (ABS)",
    "Green jobs",
    "Global Biodiversity Framework (GBF)",
    "National Biodiversity Strategies and Action Plans (NBSAPs)",
    "Nature-positive",
    "Weather vs climate",
    "Greenhouse gases (GHGs)",
    "Global warming",
    "Climate change",
    "Climate crisis",
    "Feedback loops",
    "Overshoot",
    "Climate security",
    "Climate finance",
    "Renewable energy",
    "Carbon removal vs carbon sequestration",
    "Carbon markets",
    "Just transition",
    "United Nations Framework Convention on Climate Change (UNFCCC)",
    "Conference of the Parties (COP)",
    "Paris Agreement",
    "Nationally Determined Contributions (NDCs)",
    "Transparency",
    "National Adaptation Plans (NAPs)",
    "Long-term strategies (LTS)",
    "REDD+",
    "Intergovernmental Panel on Climate Change (IPCC)"
]
'''