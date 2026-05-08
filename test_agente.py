import asyncio
from agent import procesar_texto_web, runner # Importa tus funciones

async def test():
    session_id = "test_session_001"
    
    # Prueba 1: Extracción y Normalización
    texto_sucio = "Este viernes hay peña en Yerbabuena, calle Aconquija al 2000."
    print("--- Prueba 1: Procesando primer evento ---")
    res1 = await procesar_texto_web(texto_sucio, "web_test.com", session_id)
    print(res1) 
    # Debería devolver: ubicacion: "Avenida Aconquija 2000, Yerba Buena", esDuplicado: false

    # Prueba 2: Detección de Duplicados (Mismo texto en la misma sesión)
    print("\n--- Prueba 2: Enviando el mismo evento para ver si detecta duplicado ---")
    res2 = await procesar_texto_web(texto_sucio, "web_test.com", session_id)
    print(res2)
    # Aquí es donde el InMemorySessionService brilla: el agente debería marcar esDuplicado: true

if __name__ == "__main__":
    asyncio.run(test())