from django.urls import path

from . import views

app_name = "contratos_agiles"

urlpatterns = [
    path("", views.login, name="login"),
    path("registro/", views.register, name="register"),
    path("menu/", views.menu, name="menu"),
    path("reportes/", views.reportes, name="reportes"),
    path(
        "registrar_trabajador/", views.registrar_trabajador, name="registrar_trabajador"
    ),
    path("guardar_trabajador/", views.guardar_trabajador, name="guardar_trabajador"),
    path(
        "visualizar_trabajadores/",
        views.visualizar_trabajadores,
        name="visualizar_trabajadores",
    ),
    path("buscar_trabajadores/", views.buscar_trabajadores, name="buscar_trabajadores"),
    path(
        "exportar_trabajadores/",
        views.exportar_trabajadores,
        name="exportar_trabajadores",
    ),
    path("menu_trabajadores/", views.menu_trabajadores, name="menu_trabajadores"),
    path(
        "gestion_trabajadores/", views.gestion_trabajadores, name="gestion_trabajadores"
    ),
    path(
        "cambiar_vigencia/<int:trabajador_id>/",
        views.cambiar_vigencia,
        name="cambiar_vigencia",
    ),
    path("lista_trabajadores/", views.lista_trabajadores, name="lista_trabajadores"),
    path(
        "perfil_trabajador/<int:trabajador_id>/",
        views.perfil_trabajador,
        name="perfil_trabajador",
    ),
    path("editar_perfil/<int:id>/", views.editar_perfil, name="editar_perfil"),
    path("asignar_cargo/<int:id>/", views.asignar_cargo, name="asignar_cargo"),
    path("menu_contratos/", views.menu_contratos, name="menu_contratos"),
    path("subir_contrato/", views.subir_contrato, name="subir_contrato"),
    path("listar_contratos/", views.listar_contratos, name="listar_contratos"),
    path(
        "seleccionar_contrato/", views.seleccionar_contrato, name="seleccionar_contrato"
    ),
    path("generar_contrato/", views.generar_contrato, name="generar_contrato"),
    path(
        "generar_contrato_especifico/<int:trabajador_id>/",
        views.generar_contrato_especifico,
        name="generar_contrato_especifico",
    ),
    path(
        "generar_contratos_masivos/",
        views.generar_contratos_masivos,
        name="generar_contratos_masivos",
    ),
    path(
        "visualizar_contrato/<int:contrato_id>/",
        views.visualizar_contrato,
        name="visualizar_contrato",
    ),
    path(
        "previsualizar_contrato/",
        views.importar_y_previsualizar_contrato,
        name="previsualizar_contrato",
    ),
    path(
        "previsualizar_contrato/<str:archivo>/",
        views.previsualizar_contrato,
        name="previsualizar_archivo_contrato",
    ),
    path("guardar_contrato/", views.guardar_contrato, name="guardar_contrato"),
    path("editar_contrato/", views.editar_contrato, name="editar_contrato"),
    path(
        "extender_vigencia/<int:trabajador_id>/",
        views.extender_vigencia,
        name="extender_vigencia",
    ),
    path(
        "importar_trabajadores/",
        views.importar_trabajadores,
        name="importar_trabajadores",
    ),
    path("procesar_datos/", views.procesar_datos, name="procesar_datos"),
    path(
        "registrar_asistencia/", views.registrar_asistencia, name="registrar_asistencia"
    ),
    path(
        "registrar_asistencia_por_imagen/",
        views.registrar_asistencia_por_imagen,
        name="registrar_asistencia_por_imagen",
    ),
    path(
        "listar_asistencia_trabajadores_registrados/",
        views.listar_asistencia_trabajadores_registrados,
        name="listar_asistencia_trabajadores_registrados",
    ),
    path("ver_asistencia/", views.ver_asistencia, name="ver_asistencia"),
    path(
        "autocomplete/",
        views.autocomplete_trabajadores,
        name="autocomplete_trabajadores",
    ),
    path("upload_image/", views.upload_image, name="upload_image"),
    path(
        "enviar_correos_masivos/",
        views.enviar_correos_masivos,
        name="enviar_correos_masivos",
    ),
    path("enviar_correos/", views.enviar_correos, name="enviar_correos"),
]

