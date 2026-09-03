from django.shortcuts import render
from urllib.parse import quote_plus
import json


def index(request):
	"""Render the portfolio / enhanced CV page using user's LinkedIn/CV data."""
	linkedin_url = 'https://linkedin.com/in/sebastian-espindola-46a521334'
	# Use an external QR generator (public) to show a QR code for the LinkedIn profile
	linkedin_qr = f'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={quote_plus(linkedin_url)}'

	context = {
		'name': 'Sebastián Espíndola',
		'title': 'Ingeniero en Informática',
		'summary': (
			'Desarrollé un sistema completo de trazabilidad (backend Django + app móvil Kotlin) '
			'que digitalizó el 100% del control de bins de una empresa exportadora. Combino desarrollo '
			'backend con soporte técnico integral, resolviendo problemas de principio a fin.'
		),
		'contact': {
			'email': 'seba501090@gmail.com',
			'phone': '+56 9 5380 4158',
			'location': 'Vicuña, Coquimbo, Chile',
			'linkedin': linkedin_url,
			'linkedin_qr': linkedin_qr,
		},
		'experience': [
			{
				'title': 'Asistente de Informática (Desarrollo de Software)',
				'company': 'Frutícola y Exportadora Atacama Ltda',
				'dates': 'Dic 2023 – Jul 2025',
				'location': 'Vicuña, Chile',
				'type': 'Presencial, trabajo de temporada',
				'bullets': [
					'Diseñé y desarrollé una aplicación móvil (Kotlin, Android Studio) y backend (Django + SQL Server) para el control y trazabilidad del 100% de los bins de la operación.',
					'Construí una API REST (Django REST Framework) con sincronización cada 30 segundos, reconexión automática y modo offline con SQLite; implementé validación de duplicados.',
					'Colaboré en el diseño del modelo de base de datos y generé reportes mediante consultas SQL exportados a Excel.',
					'Implementé control de acceso por roles, notificaciones internas ante fallos de sincronización y respaldos semanales automatizados.',
					'Automaticé estadísticas y diseñé una arquitectura modular con dashboard preparada para escalar hasta 100 usuarios concurrentes.',
					'Utilicé Git/GitHub y Postman; lideré el proyecto desde piloto hasta producción.'
				]
			}
		],
		'education': {
			'degree': 'Ingeniería en Informática',
			'institution': 'INACAP, Sede La Serena',
			'graduation': 'Abril 2025'
		},
		'skills': [
			'Python', 'Django', 'Django REST Framework', 'SQL Server', 'Git / GitHub',
			'Kotlin', 'Android Studio', 'Postman', 'SQLite', 'Automatización',
			'Power BI', 'ETL', 'Excel avanzado', 'Mantenimiento HW', 'Redes (CCNA)'
		],
		'certificates': [
			'Certificado de Desarrollador Full Stack (162 hrs.) — INACAP',
			'Certificado en Soporte Computacional (126 hrs.) — INACAP',
			'Certificado en Arquitectura Cloud (198 hrs.) — INACAP',
			'CCNA: Introduction to Networks — Cisco Networking Academy',
			'Google AI Essentials (5 cursos) — Google / Coursera'
		],
		'languages': [
			{'name': 'Español', 'level': 'Nativo'},
			{'name': 'Inglés', 'level': 'Intermedio'}
		]
	}


	# Define interactive bubbles for the universe view
	bubbles = [
		{
			'id': 'profile',
			'label': 'Perfil',
			'color': '#7c3aed',
			'icon': '👤',
			'type': 'center',
			'content': context['summary'],
			'photo': '/static/portafoliosapp/img/profile.jpg',
			'name': context['name'],
			'title': context['title']
		},
		{
			'id': 'tech',
			'label': 'Habilidades técnicas',
			'color': '#06b6d4',
			'icon': '💻',
			'children': [
				{'label': 'Backend', 'text': 'Django, Django REST Framework, Python'},
				{'label': 'Móvil', 'text': 'Kotlin, Android Studio, Room, Retrofit'},
				{'label': 'Bases de datos', 'text': 'SQL Server, SQLite'},
				{'label': 'IA', 'text': 'Ollama, LangChain, FAISS, RAG'}
			]
		},
		{
			'id': 'soft',
			'label': 'Habilidades personales',
			'color': '#f472b6',
			'icon': '🧭',
			'children': [
				{'label': 'Comunicación', 'text': 'Coordinación con jefaturas y equipos'},
				{'label': 'Liderazgo', 'text': 'Lideré proyecto piloto a producción'},
			]
		},
		{
			'id': 'projects',
			'label': 'Proyectos',
			'color': '#06b6d4',
			'icon': '🚀',
			'children': [
				{'label': 'ControlBins', 'text': 'App Android offline-first + backend Django. Gestión de bins y sincronización.'},
				{'label': 'Asistente IA', 'text': 'Integración local con modelos, RAG y memoria a largo plazo.'}
			]
		},
		{
			'id': 'experience',
			'label': 'Experiencia',
			'color': '#8b5cf6',
			'icon': '📁',
			'content': 'Asistente de Informática — Frutícola y Exportadora Atacama Ltda (Dic 2023 – Jul 2025)'
		},
		{
			'id': 'education',
			'label': 'Estudios',
			'color': '#60a5fa',
			'icon': '🎓',
			'content': 'Ingeniería en Informática — INACAP (Abril 2025)'
		},
		{
			'id': 'contact',
			'label': 'Contacto',
			'color': '#fb7185',
			'icon': '✉️',
			'content': f"Email: {context['contact']['email']} — Tel: {context['contact']['phone']}"
		}
	]

	context['bubbles_json'] = json.dumps(bubbles)

	return render(request, 'templatesapp/index.html', context)
