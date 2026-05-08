import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró GEMINI_API_KEY en el .env. Revisá el nombre de la variable.")

os.environ["GEMINI_API_KEY"] = api_key

class Evento(BaseModel):
    nombre: str = Field(description="El nombre oficial del evento o lugar")
    ubicacion: str = Field(description="Dirección o localidad normalizada en Tucumán. Usa como Ejemplo la siguiente dirección: Avenida Aconquija 2015, Yerba Buena")
    categoria: str = Field(description="Categoría inferida (ej. Recital, Teatro, Cervecería, Fiesta, Peña)")
    fuente: str = Field(description="URL de donde se extrajo la información")
    fechaEvento: str | None = Field(description="Fecha y hora del evento. Usa como ejemplo la siguiente fecha: Viernes 1 de Mayo a las 19:00 hs")
    esDuplicado: bool = Field(description="True si el evento ya fue mencionado en esta conversación, False si es nuevo")


class ListaEventos(BaseModel):
    eventos: list[Evento] = Field(description="Lista de todos los eventos encontrados en el texto")



agente_eventos = LlmAgent(
    name="extractor_eventos_tucuman",
    model="gemini-2.5-flash", 
    output_schema=ListaEventos, 
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=1024 
        )
    ),
    instruction="""
    # Identity
    Eres un analista de datos especializado en eventos culturales y vida nocturna en Tucumán.
    
    # Mission
    Extraer, normalizar y clasificar información de eventos a partir de texto crudo, detectando duplicados en la memoria de tu sesión.
    
    # Methodology
    1. Analiza el texto proporcionado buscando cualquier mención a eventos, bares o recitales.
    2. Normaliza las ubicaciones (ej. Si dice "Yerbabuena", cámbialo a "Yerba Buena").
    3. Fechas: Convierte TODAS las fechas al formato estricto YYYY-MM-DD. Por ejemplo, si dice "7 de Mayo", devuelve "2026-05-07". Si incluye la hora (ej. "a las 20:00 hs"), omítela y devuelve solo la fecha. Si es imposible deducir la fecha, devuelve null.
    4. Revisa tu historial de conversación: si el evento ya fue extraído en un turno anterior, marca 'esDuplicado' como True.
    5. Estructura los resultados en el formato JSON requerido.
    
    # Boundaries
    - NUNCA inventes eventos ni fechas que no estén en el texto.
    - Responde EXCLUSIVAMENTE con el JSON estructurado.
    """
    
)


session_service = InMemorySessionService()
runner = Runner(
    agent=agente_eventos,
    app_name="eventracker",
    session_service=session_service
)


def limpiar_estandarizar_datos_crudos(texto_extraido: str) -> str:
    return texto_extraido.replace("\n", " ").replace("\t", " ").strip()

async def procesar_texto_web(texto_crudo: str, url_origen: str, session_id: str):
    """Limpia el texto en Python y lo envía al Agente mediante el Runner asíncrono."""
    
    texto_limpio = limpiar_estandarizar_datos_crudos(texto_crudo)
    prompt = f"Extrae los eventos de este texto obtenido de {url_origen}: {texto_limpio[:3000]}"
    
    from google.genai.types import Content, Part
    user_message = Content(role="user", parts=[Part(text=prompt)])
    
    print(f"Procesando sesión: {session_id}...")
    
   
    try:
        # Intentamos crear la sesión explícitamente con el app_name
        await session_service.create_session(
            session_id=session_id, 
            user_id="sistema_scraper",
            app_name="eventracker"  
        )
    except Exception as e:
        # En vez de "pass" (ignorar), ahora imprimimos si pasa algo raro
        print(f"   -> Nota de sesión: {e}")
    # ==========================================================
    
    respuesta_final = None
    async for event in runner.run_async(
        user_id="sistema_scraper",
        session_id=session_id, 
        new_message=user_message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            
            respuesta_final = event.content.parts[-1].text 
            
    try:
        texto_limpio = respuesta_final.replace("```json", "").replace("```", "").strip()
        return json.loads(respuesta_final)
    except Exception as e:
        print(f"Error parseando el JSON: {e}\nRespuesta IA: {respuesta_final}")
        return []

