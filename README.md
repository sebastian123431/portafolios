Portafolios integra Contratos Ágiles como una app Django en `proyectos.contratos_agiles`.
El único proyecto principal es `portafolios`; conserva su `manage.py`, settings,
WSGI, ASGI y base SQLite. No se implementó el modal ni se rediseñó el portafolio.

```text
portafolios/
├── manage.py
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
├── portafolios/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── portafoliosapp/                 # App original conservada
├── templates/templatesapp/         # Templates del portafolio
├── static/portafoliosapp/           # Assets del portafolio
└── proyectos/
    ├── __init__.py
    ├── contratos_agiles/
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── admin.py
    │   ├── models.py
    │   ├── forms.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── email_utils.py
    │   ├── sendgrid_service.py
    │   ├── tests.py
    │   ├── tasks.py.legacy
    │   ├── migrations/            # Seis migraciones originales
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── documents.py
    │   │   ├── word_conversion.py
    │   │   └── availability.py
    │   ├── testdata/              # Rostro ficticio y procedencia de la imagen
    │   ├── templates/contratos_agiles/  # 28 templates
    │   └── static/contratos_agiles/
    │       ├── css/
    │       ├── images/
    │       └── pdfjs/
    └── agilizacion_contrato-main/  # Respaldo local privado, ignorado
```

Los archivos locales `.env`, `db.sqlite3`, `media/`, `staticfiles/`, `.venv/`
y `.tmp/` no forman parte del código distribuible. `media/` se crea al cargar
archivos. No se copiaron la base antigua, fotografías ni contratos originales.

**Ejecución local**

Desde la raíz, en PowerShell, se puede activar el entorno existente:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

En una instalación nueva, crear primero el entorno con `python -m venv .venv`.
Se comprobó Django 5.2.15 tanto con Python 3.11 como con Python 3.14 en Windows.

- Portafolio: http://127.0.0.1:8000/
- Bibliografía: http://127.0.0.1:8000/bibliografia/
- Contratos Ágiles: http://127.0.0.1:8000/proyectos/contratos-agiles/
- Menú: http://127.0.0.1:8000/proyectos/contratos-agiles/menu/
- Administración compartida: http://127.0.0.1:8000/admin/

**Configuración principal**

`portafolios/settings.py` registra `ContratosAgilesConfig`, mantiene
`ROOT_URLCONF = 'portafolios.urls'`, una sola conexión SQLite y el descubrimiento
de templates mediante `APP_DIRS`. Añade `MEDIA_ROOT = BASE_DIR / 'media'`,
`MEDIA_URL = '/media/'` y `X_FRAME_OPTIONS = 'SAMEORIGIN'`. CSRF sigue habilitado;
se quitaron las exenciones innecesarias de carga de imágenes y búsqueda.

`portafolios/urls.py` incluye las rutas de la app bajo
`proyectos/contratos-agiles/` y sirve media solamente en DEBUG. Las 39 rutas
funcionales originales están en `proyectos/contratos_agiles/urls.py`, con
namespace `contratos_agiles`. El administrador se comparte en `/admin/`.
Los redirects, los enlaces y las respuestas AJAX utilizan el router de Django.
La búsqueda devuelve `perfil_url` y `cargo_url` para construir sus enlaces.

Se usa solamente `python-dotenv` para cargar `.env`; las variables del proceso
tienen precedencia. `.env.example` contiene los nombres sin credenciales reales:

| Variable | Uso |
| --- | --- |
| `DJANGO_SECRET_KEY` | Clave propia de cada instalación. Obligatoria sin DEBUG. |
| `DJANGO_DEBUG` | `True` en desarrollo; `False` en despliegue. |
| `DJANGO_ALLOWED_HOSTS` | Dominios separados por comas. |
| `SENDGRID_API_KEY` | Clave nueva de SendGrid, opcional para navegar. |
| `DEFAULT_FROM_EMAIL` | Remitente verificado en SendGrid; ejemplo ficticio por defecto. |
| `CONTRATOS_CONTACT_PHONE` | Contacto opcional utilizado en correos de reingreso. |

En este entorno se generó una clave local nueva en `.env`, sin mostrarla ni
versionarla. Sin clave, DEBUG permite una clave efímera que cambia al reiniciar;
conviene configurar `.env` para mantener las sesiones y los enlaces de contacto.
Las claves antiguas se consideran expuestas y deben revocarse o rotarse antes
de volver a utilizar el servicio. No se copiaron al código integrado.

