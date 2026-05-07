import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. Importaciones nativas del ecosistema Google ADK
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Falta la API Key en el archivo .env")


class Evento(BaseModel):
    nombre: str
    ubicacion: str
    categoria: str
    fuente: str
    fechaEvento: str
    esDuplicado: str

def limpiar_estandarizar_datos_crudos(texto_extraido: str) -> str:
    """ Herramienta para limpiar datos basura, sacar los saltos de linea y espacios innecesarios. """
    texto_limpio = texto_extraido.replace("\n", " ").replace("\t", " ").strip()
    return texto_limpio


agente_eventos = Agent(
    name="extractor_eventos_tucuman",
    
    model="gemini-2.5-flash", 
    instruction="""
    Sos un agente extractor de eventos culturales. 
    1. Usa SIEMPRE tu herramienta 'limpiar_estandarizar_datos_crudos' antes de procesar la información.
    2. Extrae los eventos y devuélvelos estrictamente en formato JSON basado en el esquema.
    3. Recuerda los eventos que vas procesando a lo largo de la sesión para poder responder preguntas estadísticas. Si encuentras un evento que ya extrajiste previamente en esta misma conversación, marca el campo 'esDuplicado' con el valor "true". Si es un evento nuevo, pon "false".
    LIMITES
    1. Nunca inventes información. 
    """,
    tools=[limpiar_estandarizar_datos_crudos],
    
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True
            
        )
    )
)


def procesar_texto_web(texto_crudo: str, url_origen: str):
    """Envía el texto al Agente ADK y devuelve JSON estructurado."""
    
    prompt = f"Analiza este texto de la url {url_origen}: {texto_crudo[:3000]}"
    
    
    respuesta = agente_eventos.run(
        prompt,
        
        response_schema=list[Evento] 
    )
    
    try:
       
        return json.loads(respuesta.text)
    except (json.JSONDecodeError, AttributeError):
        print("Error: El agente no devolvió un JSON válido.")
        return []