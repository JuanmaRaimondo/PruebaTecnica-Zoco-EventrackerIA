from playwright.sync_api import sync_playwright

def extraer_eventos_crudos():
    fuentes = [
        'https://agendatucuman.com.ar/',
        'https://www.tucumanturismo.gob.ar/eventos',
        'https://norteticket.com/?subcategoria=Tucuman',
        'https://lascanasgroup.com.ar/',
        'https://yerbabuena.tur.ar/eventos/'
    ]

    texto_extraido = []

    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True)
        
        page = browser.new_page()

    
        for url in fuentes:
            print(f"Navegando a: {url}")
            
            page.goto(url, wait_until="domcontentloaded")
            
            texto_pagina = page.locator("body").inner_text()
            texto_extraido.append({
                "url_origen": url,
                "texto": texto_pagina
            })

        
        browser.close()
    print("Extracción finalizada.")
        
    return texto_extraido
    

if __name__ == "__main__":
    # 1. Ejecutamos tu función
    resultados = extraer_eventos_crudos()
    
    # 2. Imprimimos un pedacito de cada página para ver si funcionó
    print("\n--- RESULTADOS DE LA EXTRACCIÓN ---")
    for pagina in resultados:
        print(f"\nOrigen: {pagina['url_origen']}")
        # Imprimimos solo los primeros 200 caracteres para no inundar la consola
        print(pagina['texto'][:200] + "...\n")