**Archivos creados y adaptados**

- Creados en la raíz: `requirements.txt`, `.gitignore`, `.env.example`, este
  `README.md`; también `.env` privado y un respaldo SQLite local bajo `.tmp/`.
- Creado `proyectos/__init__.py` y el paquete `proyectos/contratos_agiles/`.
  Se reutilizaron `admin.py`, `models.py` y las migraciones originales.
- Adaptados dentro de la nueva app: `apps.py`, `views.py`, `email_utils.py`,
  `sendgrid_service.py`, `forms.py` (antes `form.py`) y los 27 templates originales.
- Creados `urls.py`, los cuatro archivos de `services/`, las pruebas de integración
  y `plantilla_correo.html`, que faltaba en el proyecto original.
- Copiados los 378 assets originales bajo `static/contratos_agiles/`.
- Modificados del proyecto principal: `portafolios/settings.py` y
  `portafolios/urls.py`. Se preservaron las ediciones preexistentes del usuario
  en vistas, tests, templates, CSS y JavaScript del portafolio.
- Normalizados el acceso a media, las URLs de imágenes y el tratamiento de
  errores de los servicios. Informes y exportación usan ORM manteniendo campos
  y estructura del resultado. Se adaptó la importación a pandas actual y a la
  serialización JSON de fechas Excel. Se corrigió la creación duplicada de
  contratos en generación masiva y su búsqueda cuando ya existen varias
  generaciones individuales. Toda lectura, edición, extracción de imágenes y
  guardado DOCX reside ahora en `services/documents.py`, sin objetos DOCX en vistas.

**Migraciones y compatibilidad**

La ubicación Python es `proyectos.contratos_agiles`, pero la etiqueta Django
sigue siendo `contratoApp`. Las seis migraciones se copiaron idénticas, incluyendo
las dos ramas 0002 y su merge 0005. No se regeneró 0001 ni se alteraron modelos.
El `db_table = 'contratoApp_login'` del modelo Login se conserva porque forma
parte del estado histórico; retirarlo generaría un cambio de migración innecesario.
Las tablas históricas conviven con las del portafolio en la base principal.

Dependencias directas: Django 5.2.15, cryptography (ya usado por el portafolio),
Pillow, numpy, pandas >= 2.1, openpyxl, opencv-contrib-python >= 4.10 y < 5,
python-docx, fuzzywuzzy, python-Levenshtein, sendgrid y python-dotenv. `pywin32`
se instala únicamente en Windows mediante un environment marker.
OpenCV 5 carecía de los clasificadores esperados en la instalación comprobada;
la rama 4.x conservó el reconocimiento original. No se copió el antiguo listado
de dependencias transitivas.

No se requiere `docx2pdf`: las tres conversiones usan el mismo servicio COM de
Word. La antigua tarea Celery invocaba `actualizar_vigencia()`, inexistente en
el modelo, y no tenía consumidores ni configuración de worker. Se conserva
como `tasks.py.legacy`, sin activar Celery ni afirmar que esa tarea funciona.

**Servicios y límites de la comprobación**

- DOCX y previsualización HTML funcionan sin Word. La conversión DOCX a PDF
  requiere Windows, pywin32 y Microsoft Word. COM se ejecuta en un proceso
  auxiliar invisible con límite de 60 segundos, aislado del servidor Django.
  Se liberan la instancia privada de Word y COM al terminar. En otros sistemas
  responde con un mensaje controlado HTTP 503; las demás pantallas siguen
  disponibles. Se probaron las tres rutas con Microsoft Word real: PDF individual,
  PDF específico y ZIP masivo. Los archivos contienen encabezado y cierre PDF
  válidos, y los DOCX generados contienen los marcadores sustituidos. Las pruebas
  reales requieren la sesión normal de Windows, fuera de la restricción del agente.
- SendGrid necesita una clave nueva, remitente verificado y conexión. Sin
  configuración informa un error controlado. Asignar un cargo se conserva y
  muestra una advertencia si no puede enviarse el correo; un envío fallido no
  marca al trabajador como notificado. No se enviaron correos reales.
