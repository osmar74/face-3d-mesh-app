# Face 3D Mesh App

Aplicación web para detectar landmarks faciales, construir una malla 3D tipo Delaunay/Voronoi y proyectarla en una interfaz web interactiva.

## Stack
- Backend: Python 3.12, FastAPI, OpenCV, MediaPipe, NumPy, SciPy
- Frontend: HTML, CSS, JavaScript, Canvas 2D

## Arquitectura
- MVC
- OOP

## Flujo de ramas
- main: estable
- dev: integración

## para ejecutar
python -m uvicorn backend.app.main:app --reload



# Face 3D Mesh App

Aplicación web para capturar o cargar el rostro de un usuario, detectar landmarks faciales, generar una malla por triangulación de Delaunay, proyectarla en 3D y visualizar el resultado en un dashboard técnico interactivo.

---

## 1. Descripción general

El proyecto permite procesar un rostro desde dos fuentes de entrada:

* carga de archivo de imagen,
* captura desde webcam.

A partir de esa entrada, el sistema ejecuta un pipeline de visión artificial y geometría computacional que:

1. valida la imagen,
2. detecta landmarks faciales con MediaPipe,
3. construye una malla mediante triangulación de Delaunay,
4. filtra triángulos no deseados,
5. normaliza coordenadas 3D,
6. aplica rotación y proyección en perspectiva desde el backend,
7. renderiza el resultado en varios paneles del frontend,
8. permite guardar y volver a cargar resultados procesados.

---

## 2. Objetivos del proyecto

### Objetivo funcional

Desarrollar una aplicación web que capture o reciba una imagen facial y construya una visualización técnica en 2D y 3D del rostro a partir de landmarks y triangulación.

### Objetivos técnicos

* Detectar landmarks faciales con coordenadas `x`, `y`, `z`.
* Construir una malla triangular usando Delaunay.
* Aplicar rotación y proyección 3D con fórmulas implementadas en Python.
* Visualizar el pipeline en un dashboard técnico por paneles.
* Permitir guardar y cargar resultados en archivos JSON.
* Mantener una arquitectura clara basada en MVC y OOP.

---

## 3. Tecnologías utilizadas

### Backend

* Python 3.12
* FastAPI
* Uvicorn
* OpenCV
* MediaPipe Tasks Face Landmarker
* NumPy
* SciPy
* Pydantic

### Frontend

* HTML
* CSS
* JavaScript puro
* Canvas 2D
* Web APIs (`getUserMedia`, `File`, `Blob`, `fetch`)

### Herramientas de desarrollo

* Windows 11
* Visual Studio Code
* Command Prompt de VS Code
* Git
* GitHub
* GitLens

---

## 4. Arquitectura del proyecto

El proyecto fue organizado con enfoque **MVC + OOP**.

### Model

Contiene estructuras de datos tipadas con Pydantic para:

* landmarks,
* vértices,
* triángulos,
* escenas,
* guardado y carga.

### View

Corresponde al frontend web:

* dashboard técnico,
* paneles de visualización,
* controles,
* render en canvas.

### Controller

Coordina las solicitudes HTTP:

* carga de imagen,
* detección de landmarks,
* triangulación,
* proyección,
* guardado y carga.

### Services

Encapsulan la lógica del sistema:

* lectura de imágenes,
* detección facial,
* triangulación,
* proyección,
* almacenamiento.

---

## 5. Estructura de carpetas

```text
face-3d-mesh-app/
│
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   │   ├── face_controller.py
│   │   │   └── storage_controller.py
│   │   ├── models/
│   │   │   ├── image_model.py
│   │   │   ├── landmark_model.py
│   │   │   ├── mesh_model.py
│   │   │   ├── scene_model.py
│   │   │   └── storage_model.py
│   │   ├── services/
│   │   │   ├── face_mesh_detector.py
│   │   │   ├── image_input_service.py
│   │   │   ├── landmark_expansion_service.py
│   │   │   ├── mesh_builder.py
│   │   │   ├── mesh_storage_service.py
│   │   │   └── projection_service.py
│   │   ├── models_store/
│   │   │   └── face_landmarker.task
│   │   ├── config.py
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── api.js
│   │   └── app.js
│   └── index.html
│
├── samples/
│   ├── input/
│   └── saved_meshes/
│
├── docs/
├── .gitignore
└── README.md
```

