import json
from pathlib import Path
from urllib.parse import quote_plus

from django.contrib.staticfiles import finders
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from portafoliosapp.security import decrypt_value, encrypt_value

if not getattr(TemplateResponse, "_portfolio_context_compat", False):
    def _get_template_response_context(self):
        stored = self.__dict__.get("_portfolio_context")
        if stored is not None:
            return stored
        return self.context_data

    def _set_template_response_context(self, value):
        self.__dict__["_portfolio_context"] = value

    TemplateResponse.context = property(_get_template_response_context, _set_template_response_context)
    TemplateResponse._portfolio_context_compat = True


def versioned_static(path):
    """Return a static asset URL that changes when the file is replaced."""
    url = static(path)
    found_path = finders.find(path)
    if not found_path:
        return url

    try:
        version = int(Path(found_path).stat().st_mtime)
    except OSError:
        return url

    separator = "&" if "?" in url else "?"
    return f"{url}{separator}v={version}"


@csrf_protect
@require_POST
def reveal_contact(request):
    try:
        payload = json.loads(request.body or "{}")
        token = payload.get("token")
        if not token:
            return JsonResponse({"error": "Token requerido"}, status=400)
        value = decrypt_value(token)
        return JsonResponse({"value": value})
    except Exception:
        return JsonResponse({"error": "No autorizado"}, status=403)


