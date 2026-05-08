import asyncio
import logging
import requests
import sys
from datetime import datetime


from scraper import extraer_eventos_crudos
from agent import procesar_texto_web


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("eventracker.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

async def ejecutar_pipeline():
    
    logging.info("Extrayendo datos de las páginas web seleccionadas")
    paginas = await asyncio.to_thread(extraer_eventos_crudos)
    
    
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    eventos_a_guardar = []

    
    for pagina in paginas:
        logging.info(f"Analizando con IA: {pagina['url_origen']}")
        resultado_ia = await procesar_texto_web(
            texto_crudo=pagina['texto'],
            url_origen=pagina['url_origen'],
            session_id=session_id
        )
        
        if resultado_ia and "eventos" in resultado_ia:
            for evento in resultado_ia["eventos"]:
                
                if not evento.get("esDuplicado", False):
                    eventos_a_guardar.append(evento)
                    logging.info(f" Evento encontrado: {evento.get('nombre')}")
                else:
                    logging.warning(f"Evento duplicado: {evento.get('nombre')}")

    
    if eventos_a_guardar:
        logging.info(f"Enviando {len(eventos_a_guardar)} eventos a la base de datos...")
        for evento in eventos_a_guardar:
            try:
                
                url_java = "http://localhost:8081/api/evento/crear" 
                response = requests.post(url_java, json=evento)
                
                if response.status_code in [200, 201]:
                    logging.info(f" Guardado en MongoDB: {evento.get('nombre')}")
                else:
                    logging.error(f"Error de Java al guardar '{evento.get('nombre')}'. Código HTTP: {response.status_code}")
            except requests.exceptions.ConnectionError:
                logging.critical("Erro: No se pudo conectar con Java. ¿Está corriendo el proyecto de Spring Boot?")
                break
    else:
        logging.info("No se encontraron eventos nuevos para guardar en este ciclo.")
        
    


async def automatizacion_continua():
    """Bucle infinito que ejecuta el ciclo y luego duerme."""
    while True:
        await ejecutar_pipeline()
        horas_espera = 24
        logging.info(f"Sistema en espera. Próxima búsqueda automática en {horas_espera} horas...")
        
        await asyncio.sleep(horas_espera * 3600)

if __name__ == "__main__":
    print("Para ejecutar una unica prueba manual ingrese 1 y si quiere que se haga automaticamente ingrese 2.")
    opcion = input("\nElegí una opción (1 o 2) y presioná Enter: ").strip()

    if opcion == "1":
        asyncio.run(ejecutar_pipeline())
        logging.info("Prueba finalizada.")
    elif opcion == "2":

        try:
            
            asyncio.run(automatizacion_continua())
        except KeyboardInterrupt:
            
            logging.info("Orquestador detenido manualmente por el usuario.")
    else:
        print(" Opción no valida")