## BallonTranslator

[Chino](/README.md) | [Inglês](/README_EN.md) | [pt-BR](../doc/README_PT-BR.md) | [Ruso](../doc/README_RU.md) | [Japonés](../doc/README_JA.md) | [Indonesio](../doc/README_ID.md) | [Vietnamita](../doc/README_VI.md) | [Koreano](../doc/README_KO.md) | Español

BallonTranslator es otra herramienta asistida por ordenador, basada en el aprendizaje profundo, para traducir cómics/manga.

<img src="../doc/src/ui0.jpg" div align=center>

<p align=center>
  <strong>Vista previa</strong>
</p>

## Recursos
* **Traducción totalmente automática:** 
  - Detecta, reconoce, elimina y traduce textos automáticamente. El rendimiento global depende de estos módulos.
  - La maquetación se basa en el formato estimado del texto original.
  - Funciona bien con manga y cómics.
  - Diseño mejorado para manga->inglés, inglés->chino (basado en la extracción de regiones de globos).
  
* **Edición de imágenes:**
  - Permite editar máscaras e inpainting (similar a la herramienta Pincel recuperador de imperfecciones de Photoshop).
  - Adaptado para imágenes con una relación de aspecto extrema, como los webtoons.
  
* **Edición de texto:**
  - Admite formato de texto y [preajustes de estilo de texto](https://github.com/dmMaze/BallonsTranslator/pull/311). Los textos traducidos pueden editarse interactivamente.
  - Buscar y reemplazar.
  - Exportación/importación a/desde documentos Word.

## Instalación

### En Windows
Si no quieres instalar Python y Git manualmente y tienes acceso a Internet:  
Descarga BallonsTranslator_dev_src_with_gitpython.7z desde [MEGA](https://mega.nz/folder/gmhmACoD#dkVlZ2nphOkU5-2ACb5dKw) o [Google Drive](https://drive.google.com/drive/folders/1uElIYRLNakJj-YS0Kd3r3HE-wzeEvrWd?usp=sharing), descomprime y ejecuta launch_win.bat.  
Ejecute scripts/local_gitpull.bat para obtener la última actualización.

### Ejecutar el código fuente
Instale [Python](https://www.python.org/downloads/release/python-31011) **< 3.12** (no utilice la versión de Microsoft Store) y [Git](https://git-scm.com/downloads).

```bash
# Clonar este repositorio
$ git clone https://github.com/dmMaze/BallonsTranslator.git ; cd BallonsTranslator

# Iniciar la aplicación
$ python3 launch.py
```

En la primera ejecución, se instalarán las librerías necesarias y las plantillas se descargarán automáticamente. Si las descargas fallan, tendrás que descargar la carpeta **data** (o los archivos que faltan mencionados en el terminal) desde [MEGA](https://mega.nz/folder/gmhmACoD#dkVlZ2nphOkU5-2ACb5dKw) o [Google Drive](https://drive.google.com/drive/folders/1uElIYRLNakJj-YS0Kd3r3HE-wzeEvrWd?usp=sharing) y guardarla en la ruta correspondiente de la carpeta de código fuente.

## Creación de la aplicación para macOS (compatible con chips Intel y Apple Silicon)

*Nota: macOS también puede ejecutar el código fuente si la aplicación no funciona.*

![录屏2023-09-11 14 26 49](https://github.com/hyrulelinks/BallonsTranslator/assets/134026642/647c0fa0-ed37-49d6-bbf4-8a8697bc873e)

#### 1. Preparación
-  Descargue las bibliotecas y plantillas de [MEGA](https://mega.nz/folder/gmhmACoD#dkVlZ2nphOkU5-2ACb5dKw) o [Google Drive](https://drive.google.com/drive/folders/1uElIYRLNakJj-YS0Kd3r3HE-wzeEvrWd?usp=sharing).

<img width="1268" alt="截屏2023-09-08 13 44 55_7g32SMgxIf" src="https://github.com/dmMaze/BallonsTranslator/assets/134026642/40fbb9b8-a788-4a6e-8e69-0248abaee21a">

-  Coloca todos los recursos descargados en una carpeta llamada `data`. La estructura final del directorio debería ser la siguiente:
  
```
data
├── libs
│   └── patchmatch_inpaint.dll
└── models
    ├── aot_inpainter.ckpt
    ├── comictextdetector.pt
    ├── comictextdetector.pt.onnx
    ├── lama_mpe.ckpt
    ├── manga-ocr-base
    │   ├── README.md
    │   ├── config.json
    │   ├── preprocessor_config.json
    │   ├── pytorch_model.bin
    │   ├── special_tokens_map.json
    │   ├── tokenizer_config.json
    │   └── vocab.txt
    ├── mit32px_ocr.ckpt
    ├── mit48pxctc_ocr.ckpt
    └── pkuseg
        ├── postag
        │   ├── features.pkl
        │   └── weights.npz
        ├── postag.zip
        └── spacy_ontonotes
            ├── features.msgpack
            └── weights.npz

7 directorios, 23 ficheros
```

- Instale la herramienta de línea de comandos pyenv para gestionar las versiones de Python. Se recomienda la instalación a través de Homebrew.

```
# Instalación mediante Homebrew
brew install pyenv

# Instalación mediante script oficial
curl https://pyenv.run | bash

# Configuración del entorno shell tras la instalación
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

#### 2. Creación de la aplicación
```
# Introduzca el directorio de trabajo `data`.
cd data

# Clonar la rama `dev` del repositorio
git clone -b dev https://github.com/dmMaze/BallonsTranslator.git

# Introduzca el directorio de trabajo `BallonsTranslator`.
cd BallonsTranslator

# Ejecute el script de construcción, que le pedirá la contraseña en el paso pyinstaller, introduzca la contraseña y pulse enter
sh scripts/build-macos-app.sh
```

> 📌 La aplicación empaquetada se encuentra en ./data/BallonsTranslator/dist/BallonsTranslator.app. Arrastre la aplicación a la carpeta de aplicaciones de macOS para instalarla. Listo para usar sin ajustes adicionales de Python.


</details>

Para utilizar el traductor Sugoi (sólo japonés-inglés), descarga la [plantilla offline](https://drive.google.com/drive/folders/1KnDlfUM9zbnYFTo6iCbnBaBKabXfnVJm) y mueve la carpeta «sugoi_translator» a BallonsTranslator/ballontranslator/data/models.


# Utilización

**Se recomienda ejecutar el programa en un terminal en caso de que se produzca un fallo y no se proporcione información, como se muestra en el siguiente gif.**
<img src="../doc/src/run.gif">  

- En la primera ejecución, selecciona el traductor y establece los idiomas de origen y destino haciendo clic en el icono de configuración.
- Abre una carpeta que contenga las imágenes del cómic (manga/manhua/manhwa) que necesites traducir haciendo clic en el icono de la carpeta.
- Haz clic en el botón «Ejecutar» y espera a que se complete el proceso.

Los formatos de fuente, como el tamaño y el color, son determinados automáticamente por el programa en este proceso. Puede predeterminar estos formatos cambiando las opciones correspondientes de "decidir por el programa" a "utilizar configuración global" en el panel Configuración->Diagramación. (La configuración global son los formatos que se muestran en el panel de formato de fuente de la derecha cuando no está editando ningún bloque de texto en la escena).

## Edición de imágenes

### Herramienta para pintar
<img src="../doc/src/imgedit_inpaint.gif">
<p align = "center">
  <strong>Modo de edición de imágenes, herramienta Inpainting</strong>
</p>

### Herramienta rectángulo
<img src="../doc/src/rect_tool.gif">
<p align = "center">
  <strong>Herramienta rectángulo</strong>
</p>

Para 'borrar' los resultados de inpainting no deseados, utilice la herramienta inpainting o la herramienta rectángulo con el **botón derecho del ratón** pulsado. El resultado depende de la precisión con la que el algoritmo ("método 1" y "método 2" en el gif) extrae la máscara de texto. El rendimiento puede ser peor con texto y fondos complejos.

## Edición de texto
<img src="../doc/src/textedit.gif">
<p align = "center">
  <strong>Modo de edición de texto</strong>
</p>

<img src="../doc/src/multisel_autolayout.gif" div align=center>
<p align=center>
  <strong>Formato de texto por lotes y maquetación automática</strong>
</p>

<img src="../doc/src/ocrselected.gif" div align=center>
<p align=center>
  <strong>OCR y traducción de áreas seleccionadas</strong>
</p>

## Atajos
* `A`/`D` o `pageUp`/`Down` para pasar de página
* `Ctrl+Z`, `Ctrl+Shift+Z` para deshacer/rehacer la mayoría de las operaciones (la pila de deshacer se borra al pasar página).
* `T` para el modo de edición de texto (o el botón "T" de la barra de herramientas inferior).
* `W` para activar el modo de creación de bloques de texto, arrastra el ratón por la pantalla con el botón derecho pulsado para añadir un nuevo bloque de texto (ver gif de edición de texto).
* `P` para el modo de edición de imágenes.
* En el modo de edición de imágenes, utiliza el control deslizante de la esquina inferior derecha para controlar la transparencia de la imagen original.
* Desactivar o activar cualquier módulo automático a través de la barra de título->ejecutar. Ejecutar con todos los módulos desactivados remapeará las letras y renderizará todo el texto según la configuración correspondiente.
* Establece los parámetros de los módulos automáticos en el panel de configuración.
* `Ctrl++`/`Ctrl+-` (También `Ctrl+Shift+=`) para redimensionar la imagen.
* `Ctrl+G`/`Ctrl+F` para buscar globalmente/en la página actual.
* `0-9` para ajustar la opacidad de la capa de texto.
* Para editar texto: negrita - `Ctrl+B`, subrayado - `Ctrl+U`, cursiva - `Ctrl+I`.
* Ajuste la sombra y la transparencia del texto en el panel de estilo de texto -> Efecto.

<img src="../doc/src/configpanel.png">

## Modo Headless (ejecución sin interfaz gráfica)

```python
python launch.py --headless --exec_dirs "[DIR_1],[DIR_2]..."
```

La configuración (idioma de origen, idioma de destino, modelo de inpainting, etc.) se cargará desde config/config.json. Si el tamaño de la fuente renderizada no es correcto, especifique manualmente el DPI lógico mediante `--ldpi`. Los valores típicos son 96 y 72.

## Módulos de automatización
Este proyecto depende en gran medida de [manga-image-translator](https://github.com/zyddnys/manga-image-translator). Los servicios en línea y la formación de modelos no son baratos, así que por favor considere hacer una donación al proyecto:
- Ko-fi: [https://ko-fi.com/voilelabs](https://ko-fi.com/voilelabs)
- Patreon: [https://www.patreon.com/voilelabs](https://www.patreon.com/voilelabs)
- 爱发电: [https://afdian.net/@voilelabs](https://afdian.net/@voilelabs)

El [traductor de Sugoi](https://sugoitranslator.com/) fue creado por [mingshiba](https://www.patreon.com/mingshiba).

## Detección de texto
* Permite detectar texto en inglés y japonés. El código de entrenamiento y más detalles en [comic-text-detector](https://github.com/dmMaze/comic-text-detector).
* Admite el uso de la detección de texto de [Starriver Cloud (Tuanzi Manga OCR)](https://cloud.stariver.org.cn/). Es necesario rellenar el nombre de usuario y la contraseña, y el inicio de sesión automático se realizará cada vez que se inicie el programa.
  * Para obtener instrucciones detalladas, consulte el [Manual de TuanziOCR](../doc/Manual_TuanziOCR_ES.md).

## OCR
* Todos los modelos mit* proceden de manga-image-translator y admiten el reconocimiento en inglés, japonés y coreano, así como la extracción del color del texto.
* [manga_ocr](https://github.com/kha-white/manga-ocr) es de [kha-white](https://github.com/kha-white), reconocimiento de texto para japonés, centrado principalmente en el manga japonés.
* Admite el uso de OCR de [Starriver Cloud (Tuanzi Manga OCR)](https://cloud.stariver.org.cn/). Es necesario rellenar el nombre de usuario y la contraseña, y el inicio de sesión automático se realizará cada vez que se inicie el programa.
  * La implementación actual utiliza OCR en cada bloque de texto individualmente, lo que resulta en una velocidad más lenta y ninguna mejora significativa en la precisión. No se recomienda. Si es necesario, utilice el Detector Tuanzi.
  * Cuando se utiliza Tuanzi Detector para la detección de texto, se recomienda configurar el OCR a none_ocr para leer el texto directamente, ahorrando tiempo y reduciendo el número de peticiones.
  * Para obtener instrucciones detalladas, consulte el [Manual de TuanziOCR](doc/Manual_TuanziOCR_ES.md). 

## Inpainting
* AOT es de [manga-image-translator](https://github.com/zyddnys/manga-image-translator).
* Todas las lama* se ajustan mediante [LaMa](https://github.com/advimman/lama).
* PatchMatch es un algoritmo de [PyPatchMatch](https://github.com/vacancy/PyPatchMatch). Este programa utiliza una [versión modificada](https://github.com/dmMaze/PyPatchMatchInpaint) por mí.

## Traductores
Traductores disponibles: Google, DeepL, ChatGPT, Sugoi, Caiyun, Baidu, Papago y Yandex.
* Google ha desactivado el servicio de traducción en China, establece la «url» correspondiente en el panel de configuración a *.com.
* Los traductores [Caiyun](https://dashboard.caiyunapp.com/), [ChatGPT](https://platform.openai.com/playground), [Yandex](https://yandex.com/dev/translate/), [Baidu](http://developers.baidu.com/) y [DeepL](https://www.deepl.com/docs-api/api-access) requieren un token o clave de API.
* DeepL y el traductor Sugoi (y su conversión CT2 Translation) gracias a [Snowad14](https://github.com/Snowad14).
* Sugoi traduce del japonés al inglés completamente offline.
* [Sakura-13B-Galgame](https://github.com/SakuraLLM/Sakura-13B-Galgame)
*
Para añadir un nuevo traductor, consulte [Cómo_añadir_un_nuevo_traductor](../doc/Como_añadir_un_nuevo_traductor.md). Es tan sencillo como crear una subclase de una clase base e implementar dos interfaces. Luego puedes usarla en la aplicación. Las contribuciones al proyecto son bienvenidas.
*
## FAQ & Varios
* Si tu ordenador tiene una GPU Nvidia o Apple Silicon, el programa activará la aceleración por hardware.
* Añadir soporte para [saladict](https://saladict.crimx.com) (*Diccionario emergente profesional y traductor de páginas todo en uno*) al mini menú al seleccionar texto. [Guía de instalación](../doc/saladict_es.md).
* Acelera el rendimiento si tienes un dispositivo [NVIDIA CUDA](https://pytorch.org/docs/stable/notes/cuda.html) o [AMD ROCm](https://pytorch.org/docs/stable/notes/hip.html), ya que la mayoría de los módulos utilizan [PyTorch](https://pytorch.org/get-started/locally/).
* Las fuentes son de tu sistema.
* Gracias a [bropines](https://github.com/bropines) por la localización rusa.
* Añadido script de exportación JSX para Photoshop por [bropines](https://github.com/bropines). Para leer las instrucciones, mejorar el código y simplemente explorar cómo funciona, vaya a `scripts/export to photoshop` -> `install_manual.md`.