def index(request):
    """Render the portfolio page as an interactive Anime.js bubble universe."""
    linkedin_url = "https://linkedin.com/in/sebastian-espindola-46a521334"
    github_url = "https://github.com/sebastian123431"
    linkedin_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={quote_plus(linkedin_url)}"
    campus_query = "INACAP Sede La Serena, Av. Francisco de Aguirre 389, La Serena, Chile"
    campus_lat = -29.9068
    campus_lng = -71.2502
    campus_map = f"https://www.google.com/maps?q={quote_plus(campus_query)}&output=embed"
    campus_link = f"https://www.google.com/maps/search/?api=1&query={quote_plus(campus_query)}"
    controlbins_logo = versioned_static("portafoliosapp/images/controlbins-logo.png")
    portrait_image = versioned_static("portafoliosapp/images/portrait/yo.png")

    def controlbins_view(filename):
        return versioned_static(f"portafoliosapp/projects/controlbins/views/{filename}")

    encrypted_email = encrypt_value("seba501090@gmail.com")
    encrypted_phone = encrypt_value("+56 9 5380 4158")
    encrypted_linkedin = encrypt_value(linkedin_url)
    encrypted_github = encrypt_value(github_url)

    context = {
        "name": "Sebastián Espíndola",
        "role": "Desarrollador Backend Python/Django y Full Stack",
        "title": "Sistemas web, APIs REST y aplicaciones Android offline-first.",
        "tech_stack": "Python · Django · Kotlin · SQL Server",
        "tagline": "Construyo sistemas asegurandome de que sean escalables",
        "site_css_src": versioned_static("portafoliosapp/css/style.css"),
        "site_js_src": versioned_static("portafoliosapp/js/main.js"),
        "summary": (
            "Desarrollador Backend Python/Django y Full Stack enfocado en sistemas web, APIs REST "
            "y aplicaciones Android offline-first. Construí ControlBins, una solución real en producción "
            "que digitalizó el 100% de la trazabilidad de bins para una empresa exportadora, respetando "
            "los flujos que los equipos ya usaban para que la adopción fuera natural."
        ),
        "contact": {
            "email": encrypted_email,
            "phone": encrypted_phone,
            "location": "Vicuña, Coquimbo, Chile",
            "linkedin": linkedin_url,
            "github": github_url,
            "linkedin_qr": linkedin_qr,
        },
        "contact_protected": {
            "email": encrypted_email,
            "phone": encrypted_phone,
            "linkedin": encrypted_linkedin,
            "github": encrypted_github,
        },
        "experience": {
            "title": "Asistente de Informática",
            "company": "Frutícola y Exportadora Atacama Ltda",
            "dates": "Dic 2023 - Jul 2025",
            "location": "Vicuña, Chile",
            "type": "Presencial, trabajo de temporada",
            "summary": (
                "Desarrollo y soporte de sistemas para digitalizar procesos operativos del packing, "
                "con foco principal en trazabilidad, sincronización de datos y continuidad operacional."
            ),
            "sections": [
                {
                    "heading": "Desarrollo de software",
                    "icon": "bi-code-slash",
                    "items": [
                        "Desarrollé una app Android Kotlin con backend Django REST y SQL Server para controlar la trazabilidad de bins.",
                        "Implementé sincronización cada 30 segundos, reconexión automática y modo offline con SQLite.",
                        "Diseñé validación de duplicados para resolver conflictos de identificadores entre sectores.",
                        "Llevé el sistema desde piloto funcional hasta producción, validado por jefatura.",
                        "Preparé una arquitectura modular para hasta 100 usuarios concurrentes.",
                    ],
                },
                {
                    "heading": "Soporte e infraestructura",
                    "icon": "bi-pc-display-horizontal",
                    "items": [
                        "Brindé soporte diario a usuarios, equipos, impresoras Zebra/Xerox y conectividad de red.",
                        "Realicé mantenimiento de notebooks, instalación de software corporativo y recuperación de archivos.",
                        "Apoyé continuidad operativa con respaldos, reportes y resolución de bloqueos de acceso.",
                    ],
                },
            ],
            "tags": ["Python", "Django REST Framework", "Kotlin", "SQL Server", "SQLite", "Postman"],
        },
        "education": {
            "degree": "Ingeniería en Informática",
            "institution": "INACAP, Sede La Serena",
            "graduation": "Abril 2025",
        },
    }

    controlbins_case = {
        "id": "controlbins-case",
        "label": "ControlBins",
        "icon": "bi-box-seam",
        "image": controlbins_logo,
        "kind": "case",
        "badge": "Proyecto empresarial",
        "content": (
            "Ecosistema de gestión operacional compuesto por una aplicación móvil y un panel web conectados "
            "mediante servicios backend. La app participa en la captura de información desde la operación, "
            "mientras que el dashboard centraliza consulta, gestión, reportes e históricos."
        ),
        "text": "Sistema de trazabilidad y gestión operacional para bins, despachos y procesos productivos.",
        "minuta": {
            "title": "Minuta del proyecto",
            "summary": "Caso de estudio visual basado en capturas autorizadas: captura operacional móvil, backend central, datos y dashboard web para gestión y análisis.",
            "points": [
                "Aplicación móvil orientada al registro de información operacional en terreno.",
                "Servicios backend para centralizar datos y sostener consultas del panel web.",
                "Dashboard con reportes, detalles, línea de tiempo e información histórica.",
            ],
            "outcome": "El código fuente permanece privado por políticas de la organización; se presenta evidencia visual autorizada.",
        },
        "sections": [
            {
                "heading": "Problema",
                "icon": "bi-exclamation-diamond",
                "items": [
                    "La trazabilidad de bins dependía de registros manuales y revisión operativa dispersa.",
                    "El proceso necesitaba continuidad en terreno incluso con conectividad intermitente.",
                    "La adopción debía sentirse cercana al flujo real de trabajo, no como una carga extra para los usuarios.",
                ],
            },
            {
                "heading": "Mi rol",
                "icon": "bi-person-check",
                "items": [
                    "Desarrollo end-to-end de la app Android, backend, API REST, modelo de datos y reportes.",
                    "Coordinación con usuarios operativos y jefatura para pasar de piloto a producción.",
                    "Diagnóstico y corrección de problemas reales de producción sin mentoría directa.",
                ],
            },
            {
                "heading": "Solución",
                "icon": "bi-diagram-3",
                "items": [
                    "App Android Kotlin con SQLite local para trabajo offline-first.",
                    "Backend Django REST con SQL Server para trazabilidad, respaldos y consultas operativas.",
                    "Sincronización automática cada 30 segundos, reconexión y validación de duplicados.",
                ],
            },
            {
                "heading": "Resultado",
                "icon": "bi-graph-up-arrow",
                "items": [
                    "Ecosistema operativo con captura móvil, centralización de datos y panel web de consulta.",
                    "Sistema preparado para revisar despachos, bins, conteos, análisis temporal e históricos.",
                ],
            },
        ],
        "architecture": [
            "Android Kotlin",
            "SQLite offline",
            "Django REST API",
            "SQL Server",
            "Reportes operativos",
        ],
        "note": "Por confidencialidad, no se publica código ni datos operacionales.",
        "actions": [
            {
                "label": "Explorar funcionamiento",
                "type": "case-study",
                "href": reverse("controlbins_study"),
                "title": "ControlBins",
                "icon": "bi-diagram-3",
            },
        ],
        "tags": ["Offline-first", "Trazabilidad", "API REST", "Producción", "Datos operativos"],
        "gallery": [],
        "case_study": {
            "intro": (
                "ControlBins registra información operacional y la convierte en datos consultables para gestión. "
                "La relación mostrada es funcional y de alto nivel; no incluye código, endpoints ni estructura interna."
            ),
            "privacy": "Capturas revisadas: contienen datos demo y no se detectaron RUT, correos, teléfonos, IPs ni credenciales reales.",
            "flow": ["Operación", "App móvil", "Servidor / API", "Datos", "Panel web", "Gestión / reportes / históricos"],
            "areas": [
                {
                    "title": "Captura operacional",
                    "icon": "bi-phone",
                    "summary": "La aplicación móvil participa en el registro de información desde terreno y la envía al backend cuando el flujo lo permite.",
                },
                {
                    "title": "Gestión y análisis",
                    "icon": "bi-display",
                    "summary": "El dashboard web permite consultar, organizar y analizar información mediante reportes, detalles e históricos.",
                },
            ],
            "screens": [
                {
                    "id": "login",
                    "title": "Inicio de sesión",
                    "group": "Acceso",
                    "src": controlbins_view("login.png"),
                    "description": "Punto de acceso al panel administrativo de ControlBins.",
                    "flow": ["Inicio de sesión", "Panel principal"],
                    "next": "dashboard",
                },
                {
                    "id": "dashboard",
                    "title": "Panel principal",
                    "group": "Dashboard",
                    "src": controlbins_view("dashboard.png"),
                    "description": "Centraliza el acceso a las áreas de consulta y análisis del sistema.",
                    "flow": ["Panel principal", "Despachos", "Bins", "Semillas", "Línea de tiempo"],
                },
                {
                    "id": "dispatch-report",
                    "title": "Reporte de despachos",
                    "group": "Despachos",
                    "src": controlbins_view("dispatch-report.png"),
                    "description": "Vista orientada a consultar y analizar información relacionada con despachos registrados.",
                    "flow": ["Panel principal", "Reporte de despachos", "Detalle de despacho"],
                    "next": "dispatch-detail",
                },
                {
                    "id": "dispatch-detail",
                    "title": "Detalle de despacho",
                    "group": "Despachos",
                    "src": controlbins_view("dispatch-detail.png"),
                    "description": "Permite profundizar en la información de una operación de despacho seleccionada.",
                    "flow": ["Reporte de despachos", "Detalle de despacho"],
                },
                {
                    "id": "bins-report",
                    "title": "Reporte de Bins",
                    "group": "Bins",
                    "src": controlbins_view("bins-report.png"),
                    "description": "Consolida y permite consultar información relacionada con bins registrados en la operación.",
                    "flow": ["Panel principal", "Reporte de Bins"],
                },
                {
                    "id": "seed-count",
                    "title": "Conteo de semillas",
                    "group": "Semillas",
                    "src": controlbins_view("seed-count.png"),
                    "description": "Módulo destinado a consultar y visualizar registros asociados al conteo de semillas.",
                    "flow": ["Panel principal", "Conteo de semillas"],
                },
                {
                    "id": "timeline",
                    "title": "Línea de tiempo",
                    "group": "Análisis",
                    "src": controlbins_view("timeline.png"),
                    "description": "Visualización temporal para revisar evolución y distribución de información registrada por año.",
                    "flow": ["Panel principal", "Línea de tiempo"],
                },
                {
                    "id": "bins-history",
                    "title": "Histórico de Bins",
                    "group": "Históricos",
                    "src": controlbins_view("bins-history.png"),
                    "description": "Permite consultar información consolidada de periodos anteriores asociada a bins.",
                    "flow": ["Históricos", "Histórico de Bins"],
                },
                {
                    "id": "dispatch-history",
                    "title": "Histórico de Despachos",
                    "group": "Históricos",
                    "src": controlbins_view("dispatch-history.png"),
                    "description": "Permite consultar operaciones de despacho correspondientes a periodos históricos.",
                    "flow": ["Históricos", "Histórico de Despachos", "Detalle histórico"],
                    "next": "dispatch-history-detail",
                },
                {
                    "id": "dispatch-history-detail",
                    "title": "Detalle histórico de despacho",
                    "group": "Históricos",
                    "src": controlbins_view("dispatch-history-detail.png"),
                    "description": "Profundiza en una operación de despacho de temporada histórica.",
                    "flow": ["Histórico de Despachos", "Detalle histórico"],
                },
                {
                    "id": "seed-history",
                    "title": "Histórico de Conteo de Semillas",
                    "group": "Históricos",
                    "src": controlbins_view("seed-history.png"),
                    "description": "Consulta registros históricos del proceso de conteo agrupados por cuartel y periodo.",
                    "flow": ["Históricos", "Histórico de Semillas"],
                },
                {
                    "id": "field-history",
                    "title": "Color por Cuartel",
                    "group": "Análisis histórico",
                    "src": controlbins_view("field-history.png"),
                    "description": "Visualización histórica relacionada con cuarteles, color actual, promedio de semilla y calendario de colores.",
                    "flow": ["Históricos", "Color por Cuartel"],
                },
                {
                    "id": "not-found",
                    "title": "Página no encontrada",
                    "group": "Manejo de error",
                    "src": controlbins_view("not-found.png"),
                    "description": "Evidencia secundaria de manejo visual de navegación no encontrada.",
                    "flow": ["Navegación", "404"],
                    "secondary": True,
                },
            ],
        },
        "simulation": {
            "title": "Flujo real de sincronización",
            "summary": "Simulación anonimizada de cómo un dato capturado en terreno se guarda sin conexión y luego llega al sistema central sin perder trazabilidad.",
            "sample": {
                "id_bin": "BIN-946464",
                "fecha_cosecha": "2026-01-18",
                "tara_bins": "18.40 kg",
                "peso_bruto": "342.60 kg",
                "peso_neto": "324.20 kg",
                "estado": "disponible",
                "estatus": "certificada",
            },
            "steps": [
                {
                    "label": "Ingreso en terreno",
                    "icon": "bi-phone",
                    "detail": "El operario registra el bin desde el teléfono: escanea el código, ingresa fecha, tara y peso bruto. La app calcula el peso neto automáticamente.",
                },
                {
                    "label": "Revisión antes de guardar",
                    "icon": "bi-shield-check",
                    "detail": "La app revisa que no falten datos importantes y que el bin no exista ya en el teléfono, en registros pendientes o en el índice descargado del sistema.",
                },
                {
                    "label": "Guardado sin conexión",
                    "icon": "bi-database",
                    "detail": "Si no hay internet, el dato queda guardado dentro del teléfono. Técnicamente se almacena en SQLite/Room como pendiente de sincronizar.",
                },
                {
                    "label": "Lista de espera",
                    "icon": "bi-list-task",
                    "detail": "La app agrega el registro a una lista de espera. Así sabe exactamente qué debe enviar cuando vuelva la conexión, sin duplicar el mismo bin.",
                },
                {
                    "label": "Conexión recuperada",
                    "icon": "bi-arrow-repeat",
                    "detail": "Cuando vuelve la señal, la app inicia la sincronización en segundo plano. Primero envía los bins y después los procesos que dependen de ellos.",
                },
                {
                    "label": "Envío al servidor",
                    "icon": "bi-cloud-upload",
                    "detail": "El teléfono envía el dato al backend mediante una API REST. En términos técnicos, Android usa Retrofit para comunicarse con Django.",
                },
                {
                    "label": "Registro central",
                    "icon": "bi-server",
                    "detail": "El servidor guarda el bin en la base de datos central SQL Server y responde a la app que el dato quedó confirmado.",
                },
                {
                    "label": "Confirmación final",
                    "icon": "bi-check2-circle",
                    "detail": "La app actualiza su copia local, marca el bin como sincronizado y conserva cualquier error visible para poder revisarlo después.",
                },
            ],
        },
    }

    contratos_agiles_case = {
        "id": "contratos-agiles",
        "label": "Contratos Ágiles",
        "icon": "bi-file-earmark-text",
        "kind": "case",
        "badge": "Proyecto empresarial",
        "content": (
            "Sistema web empresarial orientado a digitalizar y automatizar la "
            "generación de contratos laborales y la gestión de trabajadores temporales."
        ),
        "text": "Automatización contractual con Django, JavaScript, HTML5, CSS3 y base de datos relacional.",
        "minuta": {
            "title": "Proyecto empresarial",
            "summary": (
                "Plataforma web para centralizar información laboral, administrar trabajadores, "
                "utilizar plantillas contractuales y apoyar procesos administrativos de contratación."
            ),
            "points": [
                "Desarrollado en equipo como solución de software para gestión empresarial y agrícola.",
                "Integra vistas de gestión, procesos documentales y módulos administrativos.",
                "Prioriza orden de datos, continuidad de flujo y reducción de errores manuales.",
            ],
            "outcome": "Ficha profesional del proyecto integrada al portafolio con acceso a la aplicación real.",
        },
        "sections": [
            {
                "heading": "Problema",
                "icon": "bi-exclamation-diamond",
                "items": [
                    "El proceso administrativo de generación de contratos requería manejo manual de información y documentos.",
                    "La gestión de trabajadores temporales necesitaba centralizar datos y disminuir riesgo de errores.",
                    "El flujo debía ser comprensible para usuarios administrativos, no solo para perfiles técnicos.",
                ],
            },
            {
                "heading": "Solución",
                "icon": "bi-diagram-3",
                "items": [
                    "Aplicación web Django para administrar trabajadores, contratos y procesos relacionados.",
                    "Uso de plantillas contractuales para apoyar la generación documental.",
                    "Vistas organizadas para gestión de trabajadores, reportes, asistencia y administración contractual.",
                ],
            },
            {
                "heading": "Mi participación",
                "icon": "bi-person-check",
                "items": [
                    "Participé en desarrollo backend y frontend dentro de un proyecto realizado en equipo.",
                    "Apoyé implementación de procesos de automatización contractual y vistas de gestión.",
                    "Colaboré en modelamiento lógico, detección de errores y pruebas funcionales del sistema.",
                ],
            },
            {
                "heading": "Tecnologías",
                "icon": "bi-cpu",
                "items": [
                    "Python, Django, JavaScript, HTML5, CSS3, Git y base de datos relacional.",
                    "Automatización documental aplicada a contratos laborales y gestión administrativa.",
                ],
            },
            {
                "heading": "Funcionalidades principales",
                "icon": "bi-list-check",
                "items": [
                    "Gestión de trabajadores, cargos, contratos, asistencia y reportes.",
                    "Carga de plantillas, importación de información y generación de documentos.",
                    "Navegación por módulos administrativos dentro de la aplicación real.",
                ],
            },
            {
                "heading": "Aprendizajes",
                "icon": "bi-lightbulb",
                "items": [
                    "Fortalecí criterio para integrar backend, vistas, datos y procesos documentales en una solución completa.",
                    "Fortalecí habilidades para comunicar decisiones técnicas dentro de un proyecto empresarial con alcance funcional real.",
                ],
            },
        ],
        "architecture": [
            "Python",
            "Django",
            "JavaScript",
            "HTML5 / CSS3",
            "Base de datos relacional",
            "Automatización documental",
        ],
        "tags": ["Proyecto empresarial", "Django", "JavaScript", "Gestión contractual", "Automatización documental"],
        "actions": [
            {
                "label": "Ver proyecto",
                "type": "live-demo",
                "href": reverse("contratos_agiles:login"),
                "title": "Contratos Ágiles",
                "icon": "bi-window-fullscreen",
            },
        ],
    }

    certificate_assets = "/static/portafoliosapp/images/certificates"

    bubbles = [
        {
            "id": "profile",
            "label": "Perfil",
            "color": "#7cff2f",
            "icon": "bi-person-badge",
            "type": "center",
            "content": context["summary"],
            "name": context["name"],
            "title": context["role"],
            "subtitle": context["title"],
            "tagline": context["tagline"],
            "stats": ["Python", "Django", "Kotlin", "SQL Server"],
            "actions": [
                {
                    "label": "Ver bibliografia",
                    "href": "/bibliografia/",
                    "icon": "bi-person-vcard",
                },
            ],
            "sections": [
                {
                    "heading": "Autónomo",
                    "icon": "bi-lightning-charge",
                    "items": [
                        "Resolví bugs y decisiones técnicas de producción investigando, probando e iterando hasta encontrar la causa raíz.",
                    ],
                },
                {
                    "heading": "Adaptabilidad y flexibilidad",
                    "icon": "bi-signpost-split",
                    "items": [
                        "Me adapté a requerimientos operativos cambiantes sin perder el foco en la calidad del dato y la continuidad del sistema.",
                    ],
                },
                {
                    "heading": "Aprendizaje aplicado",
                    "icon": "bi-stars",
                    "items": [
                        "Aprendo lo necesario para cerrar problemas reales: backend, mobile, datos, soporte e inteligencia artificial aplicada.",
                    ],
                },
            ],
        },
        {
            "id": "projects",
            "label": "Proyectos",
            "color": "#39ff14",
            "icon": "bi-rocket-takeoff",
            "content": "Soluciones digitales creadas para trazabilidad, automatización y continuidad operativa.",
            "children": [
                controlbins_case,
                contratos_agiles_case,
            ],
        },
        {
            "id": "tech",
            "label": "Habilidades técnicas",
            "color": "#00e6ff",
            "icon": "bi-terminal",
            "content": "Stack organizado por áreas para construir sistemas web, móviles, datos y soporte operativo.",
            "children": [
                {
                    "label": "Backend",
                    "icon": "bi-hdd-network",
                    "level": "Principal",
                    "text": "Desarrollo lógica de servidor con Python, Django y Django REST Framework, priorizando APIs claras, validaciones y persistencia confiable.",
                    "sections": [
                        {
                            "heading": "Qué construyo",
                            "icon": "bi-braces",
                            "items": [
                                "Endpoints REST para conectar aplicaciones móviles, formularios web y procesos internos.",
                                "Validaciones de negocio para evitar registros incompletos, duplicados o inconsistentes.",
                                "Estructuras modulares para que el sistema pueda crecer sin volverse difícil de mantener.",
                            ],
                        },
                        {
                            "heading": "Aplicación real",
                            "icon": "bi-box-seam",
                            "items": [
                                "En ControlBins conecté una app Android con backend Django REST y SQL Server para trazabilidad en producción.",
                            ],
                        },
                    ],
                    "tags": ["Python", "Django", "DRF", "APIs REST"],
                },
                {
                    "label": "Mobile",
                    "icon": "bi-phone",
                    "level": "Android",
                    "text": "Construyo aplicaciones Android en Kotlin pensadas para terreno, donde la conexión puede fallar y el dato igual debe conservarse.",
                    "sections": [
                        {
                            "heading": "Qué resuelvo",
                            "icon": "bi-wifi-off",
                            "items": [
                                "Formularios móviles con guardado local para evitar pérdida de información.",
                                "Sincronización posterior con el servidor cuando vuelve la conexión.",
                                "Flujos simples para usuarios operativos que necesitan registrar datos rápido.",
                            ],
                        },
                        {
                            "heading": "Stack",
                            "icon": "bi-phone-flip",
                            "items": [
                                "Kotlin, Android Studio, SQLite/Room, Retrofit y enfoque offline-first.",
                            ],
                        },
                    ],
                    "tags": ["Kotlin", "Android", "SQLite", "Offline-first"],
                },
                {
                    "label": "Datos",
                    "icon": "bi-database",
                    "level": "Operacional",
                    "text": "Trabajo con bases de datos relacionales y reportes para que la información operativa sea trazable, consultable y útil.",
                    "sections": [
                        {
                            "heading": "Qué manejo",
                            "icon": "bi-table",
                            "items": [
                                "Modelado relacional para procesos de trazabilidad, estados y registros operativos.",
                                "Consultas, reportes y revisión de consistencia en SQL Server.",
                                "Preparación y limpieza de datos cuando la información viene desde planillas o procesos manuales.",
                            ],
                        },
                        {
                            "heading": "Criterio",
                            "icon": "bi-shield-check",
                            "items": [
                                "Me preocupo de que el dato tenga origen claro, estado verificable y posibilidad de auditoría.",
                            ],
                        },
                    ],
                    "tags": ["SQL Server", "Modelo relacional", "ETL", "Reportes"],
                },
                {
                    "label": "Herramientas",
                    "icon": "bi-tools",
                    "level": "Flujo técnico",
                    "text": "Uso herramientas de desarrollo y prueba para ordenar el trabajo, validar integraciones y reducir errores antes de llegar a producción.",
                    "sections": [
                        {
                            "heading": "Flujo de trabajo",
                            "icon": "bi-git",
                            "items": [
                                "Control de versiones con Git y preparación para publicar repositorios en GitHub.",
                                "Pruebas manuales de APIs con Postman y revisión de respuestas del backend.",
                                "Automatización de tareas repetitivas para ahorrar tiempo y estandarizar procesos.",
                            ],
                        }
                    ],
                    "tags": ["Git", "GitHub", "Postman", "Automatización"],
                },
                {
                    "label": "Infraestructura",
                    "icon": "bi-router",
                    "level": "Complemento",
                    "text": "Tengo base práctica en soporte, redes y continuidad operativa, lo que me ayuda a construir software pensando en el entorno real donde se usa.",
                    "sections": [
                        {
                            "heading": "Dónde aporta",
                            "icon": "bi-router",
                            "items": [
                                "Diagnóstico de conectividad entre usuarios, equipos, servidores e impresoras.",
                                "Mantención de notebooks, instalación de software y apoyo a continuidad diaria.",
                                "Comprensión del impacto operativo cuando una aplicación, red o equipo deja de funcionar.",
                            ],
                        }
                    ],
                    "tags": ["Redes", "Soporte", "Mantenimiento", "Continuidad"],
                },
            ],
        },
        {
            "id": "experience",
            "label": "Experiencia",
            "color": "#ff8a1c",
            "icon": "bi-briefcase",
            "image": controlbins_logo,
            "content": context["experience"]["summary"],
            "children": [
                {
                    "label": context["experience"]["title"],
                    "icon": "bi-person-workspace",
                    "image": controlbins_logo,
                    "kind": "job",
                    "badge": "Experiencia laboral",
                    "text": (
                        f'{context["experience"]["company"]} | {context["experience"]["dates"]} | '
                        f'{context["experience"]["location"]}. {context["experience"]["summary"]}'
                    ),
                    "related_project": controlbins_case,
                    "sections": context["experience"]["sections"],
                    "tags": context["experience"]["tags"],
                },
            ],
        },
        {
            "id": "education",
            "label": "Estudios",
            "color": "#63ff74",
            "icon": "bi-mortarboard",
            "content": "Ingeniería en Informática | INACAP Sede La Serena | Titulado: Abril 2025.",
            "institution": "INACAP Sede La Serena",
            "children": [
                {
                    "label": "INACAP Sede La Serena",
                    "icon": "bi-geo-alt-fill",
                    "kind": "location",
                    "badge": "Campus",
                    "map_embed": campus_map,
                    "map_link": campus_link,
                    "map_address": "Av. Francisco de Aguirre 389, La Serena",
                    "route": True,
                    "route_destination": campus_query,
                "route_destination_name": "INACAP Sede La Serena",
                "route_destination_lat": campus_lat,
                "route_destination_lng": campus_lng,
                "route_fallback_origin": "Vicuña, Coquimbo, Chile",
                "route_fallback_origin_lat": -30.0319,
                "route_fallback_origin_lng": -70.7081,
                "directions_link": f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(campus_query)}&travelmode=driving",
                "text": "Sede donde cursé Ingeniería en Informática. La ruta se calcula solo si el visitante decide compartir su ubicación.",
            },
                {
                    "label": context["education"]["degree"],
                    "icon": "bi-mortarboard-fill",
                    "kind": "degree",
                    "badge": "Carrera profesional",
                    "text": (
                        "Título profesional obtenido en INACAP. Formación base en desarrollo de software, "
                        "bases de datos, redes, soporte e infraestructura tecnológica."
                    ),
                    "issuer": "Instituto Profesional INACAP",
                    "date": "08 de abril de 2025",
                    "evidence": {
                        "src": f"{certificate_assets}/titulo-ingeniero-informatica.png",
                        "alt": "Certificado de título de Ingeniero en Informática",
                        "caption": "Título profesional de Ingeniero en Informática, INACAP.",
                    },
                    "sections": [
                        {
                            "heading": "Qué acredita",
                            "icon": "bi-patch-check",
                            "items": [
                                "Formación profesional en informática aplicada a desarrollo, datos, redes y soporte.",
                                "Base técnica para diseñar soluciones completas, desde la aplicación hasta la infraestructura.",
                            ],
                        }
                    ],
                },
                {
                    "label": "Desarrollador Full Stack",
                    "icon": "bi-window-stack",
                    "kind": "certificate",
                    "badge": "162 horas",
                    "text": "Certificación INACAP orientada a construir aplicaciones completas, conectando interfaz, lógica de negocio, APIs y bases de datos.",
                    "issuer": "Instituto Profesional INACAP",
                    "date": "04 de septiembre de 2025",
                    "evidence": {
                        "src": f"{certificate_assets}/cert-fullstack.png",
                        "alt": "Certificado en Desarrollador Full Stack",
                        "caption": "Certificado en Desarrollador Full Stack, 162 horas.",
                    },
                    "sections": [
                        {
                            "heading": "Valor profesional",
                            "icon": "bi-code-slash",
                            "items": [
                                "Refuerza mi perfil para desarrollar soluciones web de punta a punta.",
                                "Complementa mi experiencia práctica con Django REST, SQL Server y aplicaciones conectadas a APIs.",
                            ],
                        }
                    ],
                },
                {
                    "label": "Soporte Computacional",
                    "icon": "bi-pc-display",
                    "kind": "certificate",
                    "badge": "126 horas",
                    "text": "Certificación INACAP enfocada en diagnóstico, mantención y continuidad operativa de equipos y usuarios.",
                    "issuer": "Instituto Profesional INACAP",
                    "date": "04 de septiembre de 2025",
                    "evidence": {
                        "src": f"{certificate_assets}/cert-soporte-computacional.png",
                        "alt": "Certificado en Soporte Computacional",
                        "caption": "Certificado en Soporte Computacional, 126 horas.",
                    },
                    "sections": [
                        {
                            "heading": "Valor profesional",
                            "icon": "bi-tools",
                            "items": [
                                "Me permite entender los problemas desde la mirada del usuario final y de la operación diaria.",
                                "Aporta criterio para resolver incidentes de hardware, software, red e impresoras sin afectar la continuidad del trabajo.",
                            ],
                        }
                    ],
                },
                {
                    "label": "Arquitectura Cloud",
                    "icon": "bi-cloud-arrow-up",
                    "kind": "certificate",
                    "badge": "198 horas",
                    "text": "Certificación INACAP orientada a comprender componentes cloud, despliegue, disponibilidad y diseño de soluciones escalables.",
                    "issuer": "Instituto Profesional INACAP",
                    "date": "04 de septiembre de 2025",
                    "evidence": {
                        "src": f"{certificate_assets}/cert-arquitectura-cloud.png",
                        "alt": "Certificado en Arquitectura Cloud",
                        "caption": "Certificado en Arquitectura Cloud, 198 horas.",
                    },
                    "sections": [
                        {
                            "heading": "Valor profesional",
                            "icon": "bi-cloud-check",
                            "items": [
                                "Aporta una base para pensar sistemas con disponibilidad, respaldo y crecimiento futuro.",
                                "Complementa mi experiencia en backend, bases de datos y automatización de procesos.",
                            ],
                        }
                    ],
                },
                {
                    "label": "CCNAv7: Introduction to Networks",
                    "icon": "bi-diagram-3-fill",
                    "kind": "certificate",
                    "badge": "Cisco",
                    "text": "Certificación de Cisco Networking Academy sobre fundamentos de redes, conectividad, direccionamiento IP y resolución de problemas.",
                    "issuer": "Cisco Networking Academy",
                    "date": "03 de agosto de 2023",
                    "evidence": {
                        "src": f"{certificate_assets}/cert-ccna-introduction-networks.jpg",
                        "alt": "Certificado CCNAv7 Introduction to Networks",
                        "caption": "CCNAv7: Introduction to Networks, Cisco Networking Academy.",
                    },
                    "gallery": [
                        {
                            "src": f"{certificate_assets}/cert-ccna-course-completion.jpg",
                            "alt": "Certificado de finalización del curso CCNA Introduction to Networks",
                            "caption": "Detalle del curso: configuración básica de redes, direccionamiento IPv4/IPv6 y troubleshooting.",
                        }
                    ],
                    "sections": [
                        {
                            "heading": "Valor profesional",
                            "icon": "bi-router",
                            "items": [
                                "Me entrega base para entender conectividad entre dispositivos, servicios internos y aplicaciones en red.",
                                "Es útil para diagnosticar problemas de comunicación entre app móvil, API, servidor y usuarios.",
                            ],
                        }
                    ],
                },
                {
                    "label": "Google AI Essentials",
                    "icon": "bi-stars",
                    "kind": "certificate",
                    "badge": "5 cursos",
                    "text": "Programa especializado de Google y Coursera enfocado en uso responsable de inteligencia artificial, productividad y construcción de habilidades prácticas.",
                    "issuer": "Google / Coursera",
                    "date": "15 de agosto de 2026",
                    "evidence": {
                        "src": f"{certificate_assets}/cert-google-ai-essentials.png",
                        "alt": "Certificado Google AI Essentials",
                        "caption": "Google AI Essentials, programa de 5 cursos.",
                    },
                    "sections": [
                        {
                            "heading": "Valor profesional",
                            "icon": "bi-stars",
                            "items": [
                                "Refuerza mi capacidad para usar IA como apoyo en análisis, documentación, automatización y resolución de problemas.",
                                "Aporta criterio sobre uso responsable de herramientas de IA en flujos de trabajo reales.",
                            ],
                        }
                    ],
                },
            ],
        },
        {
            "id": "contact",
            "label": "Contacto",
            "color": "#ffb020",
            "icon": "bi-send",
            "content": "Actualmente busco nuevas oportunidades en desarrollo de software, automatización de procesos y áreas afines.",
            "children": [
                {"label": "Email", "icon": "bi-envelope", "text": "Información protegida. Haz clic para revelar el correo.", "secret_value": encrypted_email, "secret_kind": "email", "href": "#"},
                {"label": "Teléfono", "icon": "bi-telephone", "text": "Información protegida. Haz clic para revelar el teléfono.", "secret_value": encrypted_phone, "secret_kind": "phone", "href": "#"},
                {"label": "Ubicación", "icon": "bi-geo-alt", "text": f'{context["contact"]["location"]}. Base actual en la Región de Coquimbo, con interés en oportunidades remotas, híbridas o presenciales según el proyecto.'},
                {"label": "LinkedIn", "icon": "bi-linkedin", "text": "Perfil profesional para revisar trayectoria, contacto y actualizaciones laborales.", "href": linkedin_url, "secret_value": encrypted_linkedin, "secret_kind": "linkedin"},
                {"label": "GitHub", "icon": "bi-github", "text": "Repositorio profesional para revisar proyectos, codigo y evolucion tecnica.", "href": github_url, "secret_value": encrypted_github, "secret_kind": "github"},
            ],
        },
        {
            "id": "languages",
            "label": "Idiomas",
            "color": "#9bff6b",
            "icon": "bi-translate",
            "content": "Comunicación profesional en español nativo e inglés intermedio.",
            "children": [
                {"label": "Español", "icon": "bi-chat-quote", "level": "Nativo", "text": "Idioma nativo para comunicación con usuarios, levantamiento de requerimientos, documentación funcional y coordinación con equipos."},
                {"label": "Inglés", "icon": "bi-globe2", "level": "Intermedio", "text": "Lectura de documentación técnica, cursos, mensajes de error y recursos de desarrollo; útil para investigar soluciones y comprender herramientas."},
            ],
        },
    ]

    context["bubbles_json"] = json.dumps(bubbles, ensure_ascii=False)
    response = TemplateResponse(request, "templatesapp/index.html", context)
    response.render()
    response.context = response.context_data
    return response


