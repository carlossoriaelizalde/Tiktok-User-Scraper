# Tiktok-User-Scraper (English)

Tools for:
1. Extracting video metadata from a TikTok user  
2. Downloading videos from a user  
3. Downloading comments from already downloaded videos  

The correct workflow is:
1. **User-Videos Scraper**
2. **Video Downloader**
3. **Comments Downloader**

---

## Requirements

- Python 3.9+ recommended  
- A Playwright-compatible browser (installed automatically)

---

## Installation

### 1️⃣ Create and activate the environment

Type in cmd:

```
conda create -n <environment_name> python=3.10

conda activate <environment_name>
```

### 2️⃣ Install Python dependencies

Type in cmd:

```
pip install -r requirements.txt
```

### 3️⃣ Prepare anti-bot detection tools

Type in cmd (run each command separately):

```
playwright install

camoufox fetch
```

## 🧩 Program usage

Every time you want to use the program, navigate in cmd to the folder where `main.py` is located and run:

```
conda activate <environment_name>

python main.py
```

## ⚠️ Warnings:

- Downloading videos, and especially downloading comments, is slow. This is intentional to make it harder for TikTok to detect the tool as a bot.
- The video downloader module accounts for the possibility that some “videos” are actually photo posts. These are not downloaded.
- The comments downloader is not fully reliable; there will be videos for which comments are successfully downloaded on the first attempt and others for which they are not. The more comments you request per video (this can be changed in `main.py`), the more likely it is to fail due to easier bot detection. However, it may happen that after being detected for some videos, TikTok does not detect the tool for others. For this reason, the program keeps track of which videos have successfully downloaded comments, so that if you request comments for a user’s videos a second time, it will not retry videos whose comments were already downloaded and will focus only on videos whose comments were not obtained in previous executions (making subsequent runs progressively faster).


# Tiktok-User-Scraper (Español)

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
- La parte de descargar comentarios no es completamente eficaz; habrá vídeos de los cuales a la primera consiga los comentarios y otros no. Cuántos más comentarios pidáis de cada vídeo (se cambia en el main), más fallará porque os detectará más fácilmente como bots. Sin embargo, puede que después de detectaros para algunos vídeos, luego no lo haga para otros. Por eso, se guarda registro de qué vídeos sí se han conseguido comentarios, para que si volveis a pedir los comentarios de los vídeos de un usuario una segunda vez, no lo intente con aquellos vídeos cuyos comentarios sí que han sido descargados y se centre en aquellos vídeos cuyos comentarios no se han obtenido en ejecuciones anteriores (las ejecuciones serán cada vez más rápidas). 