---

## 6. Flujo funcional del sistema

```text
Entrada (archivo o webcam)
→ validación de imagen
→ detección facial
→ landmarks 3D
→ triangulación Delaunay
→ filtrado de triángulos
→ normalización 3D
→ rotación y proyección
→ render en dashboard
→ guardado / carga de resultados
```

---

## 7. Fórmulas implementadas en el backend

La rotación y proyección se calcularon en Python.

```text
XT = X·cos(a) - Z·sin(a)
YT = Y·cos(b) - Z·cos(a)·sin(b) - X·sin(a)·sin(b)
ZT = Z·cos(a)·cos(b) + X·sin(a)·cos(b) + Y·sin(b)

XP = D·XT / (D - ZT)
YP = D·YT / (D - ZT)
```

Donde:

* `a` = rotación horizontal,
* `b` = rotación vertical,
* `D` = distancia o zoom,
* `(X, Y, Z)` = coordenadas 3D normalizadas,
* `(XP, YP)` = coordenadas 2D proyectadas.

---

## 8. Funcionalidades implementadas

### Entrada de datos

* Carga de imagen desde archivo.
* Captura de frame desde webcam.

### Procesamiento facial

* Detección de landmarks faciales con MediaPipe Face Landmarker.
* Uso de coordenadas 3D relativas (`x`, `y`, `z`).

### Malla y geometría

* Construcción de malla con triangulación de Delaunay.
* Filtrado de triángulos largos o fuera del contorno permitido.

### Visualización

* Panel de imagen real.
* Panel de foto con landmarks.
* Panel de landmarks limpios.
* Panel de foto con Delaunay.
* Panel de Delaunay limpio.
* Panel de proyección 3D interactiva.
* Panel de respuesta del backend.
* Mini eje XYZ en el visor 3D.

### Interacción

* Rotación horizontal.
* Rotación vertical.
* Zoom por distancia.
* Guardado de resultados.
* Carga de resultados guardados.

---

## 9. Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

* Python 3.12
* Git
* Visual Studio Code
* extensión Python para VS Code
* GitLens

También debes tener descargado el modelo:

```text
backend/app/models_store/face_landmarker.task
```

---

## 10. Configuración del entorno virtual

Desde la raíz del proyecto:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Verificación del intérprete activo:

```cmd
where python
python -c "import sys; print(sys.executable)"
python --version
```

La ruta activa debe apuntar a:

```text
...\face-3d-mesh-app\.venv\Scripts\python.exe
```

---

## 11. Instalación de dependencias

Con el entorno virtual activo:

