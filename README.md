# Eventracker - Motor de IA (Scraper)

Este microservicio es el motor de extracción de datos del sistema. Se encarga de rastrear portales web locales, extraer la información en crudo y utilizar Inteligencia Artificial para clasificar y estructurar los eventos antes de enviarlos a la base de datos.

## 🛠️ Tecnologías Utilizadas
* **Python 3.11**
* **Google Gemini API:** Procesamiento de Lenguaje Natural (NLP) para la limpieza y clasificación de datos.
* **BeautifulSoup4 / Requests:** Web scraping de los portales.
* **Docker:** Contenerización del servicio.

## 🧠 Lógica de Funcionamiento
1. **Scraping:** Escanea las URLs configuradas buscando texto relacionado con eventos culturales y sociales.
2. **Procesamiento AI:** Envía el texto crudo a Gemini mediante un prompt estricto para extraer campos estructurados (Título, Fecha, Lugar, Categoría).
3. **Integración:** Envía el evento formateado en JSON al Backend (Spring Boot) mediante una petición HTTP POST.

¿Cómo evitás duplicados?
Evite duplicados usando un parametro llamado esDuplicado en false y luego el agente de IA determinaba si es que ya estaba en la base de datos lo marcaba como true y si no lo guaraba y seguia siendo false. 
¿Cómo escalarías este sistema?
Este sistema lo podria escalar primero con un dashboard para que el usario interactue mejor con el programa y un mapa interactivo que muestre donde se van a realizar los eventos.
¿Qué problemas puede tener este flujo?
 El principal problema es que uso una API KEY gratuita y los tokens son muy limitados para muchas consultas.
¿Cómo mejorarías la calidad de los datos?
Como hice la API REST en java podria usar annotations para que los valores de los campos no sean nulos ni vacios. Tambien en el agente podira ponerle mas seguridad pidiendo que no se ingresen valores nulos ni blancos. 

https://drive.google.com/drive/folders/1PGGYmpVCysyEq0RppRyvZZ7HN2YgW5sq?usp=sharing