def bibliografia(request):
    """Render the biography/bibliography page with the scroll-driven portrait effect."""
    context = {
        "name": "Sebastián Espíndola",
        "role": "Desarrollador Backend Python/Django y Full Stack",
        "github_url": "https://github.com/sebastian123431",
        "linkedin_url": "https://linkedin.com/in/sebastian-espindola-46a521334",
        "portrait_src": versioned_static("portafoliosapp/images/portrait/yo.png"),
        "bio_css_src": versioned_static("portafoliosapp/DigitalPortrait/DigitalPortrait.css"),
        "bio_js_src": versioned_static("portafoliosapp/DigitalPortrait/DigitalPortrait.js"),
    }
    return TemplateResponse(request, "templatesapp/bibliografia.html", context)


def controlbins_study(request):
    """Render the interactive ControlBins case study and dashboard evidence viewer."""
    def controlbins_view(filename):
        return versioned_static(f"portafoliosapp/projects/controlbins/views/{filename}")

    screens = [
        {
            "id": "login",
            "title": "Inicio de sesión",
            "group": "Acceso",
            "category": "operational",
            "src": controlbins_view("login.png"),
            "description": "Punto de acceso seguro al panel administrativo de ControlBins. Permite a los usuarios autorizados ingresar al entorno de gestión y reportería de operaciones de campo.",
            "flow": ["Inicio de sesión", "Panel principal"],
            "next": "dashboard",
            "next_label": "Ir al panel principal →",
            "badge": "Autenticación",
            "highlights": [
                "Control de acceso por credenciales y rol",
                "Interfaz corporativa adaptada a packing",
                "Punto de entrada al entorno administrativo",
            ],
        },
        {
            "id": "dashboard",
            "title": "Panel principal",
            "group": "Dashboard",
            "category": "operational",
            "src": controlbins_view("dashboard.png"),
            "description": "El panel centraliza las métricas consolidadas del día y los accesos rápidos a los reportes de despachos, bins, conteos de semillas y línea de tiempo, con gráficos de distribución por cuartel y destino.",
            "flow": ["Inicio", "Panel principal", "Módulos de gestión"],
            "next": "dispatch-report",
            "next_label": "Ver Reporte de despachos →",
            "badge": "Métricas & Accesos",
            "highlights": [
                "Accesos directos a los 4 reportes operativos",
                "Gráficos de distribución de bins y despachos en tiempo real",
                "Monitoreo de porcentajes y muestreos de semillas",
            ],
        },
        {
            "id": "dispatch-report",
            "title": "Reporte de despachos",
            "group": "Despachos",
            "category": "operational",
            "src": controlbins_view("dispatch-report.png"),
            "description": "Vista orientada a consultar, filtrar y analizar información de despachos registrados en el sistema, con filtros por temporada, fecha, sector y correlativo, permitiendo exportar a Excel y acceder al detalle.",
            "flow": ["Panel principal", "Reporte de despachos", "Detalle de despacho"],
            "next": "dispatch-detail",
            "next_label": "Ver Detalle de despacho →",
            "badge": "Operación de salida",
            "highlights": [
                "Filtros avanzados por temporada, fecha y sector",
                "Consolidación de kilos, total de bins y promedios",
                "Acceso directo con un clic a la vista de detalle",
            ],
        },
        {
            "id": "dispatch-detail",
            "title": "Detalle de despacho",
            "group": "Despachos",
            "category": "operational",
            "src": controlbins_view("dispatch-detail.png"),
            "description": "Permite profundizar en una operación de despacho específica: conductor, patentes, romana, pesajes brutos/netos, lista individual de bins despachados y resumen agrupado por variedad y cuartel.",
            "flow": ["Reporte de despachos", "Detalle de despacho"],
            "prev": "dispatch-report",
            "prev_label": "← Volver a Reporte de despachos",
            "next": "bins-report",
            "next_label": "Ver Reporte de Bins →",
            "badge": "Ficha detallada",
            "highlights": [
                "Trazabilidad individual de cada bin dentro del camión",
                "Cálculo automático de peso bruto, tara y peso neto",
                "Resumen por variedad, especie y cuadrilla cosechera",
            ],
        },
        {
            "id": "bins-report",
            "title": "Reporte de Bins",
            "group": "Bins",
            "category": "operational",
            "src": controlbins_view("bins-report.png"),
            "description": "Vista de trazabilidad individual de cada bin registrado en la operación. Permite consultar correlativos, tarjas, cuadrillas, cuarteles, especies, estado (disponible/despachado) y conteos de semillas asociados.",
            "flow": ["Panel principal", "Reporte de Bins"],
            "next": "seed-count",
            "next_label": "Ver Conteo de semillas →",
            "badge": "Trazabilidad de campo",
            "highlights": [
                "Auditoría unitaria de cada unidad de cosecha (bin)",
                "Registro de fecha de ingreso, cosecha y pesaje",
                "Acceso directo a exportación de planillas para auditoría",
            ],
        },
        {
            "id": "seed-count",
            "title": "Conteo de semillas",
            "group": "Semillas",
            "category": "operational",
            "src": controlbins_view("seed-count.png"),
            "description": "Módulo destinado a consultar y clasificar la información de muestreos de semillas realizados en terreno, categorizando los bins según rangos de tolerancia y niveles de color (verde, blanco, negro, amarillo).",
            "flow": ["Panel principal", "Conteo de semillas", "Color por cuartel"],
            "next": "field-history",
            "next_label": "Ver Análisis Color por Cuartel →",
            "badge": "Calidad & Muestreo",
            "highlights": [
                "Clasificación inmediata por niveles de color de calidad",
                "Monitoreo de porcentaje de semillas por cuartel y huerto",
                "Enlace directo con la herramienta analítica de cuarteles",
            ],
        },
        {
            "id": "timeline",
            "title": "Línea de tiempo",
            "group": "Análisis",
            "category": "operational",
            "src": controlbins_view("timeline.png"),
            "description": "Visualización temporal interactiva que consolida la evolución y distribución anual de bins, despachos, muestreos y kilogramos totales a través de las diferentes temporadas de producción.",
            "flow": ["Panel principal", "Línea de tiempo"],
            "next": "bins-history",
            "next_label": "Explorar Análisis Histórico →",
            "badge": "Evolución anual",
            "highlights": [
                "Comparativa gráfica de temporadas 2024, 2025 y 2026",
                "Desglose por especie y actividad total del periodo",
                "Herramienta analítica transversal para jefaturas",
            ],
        },
        {
            "id": "bins-history",
            "title": "Histórico de Bins",
            "group": "Históricos",
            "category": "historical",
            "src": controlbins_view("bins-history.png"),
            "description": "Permite consultar y auditar la información consolidada de temporadas anteriores asociada a los bins, seleccionando el año correspondiente para revisar la trazabilidad histórica de cosechas pasadas.",
            "flow": ["Históricos", "Histórico de Bins"],
            "next": "dispatch-history",
            "next_label": "Ver Histórico de Despachos →",
            "badge": "Auditoría histórica",
            "highlights": [
                "Modo histórico protegido contra modificaciones",
                "Selector de temporada para consulta retrospectiva",
                "Conservación de metadatos de cosechas anteriores",
            ],
        },
        {
            "id": "dispatch-history",
            "title": "Histórico de Despachos",
            "group": "Históricos",
            "category": "historical",
            "src": controlbins_view("dispatch-history.png"),
            "description": "Permite consultar las operaciones de despacho correspondientes a periodos agrícolas anteriores, conservando correlativos, pesajes, camiones y destinos para trazabilidad retrospectiva.",
            "flow": ["Históricos", "Histórico de Despachos", "Detalle histórico"],
            "next": "dispatch-history-detail",
            "next_label": "Ver Detalle de despacho histórico →",
            "badge": "Despachos anteriores",
            "highlights": [
                "Consulta de temporadas completas cerradas",
                "Filtros por sector, fecha y correlativo histórico",
                "Enlace con la vista de detalle histórico correspondiente",
            ],
        },
        {
            "id": "dispatch-history-detail",
            "title": "Detalle histórico de despacho",
            "group": "Históricos",
            "category": "historical",
            "src": controlbins_view("dispatch-history-detail.png"),
            "description": "Profundiza en la ficha técnica de un despacho de temporada pasada en modo solo lectura, mostrando los bins individuales, pesajes y resumen de variedades registrado en su momento.",
            "flow": ["Histórico de despachos", "Detalle histórico"],
            "prev": "dispatch-history",
            "prev_label": "← Volver a Histórico de despachos",
            "next": "seed-history",
            "next_label": "Ver Histórico de Conteo de Semillas →",
            "badge": "Ficha histórica",
            "highlights": [
                "Vista inmutable de la operación de despacho histórica",
                "Desglose completo de tarjas, tara y peso neto",
                "Respaldo documental de temporadas previas",
            ],
        },
        {
            "id": "seed-history",
            "title": "Histórico de Conteo de Semillas",
            "group": "Históricos",
            "category": "historical",
            "src": controlbins_view("seed-history.png"),
            "description": "Consulta registros históricos del proceso de muestreo de semillas de temporadas previas, presentados agrupados por cuartel y huerto para facilitar comparativas interanuales de calidad.",
            "flow": ["Históricos", "Histórico de Semillas"],
            "next": "field-history",
            "next_label": "Ver Color por Cuartel →",
            "badge": "Muestreos anteriores",
            "highlights": [
                "Agrupación jerárquica por cuartel y sector",
                "Comparativa de porcentajes y niveles de semilla históricos",
                "Control de calidad retrospectivo",
            ],
        },
        {
            "id": "field-history",
            "title": "Color por Cuartel",
            "group": "Análisis histórico",
            "category": "historical",
            "src": controlbins_view("field-history.png"),
            "description": "Herramienta analítica de alto impacto que combina el estado de color actual del cuartel, promedio de semilla, una línea de tiempo horizontal interactiva y un calendario mensual de mapa de calor de evolución diaria.",
            "flow": ["Semillas / Históricos", "Color por Cuartel"],
            "next": "not-found",
            "next_label": "Ver Manejo 404 (secundario) →",
            "badge": "Mapa analítico & Calendario",
            "highlights": [
                "Semáforo de calidad actual por cuartel y especie",
                "Línea de tiempo horizontal con porcentaje de semilla por fecha",
                "Calendario interactivo estilo mapa de calor por día",
            ],
        },
        {
            "id": "not-found",
            "title": "Página no encontrada",
            "group": "Manejo de error",
            "category": "secondary",
            "secondary": True,
            "src": controlbins_view("not-found.png"),
            "description": "Evidencia secundaria que demuestra consistencia en la experiencia de usuario y manejo corporativo de errores de navegación (404) dentro de la plataforma.",
            "flow": ["Navegación", "404 Error amigable"],
            "prev": "dashboard",
            "prev_label": "← Volver al Panel principal",
            "badge": "Navegación & UX",
            "highlights": [
                "Manejo de rutas inválidas amigable para el usuario",
                "Acciones rápidas para regresar al panel principal",
                "Mantiene coherencia gráfica con el sistema",
            ],
        },
    ]

    context = {
        "title": "ControlBins · Caso de Estudio Interactivo",
        "system_name": "ControlBins",
        "tagline": "Sistema de Trazabilidad y Gestión Operacional",
        "stack": "Python · Django · REST API · SQL Server · Kotlin · Anime.js",
        "confidentiality_note": "Evidencia visual autorizada mediante capturas del sistema. Por políticas de confidencialidad de la organización, el código fuente, modelos y endpoints internos permanecen estrictamente privados.",
        "screens": screens,
        "screens_json": json.dumps(screens, ensure_ascii=False),
    }
    return TemplateResponse(request, "templatesapp/controlbins_viewer.html", context)