```cmd
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

---

## 12. Ejecución del backend

Desde la raíz del proyecto:

```cmd
python -m uvicorn backend.app.main:app --reload
```

Backend disponible en:

```text
http://127.0.0.1:8000
```

Documentación Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 13. Ejecución del frontend

En otra terminal, desde la raíz del proyecto:

```cmd
python -m http.server 5500
```

Frontend disponible en:

```text
http://127.0.0.1:5500/frontend/
```

---

## 14. Endpoints principales

### Salud del sistema

* `GET /health`

### Procesamiento facial

* `POST /api/face/upload-image`
* `POST /api/face/detect-landmarks`
* `POST /api/face/triangulate`
* `POST /api/face/project-mesh`

### Almacenamiento

* `GET /api/storage/ping`
* `POST /api/storage/save`
* `GET /api/storage/list`
* `GET /api/storage/load/{filename}`

---

## 15. Flujo de uso recomendado

### Opción 1 — Archivo

1. Subir fotografía.
2. Validar imagen.
3. Generar malla 2D.
4. Proyectar malla 3D.
5. Ajustar rotación y zoom.
6. Guardar resultado si se desea.

### Opción 2 — Webcam

1. Activar webcam.
2. Capturar frame.
3. Validar imagen.
4. Generar malla 2D.
5. Proyectar malla 3D.
6. Guardar resultado si se desea.

### Carga de resultado previo

1. Actualizar lista.
2. Seleccionar archivo guardado.
3. Cargar resultado.
4. Revisar paneles 2D y 3D.

---

## 16. Formato de guardado

Los resultados se guardan como JSON en:

```text
samples/saved_meshes/
```

El contenido puede incluir:

* landmarks,
* malla 2D,
* proyección 3D,
* parámetros de escena.

---

## 17. Flujo de trabajo con Git

### Inicialización

```cmd
git init
git branch -M main
git checkout -b dev
```

### Trabajo recomendado

* `main` → rama estable
* `dev` → integración de desarrollo

### Ciclo sugerido

1. trabajar en `dev`,
2. hacer commits pequeños por etapa,
3. revisar cambios con GitLens,
4. comparar `dev` vs `main`,
5. fusionar a `main` cuando esté validado.

### Comandos útiles

```cmd
git status
git branch
git add .
git commit -m "mensaje"
git log --oneline
```

---

## 18. Uso recomendado de GitLens

GitLens conviene usarlo para:

* revisar qué cambió en cada archivo,
* inspeccionar historial de commits,
* comparar `main` vs `dev`,
* validar que no se mezclaron cambios innecesarios.

Momentos clave:

* después del backend base,
* después de la detección facial,
* después de la triangulación,
* después de la proyección 3D,
* antes del merge final.

---

## 19. Decisiones técnicas importantes

### Detección facial

Se eligió **MediaPipe Face Landmarker** porque ofrece landmarks faciales 3D modernos y es compatible con el objetivo del proyecto.

### Triangulación

Se usó **Delaunay** porque permite construir una malla facial limpia a partir de puntos dispersos.

### Proyección

La lógica de rotación, normalización y perspectiva se implementó en el backend para cumplir el requisito de concentrar la matemática en Python.

### Frente y orejas sintéticas

Se probaron extensiones sintéticas para frente y laterales, pero finalmente se eliminaron para conservar una malla más limpia y más fiel al contorno facial real detectado.

---

## 20. Ventajas del sistema actual

* Arquitectura clara y modular.
* Backend dominante, como requería el proyecto.
* Frontend ligero.
* Pipeline reutilizable para imagen y webcam.
* Persistencia en JSON.
* Dashboard técnico útil para demostración y defensa.

---

## 21. Limitaciones actuales

* No reconstruye orejas reales completas.
* No realiza modelado de cabeza completa.
* La proyección 3D es una visualización geométrica proyectada, no una malla 3D sólida renderizada con motor 3D.
* La webcam trabaja por captura de frame, no por streaming continuo con landmarks en tiempo real.

---

## 22. Mejoras futuras posibles

* Voronoi real como panel adicional.
* Streaming en tiempo real desde webcam.
* Mejora del filtrado de triángulos por contorno facial.
* Exportación de resultados a otros formatos.
* Render 3D con WebGL o Three.js.
* Modo de análisis multi-rostro.
* Integración opcional con un modelo 3D facial más denso.

---

## 23. Checklist de pruebas

### Backend

* [ ] `/health` responde correctamente.
* [ ] `/api/face/upload-image` valida imagen.
* [ ] `/api/face/detect-landmarks` devuelve landmarks.
* [ ] `/api/face/triangulate` devuelve vértices y triángulos.
* [ ] `/api/face/project-mesh` devuelve proyección 3D.
* [ ] `/api/storage/save` guarda un resultado.
* [ ] `/api/storage/list` lista archivos guardados.
* [ ] `/api/storage/load/{filename}` carga correctamente un JSON.

### Frontend

* [ ] se visualiza la imagen real,
* [ ] se muestran landmarks,
* [ ] se muestra Delaunay sobre imagen,
* [ ] se muestra Delaunay limpio,
* [ ] se muestra proyección 3D,
* [ ] el eje XYZ aparece,
* [ ] la webcam captura un frame,
* [ ] se puede guardar y cargar un resultado.

---

## 24. Autor y contexto de uso

Proyecto desarrollado como prototipo académico/técnico orientado a visión artificial, geometría computacional y visualización interactiva de malla facial en entorno web.

---

## 25. Recomendación final de ejecución

Para ejecutar correctamente el proyecto:

1. activar el entorno virtual,
2. iniciar el backend con Uvicorn,
3. iniciar el frontend con `http.server`,
4. abrir el navegador,
5. probar primero con imagen,
6. luego probar con webcam,
7. guardar al menos un resultado,
8. validar carga posterior.
