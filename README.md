# Tiktok-User-Scraper

Herramientas para:
1. Extraer metadatos de vídeos de un usuario de TikTok  
2. Descargar vídeos de un usuario
3. Descargar comentarios de vídeos ya descargados  

El flujo correcto es:
1. **User-Videos Scraper**
2. **Video Downloader**
3. **Comments Downloader**

---

## Requisitos

- Python 3.9+ recomendado
- Navegador compatible con Playwright (se instala automáticamente)

---

## Instalación

### 1️⃣ Crear environment y activarlo

Escribir en cmd: 

```
conda create -n <nombre_environment> python=3.10

conda activate <nombre_environment>
```

### 2️⃣ Instalar dependencias Python

Escribir en cmd:

```
pip install -r requirements.txt
```

### 3️⃣ Preparar herramientas anti-detección de bots

Escribir en cmd (ejecutar cada una por separado):

```
playwright install

camoufox fetch
```

## 🧩 Uso del programa

Cada vez que vayais a usar el programa, posicionaros en cmd en la carpeta donde esté el main y ejecutad:

```
conda activate <nombre_environment>

python main.py
```

## ⚠️ Advertencias:

- La parte de descargar vídeos, y sobre todo la de descargar comentarios, son lentas. Esto es así para dificultar que TikTok nos detecte como bots.
- El módulo de descargar vídeos contempla la posibilidad de que algunos vídeos en realidad no lo sean (fotos). No los descarga. 
- La parte de descargar comentarios no es completamente eficaz; habrá vídeos de los cuales a la primera consiga los comentarios y otros no. Cuántos más comentarios pidáis de cada vídeo, más fallará porque os detectará antes como bots. Sin embargo, puede que después de detectaros para algunos vídeos, luego no lo haga para otros. Por eso, se guarda registro de qué vídeos sí se han conseguido comentarios, para que si pedís los comentarios de los vídeos de un usuario una segunda vez, no lo intente con aquellos vídeos cuyos comentarios sí que han sido descargados y se centre en aquellos vídeos cuyos comentarios no se han obtenido en ejecuciones anteriores (las ejecuciones serán cada vez más rápidas). 




