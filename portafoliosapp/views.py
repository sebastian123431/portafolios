from django.shortcuts import render


def index(request):
	"""Render the enhanced CV / portfolio homepage."""
	context = {
		'name': 'Tu Nombre',
		'role': 'Desarrollador / Diseñador',
		'intro': 'Resumen breve sobre ti: experiencia, intereses y objetivo profesional.',
		'skills': ['Python', 'Django', 'JavaScript', 'HTML', 'CSS', 'Anime.js'],
		'contact': {
			'email': 'tu@correo.com',
			'location': 'Ciudad, País'
		}
	}
	return render(request, 'templatesapp/index.html', context)
