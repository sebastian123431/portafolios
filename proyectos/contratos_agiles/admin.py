from django.contrib import admin

# Register your models here.
from .models import Cargo, Contrato, ContratoTrabajador, Login, antecedentes, trabajadores

admin.site.register(trabajadores)
admin.site.register(Cargo)
admin.site.register(antecedentes)
admin.site.register(Contrato)
admin.site.register(ContratoTrabajador)
admin.site.register(Login)