- Se probaron el detector Haar, el reconocedor LBPH y el registro de asistencia
  reales, sin mocks, usando `testdata/synthetic_face.png`, un rostro ficticio
  generado con ImageGen. Una captura con iluminación y compresión modificadas
  se reconoce y no duplica la asistencia; una imagen sin rostro se rechaza.
  Esto comprueba el flujo del motor, no la precisión biométrica con personas
  reales. La cámara física requiere permiso y un navegador conectado.
- El visor Office original requiere que Microsoft pueda acceder a la URL del
  documento; localhost no es accesible para ese servicio. Se conserva el enlace
  de descarga como alternativa. Los gráficos originales utilizan Chart.js remoto.
- El login heredado usa su tabla `Login` y contraseñas en texto plano, sin
  establecer una sesión Django ni proteger todas las vistas. Se preservó su
  comportamiento para esta integración; necesita una etapa específica de
  autenticación y permisos antes de una demo pública con cuentas reales.
- No se ejecutó un servidor Linux real. Las dependencias COM están aisladas;
  en Linux OpenCV puede requerir bibliotecas del sistema para importar `cv2`.

**Verificación realizada**

```text
python manage.py check                         Sin errores (0 silenced)
python manage.py showmigrations contratoApp     Seis migraciones reconocidas
python manage.py migrate                       Seis migraciones aplicadas OK
python manage.py makemigrations --check         No changes detected
python manage.py collectstatic --noinput        Completado
Pruebas con CONTRATOS_TEST_REAL_WORD=1          46 pruebas aprobadas
```

Para repetir la suite con Microsoft Word real desde una sesión normal de Windows:

```powershell
$env:CONTRATOS_TEST_REAL_WORD = "1"
python manage.py test proyectos.contratos_agiles portafoliosapp --noinput
Remove-Item Env:CONTRATOS_TEST_REAL_WORD
```

Sin esa variable, la única prueba optativa de Word se omite para poder ejecutar
la suite en servidores sin Office. Las 46 pruebas pasaron con Python 3.11 y con
el entorno `.venv` de Python 3.14, incluyendo las conversiones reales.
Incluyen las 39 rutas, registro/login con CSRF, trabajadores, búsquedas, perfiles,
cargos, informes, CSV/Excel, previsualización DOCX con imágenes y texto escapado,
marcadores y logo, rutas de documentos inválidas, PDF individual y masivo real,
correo sin configuración, carga de imágenes y el motor facial real con datos ficticios.
La comparación de código confirmó las migraciones idénticas y ningún endpoint
original perdido. No quedan referencias activas a los imports, templates o
rutas globales antiguos. Ocho bloques de JavaScript renderizado pasaron una
comprobación de sintaxis.

El servidor respondió HTTP 200 para `/`, `/bibliografia/`, la entrada y el menú
de Contratos Ágiles, su CSS y su logo. La base principal quedó sin trabajadores
ni contratos: los datos ficticios de pruebas se destruyeron con la base de test.
No hubo navegador conectado: quedan pendientes la inspección visual, la consola,
las interacciones reales de cámara y la comprobación interactiva completa.

**Legacy y pendientes antes de publicar**

El respaldo `proyectos/agilizacion_contrato-main/` sigue local e ignorado.
Su `manage.py`, y los `settings.py`, `urls.py`, `wsgi.py`, `asgi.py` del proyecto
antiguo, se renombraron con sufijo `.legacy`. Así se conserva su contenido sin
dejar otro proyecto Django operativo. Tras aceptar las comprobaciones, se pueden
eliminar esos archivos de arranque, `contratoApp/`, los templates/static
duplicados y su entorno virtual. Revisar y respaldar por separado su base y
`media/` privados antes de eliminar la carpeta completa. No se borraron datos.

`.gitignore` excluye secretos, bases, media, entornos, caches, temporales y
estáticos recolectados. Sin embargo, Git ya seguía 2470 archivos ahora ignorados:
2294 en `.tmp/`, la base SQLite, 25 archivos de bytecode y 150 en `staticfiles/`.
Retirarlos del índice conservando el disco fue bloqueado por la revisión
automática, que exige aprobación explícita para esa limpieza masiva. Ese paso
está pendiente y no se ha ejecutado.

El historial previo también contiene una SECRET_KEY literal. Cambiar el archivo
actual y añadir `.gitignore` no elimina secretos ni datos de commits anteriores.
No se reescribió el historial, no se creó un commit y no se publicó el repositorio.
La integración local está verificada con los límites anteriores; el repositorio
todavía no se considera listo para publicación pública.
