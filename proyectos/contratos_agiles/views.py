import base64
import io
import os
import shutil
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.db.models import Count
from django.db.models.functions import ExtractYear
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now
from fuzzywuzzy import process

from .email_utils import send_contract_email
from .services.documents import (
    generate_contract_files,
    preview_uploaded_document,
    save_preview_document,
)
from .services.availability import EmailUnavailable, handle_service_errors
from .forms import (
    CargoForm,
    ContratoForm,
    ContratoTrabajadorForm,
    TrabajadorForm,
    UploadFileForm,
)
from .models import (
    ArchivoContrato,
    Asistencia,
    Cargo,
    Contrato,
    ContratoTrabajador,
    Login,
    trabajadores,
)


DEMO_ACCESS = {
    "username": "visitante",
    "password": "portafolio2026",
}


def ensure_demo_login():
    Login.objects.update_or_create(
        username=DEMO_ACCESS["username"],
        defaults={"password": DEMO_ACCESS["password"]},
    )


def reportes(request):
    previcion_salud_data = list(
        trabajadores.objects.values("previcion_salud").annotate(count=Count("id")).order_by("previcion_salud")
    )
    afp_data = list(trabajadores.objects.values("afp").annotate(count=Count("id")).order_by("afp"))
    nacimiento_data = [
        {"year": str(row["year"]) if row["year"] is not None else None, "count": row["count"]}
        for row in trabajadores.objects.annotate(year=ExtractYear("fecha_nacimiento"))
        .values("year").annotate(count=Count("id")).order_by("year")
    ]

    context = {
        "previcion_salud_data": previcion_salud_data,
        "afp_data": afp_data,
        "nacimiento_data": nacimiento_data,
    }
    return render(request, "contratos_agiles/reportes.html", context)


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Verificar si el usuario ya existe
        if Login.objects.filter(username=username).exists():
            return JsonResponse(
                {"status": "error", "message": "Este nombre de usuario ya está en uso"}
            )

        # Guardar el nuevo usuario en la base de datos
        new_user = Login(username=username, password=password)
        new_user.save()

        return JsonResponse(
            {"status": "success", "message": "Usuario registrado exitosamente"}
        )

    # Si el método es GET, muestra el formulario de registro
    return render(request, "contratos_agiles/registro.html")


def login(request):
    ensure_demo_login()

    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        username = request.POST.get("username")
        password = request.POST.get("password")


        try:
            Login.objects.get(username=username, password=password)
            if (
                username == "asistencia" and password == "asistencia"
            ):  # Verifica si el usuario y la contraseña son 'asistencia'
                return JsonResponse(
                    {"status": "success", "redirect_url": reverse("contratos_agiles:registrar_asistencia")}
                )
            else:
                return JsonResponse({"status": "success", "redirect_url": reverse("contratos_agiles:menu")})

        except Login.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Usuario o contraseña incorrectos"}
            )

    return render(request, "contratos_agiles/inicio.html", {"demo_access": DEMO_ACCESS})


def menu(request):
    # Consultar la cantidad de días presentes para cada trabajador
    presentes_datos = (
        Asistencia.objects.filter(presente=True)
        .values("trabajador__nombre", "trabajador__apellido")
        .annotate(presente=Count("id"))
    )

    # Consultar la cantidad de días ausentes para cada trabajador
    ausentes_datos = (
        Asistencia.objects.filter(presente=False)
        .values("trabajador__nombre", "trabajador__apellido")
        .annotate(ausente=Count("id"))
    )

    # Crear un diccionario para combinar los datos de presentes y ausentes por trabajador
    asistencia_datos = {}
    for dato in presentes_datos:
        nombre_completo = f"{dato['trabajador__nombre']} {dato['trabajador__apellido']}"
        asistencia_datos[nombre_completo] = {"presente": dato["presente"], "ausente": 0}

    for dato in ausentes_datos:
        nombre_completo = f"{dato['trabajador__nombre']} {dato['trabajador__apellido']}"
        if nombre_completo in asistencia_datos:
            asistencia_datos[nombre_completo]["ausente"] = dato["ausente"]
        else:
            asistencia_datos[nombre_completo] = {
                "presente": 0,
                "ausente": dato["ausente"],
            }

    # Convertir los datos en listas para pasar a Chart.js
    nombres = list(asistencia_datos.keys())
    presentes = [asistencia_datos[nombre]["presente"] for nombre in nombres]
    ausentes = [asistencia_datos[nombre]["ausente"] for nombre in nombres]

    # Obtener los contratos que están a punto de vencer (por ejemplo, en los próximos 30 días)
    fecha_limite = date.today() + timedelta(days=30)
    contratos_vencimiento = ContratoTrabajador.objects.filter(
        fecha_termino__lte=fecha_limite, fecha_termino__gte=date.today()
    )

    return render(
        request,
        "contratos_agiles/menu.html",
        {
            "nombres": nombres,
            "presentes": presentes,
            "ausentes": ausentes,
            "contratos_vencimiento": contratos_vencimiento,
        },
    )


def registrar_trabajador(request):
    return render(request, "contratos_agiles/registrar_trabajadores.html")


def menu_trabajadores(request):
    return render(request, "contratos_agiles/menu_trabajadores.html")


def menu_contratos(request):
    return render(request, "contratos_agiles/menu_contratos.html")


def guardar_trabajador(request):
    if request.method == "POST":
        try:
            # Captura de los datos del formulario
            nombre = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            rut = request.POST.get("rut")
            direccion = request.POST.get("direccion")
            telefono = request.POST.get("telefono")
            cargo = request.POST.get("cargo")
            afp = request.POST.get("afp")
            estado_civil = request.POST.get("estado_civil")
            previcion_salud = request.POST.get("prevision_salud")
            fecha_nacimiento = request.POST.get("fecha_nacimiento")
            correo = request.POST.get("correo")

            # Procesar la imagen si se subió
            foto = request.FILES.get("foto")

            # Crear un nuevo trabajador con los datos capturados
            trabajador = trabajadores(
                nombre=nombre,
                apellido=apellido,
                rut=rut,
                direccion=direccion,
                telefono=telefono,
                afp=afp,
                estado_civil=estado_civil,
                previcion_salud=previcion_salud,
                fecha_nacimiento=fecha_nacimiento,
                correo=correo,
                foto=foto,
            )

            # Guardar el trabajador en la base de datos
            trabajador.save()
            if cargo:
                Cargo.objects.create(
                    trabajadores=trabajador,
                    labor=cargo,
                    fecha_ingreso=date.today(),
                    sueldo=0,
                )

            # Redirigir al menú después de guardar exitosamente
            return redirect("contratos_agiles:menu")

        except KeyError:
            return HttpResponseBadRequest("Faltan datos en la solicitud", status=401)
        except Exception as e:
            return HttpResponseServerError(
                f"Error al guardar el trabajador: {str(e)}", status=500
            )
    else:
        return HttpResponseBadRequest("Método no permitido", status=401)


@handle_service_errors
def importar_y_previsualizar_contrato(request):
    if request.method == "POST" and request.FILES.get("contrato"):
        context = preview_uploaded_document(request.FILES["contrato"])
        return render(request, "contratos_agiles/previsualizar_contrato.html", context)
    return render(request, "contratos_agiles/subir_contrato.html")



def visualizar_trabajadores(request):
    # Obtener todos los trabajadores de la base de datos
    trabajadores_list = trabajadores.objects.all()

    # Pasar los trabajadores a la plantilla
    return render(
        request,
        "contratos_agiles/visualizar_trabajadores.html",
        {"trabajadores": trabajadores_list},
    )


def legacy_guardar_contrato_con_contenido(request):
    return HttpResponseBadRequest(
        "Esta ruta legacy ya no se usa. Usa subir_contrato o generar_contrato."
    )


def editar_contrato(request):
    if request.method == "POST":
        return redirect("contratos_agiles:subir_contrato")

    return redirect("contratos_agiles:subir_contrato")


def upload_image(request):
    if request.method == "POST" and request.FILES.get("upload"):
        image = request.FILES["upload"]

        # Guardar la imagen en el sistema de archivos de Django (carpeta media)
        save_path = default_storage.save(
            f"contratos_agiles/images/{image.name}", ContentFile(image.read())
        )
        image_url = default_storage.url(save_path)

        # Responder con la URL de la imagen para que CKEditor pueda mostrarla
        return JsonResponse({"uploaded": True, "url": image_url})

    return JsonResponse({"uploaded": False, "error": {"message": "Upload failed"}})


def previsualizar_contrato(request, archivo):
    # Detectar la extensión del archivo (PDF o DOCX)
    extension = archivo.split(".")[-1].lower()
    # Ruta completa del archivo en el directorio de medios
    contrato_url = default_storage.url(f"contratos/{archivo}")
    # Pasar la URL del archivo y la extensión al template
    return render(
        request,
        "contratos_agiles/previsualizar_contrato.html",
        {"contrato_url": contrato_url, "extension": extension},
    )

    # Vista para subir y previsualizar contratos


@handle_service_errors
def guardar_contrato(request):
    file_path = request.GET.get("file_path")
    if not file_path:
        return HttpResponseBadRequest("Falta file_path para guardar el contrato.")
    try:
        save_preview_document(file_path)
    except FileNotFoundError:
        return HttpResponse("El archivo no existe.", status=404)
    return render(
        request, "contratos_agiles/previsualizar_contrato.html",
        {"mensaje": "Contrato guardado exitosamente."},
    )



def seleccionar_contrato(request):
    # Obtener todos los trabajadores y contratos de la base de datos
    trabajadores_list = trabajadores.objects.all()
    contratos_list = Contrato.objects.all()  # Nombre correcto del modelo

    # Pasar los datos al contexto de la plantilla
    return render(
        request,
        "contratos_agiles/seleccionar_contrato.html",
        {"trabajadores": trabajadores_list, "contratos": contratos_list},
    )


@handle_service_errors
def generar_contrato(request):
    if request.method == "POST":
        trabajador_id = request.POST.get("trabajador")
        contrato_id = request.POST.get("contrato")

        # Verificar si el trabajador y contrato existen
        trabajador = get_object_or_404(trabajadores, id=trabajador_id)
        contrato = get_object_or_404(Contrato, id=contrato_id)

        # Obtener el cargo del trabajador
        cargo = Cargo.objects.filter(trabajadores=trabajador).first()
        if not cargo:
            return HttpResponse("El trabajador no tiene un cargo asignado", status=400)

        # Obtener la ruta completa del archivo de contrato
        contrato_path = contrato.archivo.path


        # Definir el contexto con datos del trabajador y su cargo
        contexto = {
            "nombre": trabajador.nombre,
            "apellido": trabajador.apellido,
            "rut": trabajador.rut,
            "direccion": trabajador.direccion,
            "telefono": trabajador.telefono,
            "cargo": cargo.labor,  # Usar el atributo correcto del cargo
            "afp": trabajador.afp,
            "estado_civil": trabajador.estado_civil,
            "previcion_salud": trabajador.previcion_salud,
            "fecha_nacimiento": trabajador.fecha_nacimiento.strftime("%d-%m-%Y"),
        }

        generated = generate_contract_files(
            contrato_path, contexto,
            f"contrato_{trabajador.nombre}_{trabajador.apellido}.docx",
        )
        pdf_output_path = generated.pdf_path

            # Guardar el contrato en la base de datos
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_termino = request.POST.get("fecha_termino")

        contrato_trabajador = ContratoTrabajador(
            trabajador=trabajador,
            ArchivoContrato=contrato,  # Asegúrate de que 'contrato' es una instancia de Contrato
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_termino,
        )
        contrato_trabajador.save()

        # Descargar el archivo PDF generado
        with open(pdf_output_path, "rb") as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="contrato_{trabajador.nombre}_{trabajador.apellido}.pdf"'
            )
            return response
    else:
        return HttpResponse("Método no permitido", status=405)


# metodo para subir contratos


def subir_contrato(request):
    if request.method == "POST":
        form = ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Guardar el contrato en la base de datos
            return redirect(
                "contratos_agiles:listar_contratos"
            )  # Redirigir a una página de listado después de subir
    else:
        form = ContratoForm()

    return render(request, "contratos_agiles/subir_contrato.html", {"form": form})


def listar_contratos(request):
    contratos = Contrato.objects.all()
    return render(
        request, "contratos_agiles/listar_contratos.html", {"contratos": contratos}
    )


# importar trabajadores en exel


def limpiar_datos(df):
    # Ejemplo de limpieza y formateo de datos
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Combina columnas si es necesario (ejemplo: nombre completo)
    if "nombre" in df.columns and "apellido" in df.columns:
        df["nombre_completo"] = df["nombre"] + " " + df["apellido"]

    # Convierte las fechas a un formato específico
    if "fecha_nacimiento" in df.columns:
        df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")
        df["fecha_nacimiento"] = df["fecha_nacimiento"].dt.strftime(
            "%Y-%m-%d"
        )  # Convertir a cadena de texto

    # Limpieza de la columna previcion_salud
    if "previcion_salud" in df.columns:
        df["previcion_salud"] = df["previcion_salud"].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    # Otros procesos de limpieza y formateo según sea necesario
    # ...

    return df


def procesar_datos(request):
    if "df" in request.session and "column_mapping" in request.session:
        df = pd.DataFrame(request.session["df"])
        column_mapping = request.session["column_mapping"]
        # Renombrar las columnas usando el mapeo seleccionado por el usuario
        df = df.rename(columns=column_mapping)
        # Limpiar y formatear los datos
        df = limpiar_datos(df)
        # Guardar los datos en la base de datos
        request.session["df"] = df.to_dict(orient="list")

        return redirect("contratos_agiles:importar_trabajadores")
    else:
        return redirect("contratos_agiles:importar_trabajadores")


def mapear_columnas_similares(df_columns, target_columns):
    mapping = {}
    for target in target_columns:
        match, score = process.extractOne(target, df_columns)
        if score >= 80:  # Ajusta el umbral según sea necesario
            mapping[target] = match
    return mapping


def importar_trabajadores(request):
    if request.method == "POST" and "file" in request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_path = fs.path(filename)
            if file.name.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            # Las fechas de Excel pueden ser Timestamp; la sesión utiliza JSON.
            request.session["df"] = df.astype(object).where(pd.notna(df), None).map(
                lambda value: value.isoformat() if isinstance(value, (date, datetime)) else value
            ).to_dict(orient="list")
            request.session["columns"] = list(df.columns)
            fs.delete(filename)
            target_columns = [
                "nombre",
                "apellido",
                "rut",
                "direccion",
                "telefono",
                "cargo",
                "afp",
                "estado_civil",
                "fecha_nacimiento",
                "previcion_salud",
                "correo",
            ]
            column_mapping = mapear_columnas_similares(df.columns, target_columns)
            return render(
                request,
                "contratos_agiles/mapeo_columnas.html",
                {"columns": df.columns, "form": form, "column_mapping": column_mapping},
            )
    elif request.method == "POST" and "guardar_mapeo" in request.POST:
        column_mapping = request.POST.dict()
        column_mapping.pop("csrfmiddlewaretoken")
        column_mapping.pop("guardar_mapeo")
        request.session["column_mapping"] = column_mapping
        return redirect("contratos_agiles:procesar_datos")
    elif request.method == "POST" and "guardar" in request.POST:
        df = pd.DataFrame(request.session.get("df"))
        for index, row in df.iterrows():
            trabajador = trabajadores.objects.create(
                nombre=row.get("nombre", ""),
                apellido=row.get("apellido", ""),
                rut=row.get("rut", ""),
                direccion=row.get("direccion", ""),
                telefono=row.get("telefono", ""),
                afp=row.get("afp", ""),
                estado_civil=row.get("estado_civil", ""),
                fecha_nacimiento=row.get("fecha_nacimiento", ""),
                previcion_salud=row.get("previcion_salud", ""),
                correo=row.get("correo", "") or "sin-correo@example.com",
            )
            cargo = row.get("cargo", "")
            if cargo:
                Cargo.objects.create(
                    trabajadores=trabajador,
                    labor=cargo,
                    fecha_ingreso=date.today(),
                    sueldo=0,
                )
        del request.session["df"]
        del request.session["column_mapping"]
        return redirect("contratos_agiles:visualizar_trabajadores")
    elif request.method == "POST" and "eliminar" in request.POST:
        index = int(request.POST["eliminar"])
        df = pd.DataFrame(request.session.get("df"))
        df = df.drop(index)
        request.session["df"] = df.to_dict(orient="list")
        return render(
            request,
            "contratos_agiles/importar_trabajadores.html",
            {"form": UploadFileForm(), "df": df.to_dict(orient="records")},
        )
    elif request.method == "POST" and "borrar_todo" in request.POST:
        if "df" in request.session:
            del request.session["df"]
        return redirect("contratos_agiles:importar_trabajadores")
    elif request.method == "POST" and "subir_nuevo" in request.POST:
        if "df" in request.session:
            del request.session["df"]
        return redirect("contratos_agiles:importar_trabajadores")
    else:
        form = UploadFileForm()
        df = request.session.get("df", None)
        if df:
            df = pd.DataFrame(df).to_dict(orient="records")
        return render(
            request, "contratos_agiles/importar_trabajadores.html", {"form": form, "df": df}
        )


def grafico_asistencia(request):
    return ver_asistencia(request)



def autocomplete_trabajadores(request):
    if "term" in request.GET:
        term = request.GET.get("term")
        trabajadores_filtrados = trabajadores.objects.filter(
            nombre__icontains=term
        ) | trabajadores.objects.filter(apellido__icontains=term)
        trabajadores_list = list(
            trabajadores_filtrados.values("id", "nombre", "apellido")
        )
        return JsonResponse(trabajadores_list, safe=False)
    return JsonResponse([], safe=False)


def perfil_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(trabajadores, id=trabajador_id)
    cargos = Cargo.objects.filter(trabajadores=trabajador)
    contratos = ContratoTrabajador.objects.filter(trabajador=trabajador)
    asistencias = Asistencia.objects.filter(trabajador=trabajador)

    trabajador_vigente = validar_vigencia_trabajador(trabajador)

    # Crear los formularios para cada cargo y contrato
    cargo_forms = [
        CargoForm(instance=cargo, prefix=f"cargo_{cargo.id}") for cargo in cargos
    ]
    contrato_forms = [
        ContratoTrabajadorForm(instance=contrato, prefix=f"contrato_{contrato.id}")
        for contrato in contratos
    ]

    if request.method == "POST":
        form = TrabajadorForm(request.POST, instance=trabajador)
        if form.is_valid():
            form.save()
            return redirect("contratos_agiles:perfil_trabajador", trabajador_id=trabajador.id)
    else:
        form = TrabajadorForm(instance=trabajador)

    context = {
        "trabajador": trabajador,
        "form": form,
        "cargos": cargos,
        "asistencias": asistencias,
        "contratos": contratos,
        "trabajador_vigente": trabajador_vigente,
        "cargo_forms": cargo_forms,  # Agregamos los formularios de cargos
        "contrato_forms": contrato_forms,  # Agregamos los formularios de contratos
    }

    return render(request, "contratos_agiles/perfil_trabajador.html", context)


def gestion_trabajadores(request):
    trabajadores_vigentes = trabajadores.objects.filter(
        cargo__vigente="Vigente"
    ).distinct()
    trabajadores_no_vigentes = trabajadores.objects.exclude(
        id__in=trabajadores_vigentes.values_list("id", flat=True)
    )
    return render(
        request,
        "contratos_agiles/gestion_trabajadores.html",
        {
            "trabajadores_vigentes": trabajadores_vigentes,
            "trabajadores_no_vigentes": trabajadores_no_vigentes,
        },
    )




def cambiar_vigencia(request, trabajador_id):
    trabajador = get_object_or_404(trabajadores, id=trabajador_id)
    cargos = Cargo.objects.filter(trabajadores=trabajador).order_by(
        "-fecha_ingreso", "-id"
    )

    if cargos.filter(vigente="Vigente").exists():
        cargos.filter(vigente="Vigente").update(vigente="No vigente")
    else:
        cargo_reciente = cargos.first()
        if cargo_reciente:
            cargo_reciente.vigente = "Vigente"
            cargo_reciente.save(update_fields=["vigente"])

    return redirect(reverse("contratos_agiles:gestion_trabajadores"))


def lista_trabajadores(request):
    lista_trabajadores = trabajadores.objects.all()
    return render(
        request,
        "contratos_agiles/listar_trabajadores.html",
        {"trabajadores": lista_trabajadores},
    )


@handle_service_errors
def generar_contrato_especifico(request, trabajador_id):
    trabajador = get_object_or_404(trabajadores, id=trabajador_id)

    # Verificar si el trabajador tiene un cargo asignado
    cargo = Cargo.objects.filter(trabajadores=trabajador).first()
    if not cargo:
        error_message = f"No se puede crear el contrato para {trabajador.nombre} {trabajador.apellido} porque no tiene un cargo asignado."
        return render(
            request,
            "contratos_agiles/generar_contratos_especifico.html",
            {
                "trabajador": trabajador,
                "trabajadores": trabajadores.objects.all(),
                "contratos": Contrato.objects.all(),
                "error_message": error_message,
            },
        )

    if request.method == "POST":
        contrato_id = request.POST.get("contrato")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_termino = request.POST.get("fecha_termino")

        # Verificar si el contrato existe
        contrato = get_object_or_404(Contrato, id=contrato_id)

        # Obtener la ruta completa del archivo de contrato
        contrato_path = contrato.archivo.path


        # Definir el contexto con datos del trabajador y su cargo
        contexto = {
            "nombre": trabajador.nombre,
            "apellido": trabajador.apellido,
            "rut": trabajador.rut,
            "direccion": trabajador.direccion,
            "telefono": trabajador.telefono,
            "cargo": cargo.labor,  # Usar el atributo correcto del cargo
            "afp": trabajador.afp,
            "estado_civil": trabajador.estado_civil,
            "previcion_salud": trabajador.previcion_salud,
            "fecha_nacimiento": trabajador.fecha_nacimiento.strftime("%d-%m-%Y"),
        }

        generated = generate_contract_files(
            contrato_path, contexto,
            f"contrato_{trabajador.nombre}_{trabajador.apellido}.docx",
        )
        pdf_output_path = generated.pdf_path

        # Guardar el contrato en la base de datos
        contrato_trabajador = ContratoTrabajador(
            trabajador=trabajador,
            ArchivoContrato=contrato,  # Asegúrate de que 'contrato' es una instancia de Contrato
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_termino,
        )
        contrato_trabajador.save()

        # Guardar el archivo PDF en la base de datos
        with open(pdf_output_path, "rb") as pdf_file:
            archivo_contrato = ArchivoContrato(
                contrato_trabajador=contrato_trabajador,
                archivo=ContentFile(
                    pdf_file.read(),
                    name=f"contrato_{trabajador.nombre}_{trabajador.apellido}.pdf",
                ),
            )
            archivo_contrato.save()

        # Descargar el archivo PDF generado
        with open(pdf_output_path, "rb") as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="contrato_{trabajador.nombre}_{trabajador.apellido}.pdf"'
            )
            return response
    else:
        # Manejar el método GET
        return render(
            request,
            "contratos_agiles/generar_contratos_especifico.html",
            {
                "trabajador": trabajador,
                "trabajadores": trabajadores.objects.all(),
                "contratos": Contrato.objects.all(),
            },
        )


def asignar_cargo(request, id):
    trabajador = get_object_or_404(trabajadores, id=id)
    if request.method == "POST":
        form = CargoForm(request.POST)
        if form.is_valid():
            cargo = form.save(commit=False)
            cargo.trabajadores = trabajador
            cargo.save()

            # Enviar correo de confirmación
            subject = "Asignación de Cargo"
            html_content = f"<p>Hola {trabajador.nombre},</p><p>Cargo '{cargo.labor}' asignado correctamente.</p><p>Saludos,</p><p>Fundo la Campana</p>"
            try:
                send_contract_email(
                    to_email=trabajador.correo, subject=subject, html_content=html_content
                )
            except EmailUnavailable as exc:
                messages.warning(request, f"Cargo guardado. {exc}")

            return redirect("contratos_agiles:perfil_trabajador", trabajador_id=trabajador.id)
    else:
        form = CargoForm()
    return render(
        request,
        "contratos_agiles/asignar_cargo.html",
        {"form": form, "trabajador": trabajador},
    )


def editar_perfil(request, id):
    trabajador = get_object_or_404(trabajadores, id=id)
    if request.method == "POST":
        form = TrabajadorForm(request.POST, instance=trabajador)
        if form.is_valid():
            form.save()
            return redirect("contratos_agiles:perfil_trabajador", trabajador_id=trabajador.id)
    else:
        form = TrabajadorForm(instance=trabajador)
    return render(
        request,
        "contratos_agiles/perfil_trabajador.html",
        {"form": form, "trabajador": trabajador},
    )


def validar_vigencia_trabajador(trabajador):
    cargos_vigentes = Cargo.objects.filter(
        trabajadores=trabajador,
        fecha_ingreso__lte=date.today(),
        vigente="Vigente",  # Verifica también el campo de vigencia
    )
    contratos_vigentes = ContratoTrabajador.objects.filter(
        trabajador=trabajador, fecha_termino__gte=date.today()
    )
    return cargos_vigentes.exists() and contratos_vigentes.exists()


def extender_vigencia(request, trabajador_id):
    trabajador = get_object_or_404(trabajadores, id=trabajador_id)

    if request.method == "POST":
        cargos = Cargo.objects.filter(trabajadores=trabajador)
        contratos = ContratoTrabajador.objects.filter(trabajador=trabajador)

        # Procesar formularios de cargos
        cargos_actualizados = True
        for cargo in cargos:
            form = CargoForm(request.POST, instance=cargo, prefix=f"cargo_{cargo.id}")
            if form.is_valid():
                form.save()
            else:
                cargos_actualizados = (
                    False  # Indica si hubo errores en algún formulario
                )

        # Procesar formularios de contratos
        contratos_actualizados = True
        for contrato in contratos:
            form = ContratoTrabajadorForm(
                request.POST, instance=contrato, prefix=f"contrato_{contrato.id}"
            )
            if form.is_valid():
                form.save()
            else:
                contratos_actualizados = False

        # Mensajes según el resultado de los formularios
        if cargos_actualizados and contratos_actualizados:
            messages.success(
                request, "Vigencia de los cargos y contratos actualizada correctamente."
            )
        else:
            messages.error(
                request,
                "Ocurrieron errores al actualizar algunos datos. Verifica los campos.",
            )

        return redirect("contratos_agiles:perfil_trabajador", trabajador_id=trabajador.id)

    else:
        # Crear formularios para los cargos y contratos
        cargo_forms = [
            CargoForm(instance=cargo, prefix=f"cargo_{cargo.id}")
            for cargo in Cargo.objects.filter(trabajadores=trabajador)
        ]
        contrato_forms = [
            ContratoTrabajadorForm(instance=contrato, prefix=f"contrato_{contrato.id}")
            for contrato in ContratoTrabajador.objects.filter(trabajador=trabajador)
        ]

        context = {
            "trabajador": trabajador,
            "cargo_forms": cargo_forms,
            "contrato_forms": contrato_forms,
        }
        return render(request, "contratos_agiles/perfil_trabajador.html", context)


def legacy_visualizar_contrato_datos(request, contrato_id):
    return visualizar_contrato(request, contrato_id)



@handle_service_errors
def generar_contratos_masivos(request):
    if request.method == "POST":

        trabajadores_ids = request.POST.getlist("trabajadores")
        contrato_id = request.POST.get("contrato")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_termino = request.POST.get("fecha_termino")

        contrato = get_object_or_404(Contrato, id=contrato_id)
        contrato_path = contrato.archivo.path

        trabajadores_sin_cargo = []  # Lista para almacenar trabajadores sin cargo

        # Verificar si todos los trabajadores tienen un cargo asignado
        for trabajador_id in trabajadores_ids:
            trabajador = get_object_or_404(trabajadores, id=trabajador_id)
            cargo = Cargo.objects.filter(trabajadores=trabajador).first()
            if not cargo:
                trabajadores_sin_cargo.append(
                    f"{trabajador.nombre} {trabajador.apellido}"
                )

        if trabajadores_sin_cargo:
            error_message = (
                "No se puede crear el contrato para los siguientes trabajadores porque no tienen un cargo asignado: "
                + ", ".join(trabajadores_sin_cargo)
            )
            return render(
                request,
                "contratos_agiles/generar_contratos_masivos.html",
                {
                    "trabajadores": trabajadores.objects.all(),
                    "contratos": Contrato.objects.all(),
                    "error_message": error_message,
                },
            )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for trabajador_id in trabajadores_ids:
                trabajador = get_object_or_404(trabajadores, id=trabajador_id)
                cargo = Cargo.objects.filter(trabajadores=trabajador).first()


                # Crear contexto con datos del trabajador y cargo
                contexto = {
                    "nombre": trabajador.nombre,
                    "apellido": trabajador.apellido,
                    "rut": trabajador.rut,
                    "direccion": trabajador.direccion,
                    "telefono": trabajador.telefono,
                    "afp": trabajador.afp,
                    "estado_civil": trabajador.estado_civil,
                    "previcion_salud": trabajador.previcion_salud,
                    "fecha_nacimiento": trabajador.fecha_nacimiento.strftime(
                        "%d-%m-%Y"
                    ),
                    "fecha_inicio": fecha_inicio,
                    "fecha_termino": fecha_termino,
                    "cargo_labor": cargo.labor if cargo else "N/A",
                    "cargo_fecha_ingreso": cargo.fecha_ingreso.strftime("%d-%m-%Y")
                    if cargo and cargo.fecha_ingreso
                    else "N/A",
                }

                generated = generate_contract_files(
                    contrato_path, contexto,
                    f"contrato_{trabajador.nombre}_{trabajador.apellido}.docx",
                )
                pdf_output_path = generated.pdf_path

                # Crear instancia de ContratoTrabajador si no existe
                contract_lookup = dict(
                    trabajador=trabajador,
                    ArchivoContrato=contrato,
                    fecha_inicio=datetime.strptime(fecha_inicio, "%Y-%m-%d"),
                    fecha_termino=datetime.strptime(fecha_termino, "%Y-%m-%d"),
                )
                # Puede haber varias generaciones individuales del mismo contrato.
                contrato_trabajador = ContratoTrabajador.objects.filter(
                    **contract_lookup
                ).order_by("pk").first()
                if contrato_trabajador is None:
                    contrato_trabajador = ContratoTrabajador.objects.create(**contract_lookup)

                # Guardar el archivo PDF en la base de datos
                with open(pdf_output_path, "rb") as pdf_file:
                    archivo_contrato = ArchivoContrato(
                        contrato_trabajador=contrato_trabajador,
                        archivo=ContentFile(
                            pdf_file.read(),
                            name=f"contrato_{trabajador.nombre}_{trabajador.apellido}.pdf",
                        ),
                    )
                    archivo_contrato.save()

                    # Añadir el PDF al archivo ZIP
                    zip_file.write(pdf_output_path, os.path.basename(pdf_output_path))

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=contratos_generados.zip"
        limpiar_tmp()

        return response

    return render(
        request,
        "contratos_agiles/generar_contratos_masivos.html",
        {
            "trabajadores": trabajadores.objects.all(),
            "contratos": Contrato.objects.all(),
        },
    )

FACE_SIZE = (160, 160)
LBPH_CONFIDENCE_LIMIT = 110.0
FACE_CASCADE = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
PROFILE_FACE_CASCADE = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_profileface.xml"))


def detectar_rostros(gray_image):
    if gray_image is None or gray_image.size == 0 or FACE_CASCADE.empty():
        return []

    rostros = FACE_CASCADE.detectMultiScale(
        gray_image,
        scaleFactor=1.05,
        minNeighbors=4,
        minSize=(70, 70),
    )
    if len(rostros) == 0 and not PROFILE_FACE_CASCADE.empty():
        rostros = PROFILE_FACE_CASCADE.detectMultiScale(
            gray_image,
            scaleFactor=1.05,
            minNeighbors=4,
            minSize=(70, 70),
        )
    return sorted(rostros, key=lambda rostro: rostro[2] * rostro[3], reverse=True)


def normalizar_imagen_rostro(image, recorte_fallback=True):
    if image is None or image.size == 0:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    gray = cv2.equalizeHist(gray)
    rostros = detectar_rostros(gray)

    if len(rostros) > 0:
        x, y, w, h = rostros[0]
        margen = int(max(w, h) * 0.18)
        x1 = max(x - margen, 0)
        y1 = max(y - margen, 0)
        x2 = min(x + w + margen, gray.shape[1])
        y2 = min(y + h + margen, gray.shape[0])
        gray = gray[y1:y2, x1:x2]
    elif not recorte_fallback:
        return None
    else:
        alto, ancho = gray.shape[:2]
        lado = min(ancho, alto)
        x1 = max((ancho - lado) // 2, 0)
        y1 = max((alto - lado) // 3, 0)
        gray = gray[y1 : y1 + lado, x1 : x1 + lado]

    if gray.size == 0:
        return None

    rostro = cv2.resize(gray, FACE_SIZE)
    return cv2.equalizeHist(rostro)


def cargar_rostros_entrenamiento():
    rostros = []
    etiquetas = []
    trabajadores_por_id = {}

    extensiones_validas = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for trabajador in trabajadores.objects.exclude(foto=""):
        if not trabajador.foto:
            continue

        try:
            ruta_foto = Path(trabajador.foto.path)
        except ValueError:
            continue

        if not ruta_foto.exists() or ruta_foto.suffix.lower() not in extensiones_validas:
            continue

        imagen_referencia = cv2.imread(str(ruta_foto))
        rostro_referencia = normalizar_imagen_rostro(imagen_referencia, recorte_fallback=False)
        if rostro_referencia is None:
            continue

        rostros.append(rostro_referencia)
        etiquetas.append(trabajador.id)
        trabajadores_por_id[trabajador.id] = trabajador

    return rostros, np.array(etiquetas, dtype=np.int32), trabajadores_por_id


def identificar_trabajador(face_image):
    if not hasattr(cv2, "face"):
        return None, "OpenCV contrib no esta instalado; falta el modulo cv2.face."

    rostro_captura = normalizar_imagen_rostro(face_image, recorte_fallback=False)
    if rostro_captura is None:
        return None, "No se detecto ningun rostro claro en la imagen."

    rostros, etiquetas, trabajadores_por_id = cargar_rostros_entrenamiento()
    if len(rostros) == 0:
        return None, "No hay fotos validas de trabajadores para comparar."

    reconocedor = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8, grid_x=8, grid_y=8)
    reconocedor.train(rostros, etiquetas)
    etiqueta, confianza = reconocedor.predict(rostro_captura)

    if confianza <= LBPH_CONFIDENCE_LIMIT and int(etiqueta) in trabajadores_por_id:
        return int(etiqueta), None

    return None, f"No se pudo identificar con suficiente confianza. Mejor coincidencia: {confianza:.2f}."





def registrar_asistencia_por_imagen(request):
    if request.method == "POST":
        try:
            # Obtiene la imagen en base64 desde el cliente
            image_data = request.POST.get("image")
            if not image_data or ";base64," not in image_data:
                return JsonResponse(
                    {"status": "error", "message": "No se recibio una imagen valida"}
                )

            _, imgstr = image_data.split(";base64,", 1)
            frame = np.frombuffer(base64.b64decode(imgstr), np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            if frame is None:
                return JsonResponse(
                    {"status": "error", "message": "No se pudo leer la imagen"}
                )

            trabajador_id, error_identificacion = identificar_trabajador(frame)
            if trabajador_id:
                trabajador = trabajadores.objects.get(id=trabajador_id)
                asistencia = Asistencia(
                    trabajador=trabajador, fecha=now().date(), presente=True
                )
                if asistencia.trabajador_vigente():
                    Asistencia.objects.get_or_create(
                        trabajador=trabajador,
                        fecha=now().date(),
                        defaults={"presente": True},
                    )
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": f"Asistencia registrada: {trabajador.nombre} {trabajador.apellido}",
                        }
                    )
                else:
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": f"Rostro reconocido: {trabajador.nombre} {trabajador.apellido}, pero el trabajador no esta vigente.",
                        }
                    )
            return JsonResponse(
                {
                    "status": "error",
                    "message": error_identificacion or "No se pudo identificar",
                }
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Método no permitido"})


def registrar_asistencia(request):
    if request.method == "POST":
        # Aquí deberías procesar la imagen y reconocer al trabajador
        # Por simplicidad, asumiremos que se ha reconocido al trabajador con ID 1
        trabajador_id = 1
        trabajador = trabajadores.objects.get(id=trabajador_id)

        # Registrar la asistencia del dia sin duplicar al mismo trabajador
        Asistencia.objects.get_or_create(
            trabajador=trabajador,
            fecha=date.today(),
            defaults={"presente": True},
        )

        return JsonResponse(
            {
                "status": "success",
                "message": f"Asistencia registrada. Bienvenido {trabajador.nombre}",
            }
        )

    trabajadores_presentes = trabajadores.objects.filter(
        asistencia__presente=True
    ).distinct()
    return render(
        request,
        "contratos_agiles/registrar_asistencia.html",
        {"trabajadores_presentes": trabajadores_presentes},
    )


def limpiar_tmp():
    tmp_dir = Path(settings.MEDIA_ROOT) / "tmp"
    if not tmp_dir.exists():
        return
    for filename in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"No se pudo eliminar {file_path}. Razón: {e}")


def visualizar_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    # Asegurar que el archivo existe y es accesible
    if not contrato.archivo or not os.path.exists(contrato.archivo.path):
        return HttpResponse("El archivo no está disponible.", status=404)

    context = {
        "nombre": contrato.nombre,
        "descripcion": contrato.descripcion,
        "contrato_url": request.build_absolute_uri(contrato.archivo.url),
    }
    return render(request, "contratos_agiles/ver_contrato.html", context)


def exportar_trabajadores(request):
    columns = ["id", "nombre", "apellido", "rut", "direccion", "telefono", "afp", "estado_civil", "fecha_nacimiento", "previcion_salud"]
    rows = trabajadores.objects.order_by("id").values_list(*columns)

    df = pd.DataFrame(rows, columns=columns)
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=trabajadores.xlsx"
    df.to_excel(response, index=False, engine="openpyxl")

    return response


def buscar_trabajadores(request):
    if request.method == "GET":
        query = request.GET.get("q", "")
        if query:  # Si hay una búsqueda
            matches = (
                trabajadores.objects.filter(nombre__icontains=query)
                | trabajadores.objects.filter(apellido__icontains=query)
                | trabajadores.objects.filter(rut__icontains=query)
            )
        else:  # Si no hay búsqueda, mostrar todos los trabajadores
            matches = trabajadores.objects.all()

        trabajadores_list = list(
            matches.values(
                "id",
                "nombre",
                "apellido",
                "rut",
                "direccion",
                "telefono",
                "afp",
                "estado_civil",
                "fecha_nacimiento",
                "previcion_salud",
                "correo",
            )
        )
        for trabajador in trabajadores_list:
            trabajador["perfil_url"] = reverse("contratos_agiles:perfil_trabajador", args=[trabajador["id"]])
            trabajador["cargo_url"] = reverse("contratos_agiles:asignar_cargo", args=[trabajador["id"]])
        return JsonResponse({"trabajadores": trabajadores_list}, safe=False)
    return JsonResponse({"trabajadores": []})


def listar_asistencia_trabajadores_registrados(request):
    trabajadores_presentes = trabajadores.objects.filter(
        asistencia__presente=True
    ).distinct()
    return render(
        request,
        "contratos_agiles/lista_asistencia_trabajadores_registrados.html",
        {"trabajadores_presentes": trabajadores_presentes},
    )


def ver_asistencia(request):
    # Obtener la fecha seleccionada del formulario, por defecto la fecha actual
    fecha_seleccionada = request.GET.get("date", date.today())

    # Filtrar las asistencias para la fecha seleccionada donde los trabajadores están presentes
    asistencias_presentes = Asistencia.objects.filter(
        fecha=fecha_seleccionada, presente=True
    ).select_related("trabajador")

    # Obtener los trabajadores que están presentes ese día
    trabajadores_presentes = [
        asistencia.trabajador for asistencia in asistencias_presentes
    ]

    # Datos para el dashboard: totales de asistencia por trabajador
    resumen = {}
    asistencias = Asistencia.objects.select_related("trabajador").order_by(
        "trabajador__apellido",
        "trabajador__nombre",
    )
    for asistencia in asistencias:
        nombre = f"{asistencia.trabajador.nombre} {asistencia.trabajador.apellido}"
        if nombre not in resumen:
            resumen[nombre] = {"presente": 0, "ausente": 0}
        if asistencia.presente:
            resumen[nombre]["presente"] += 1
        else:
            resumen[nombre]["ausente"] += 1

    # Preparar los datos en listas para ser usados en gráficos
    nombres = list(resumen.keys())
    total_presentes = [dato["presente"] for dato in resumen.values()]
    total_ausentes = [dato["ausente"] for dato in resumen.values()]

    # Contexto para pasar a la plantilla HTML
    contexto = {
        "trabajadores_presentes": trabajadores_presentes,
        "fecha_seleccionada": fecha_seleccionada,
        "nombres": nombres,
        "total_presentes": total_presentes,
        "total_ausentes": total_ausentes,
    }

    return render(request, "contratos_agiles/ver_asistencia.html", contexto)


@handle_service_errors
def legacy_enviar_correos_reingreso(request):
    if request.method == "POST":
        estado = request.POST.get("estado")
        if estado == "no_vigente":
            trabajadores_lista = trabajadores.objects.filter(
                cargo__vigente="No vigente"
            ).distinct()
            for trabajador in trabajadores_lista:
                subject = f"Hola {trabajador.nombre}, tienes un nuevo mensaje"
                mensaje = f"Estamos agradecidos de que hayas formado parte de nuestra familia Fundo la Campana. <p></p> Es por eso que queremos invitarte a ser parte de nuestro equipo otra vez.<p></p> Por favor comunicate con nosotros a traves del numero {settings.CONTRATOS_CONTACT_PHONE}."
                html_content = f"<p>Hola {trabajador.nombre},</p><p>{mensaje}</p><p>Saludos,</p><p>Fundo la Campana</p>"
                send_contract_email(
                    to_email=trabajador.correo,
                    subject=subject,
                    html_content=html_content,
                )
            return HttpResponse("Correos enviados exitosamente.")
        else:
            return HttpResponse("Estado no válido.")
    else:
        trabajadores_lista = trabajadores.objects.all()
        return render(
            request,
            "contratos_agiles/mandarcorreo.html",
            {"trabajadores": trabajadores_lista},
        )


@handle_service_errors
def enviar_correos_masivos(request):
    if request.method == "POST":
        # Filtrar trabajadores cuyo campo 'vigente' es null
        trabajadores_lista = trabajadores.objects.filter(sent="no_enviado")
        for trabajador in trabajadores_lista:
            # Enviar correo
            subject = f"Hola {trabajador.nombre}, tienes un nuevo mensaje"
            mensaje = "Te damos la bienvenida. Estamos agradecidos de que formes parte de nuestra familia Fundo la Campana. <p></p> Te invitamos a que leas nuestras normas esenciales para una buena convivencia. <p></p> 1. Ser limpio y ordenado. <p></p> 2. Respetar a los demás. <p></p> 3. Ser puntual. <p></p> 4. Ser responsable. <p></p> 5. Ser honesto. <p></p> 6. Ser solidario. <p></p> 7. Ser respetuoso. <p></p> 8. Ser amable. <p></p> 9. Ser tolerante. <p></p> 10. Ser agradecido. <p></p>"
            html_content = f"<p>Hola {trabajador.nombre},</p><p>{mensaje}</p><p>Saludos,</p><p>Fundo la Campana</p>"
            send_contract_email(
                to_email=trabajador.correo, subject=subject, html_content=html_content
            )
            # Actualizar el campo 'vigente' a 'no vigente'
            trabajador.sent = "enviado"
            trabajador.save()

        return render(request, "contratos_agiles/menu.html")
    else:
        return render(request, "contratos_agiles/mandarcorreo.html")


@handle_service_errors
def enviar_correos(request):
    if request.method == "POST":
        # Filtrar trabajadores cuyo cargo tiene el estado "No vigente"
        trabajadores_lista = trabajadores.objects.filter(cargo__vigente="No vigente")
        for trabajador in trabajadores_lista:
            subject = f"Hola {trabajador.nombre}, tienes un nuevo mensaje"
            mensaje = f"Estamos agradecidos de que hayas formado parte de nuestra familia Fundo la Campana. <p></p> Es por eso que queremos invitarte a ser parte de nuestro equipo otra vez.<p></p> Por favor comunicate con nosotros a traves del numero {settings.CONTRATOS_CONTACT_PHONE}."
            html_content = f"<p>Hola {trabajador.nombre},</p><p>{mensaje}</p><p>Saludos,</p><p>Fundo la Campana</p>"
            send_contract_email(
                to_email=trabajador.correo, subject=subject, html_content=html_content
            )

        return HttpResponse("Correos enviados exitosamente.")
    else:
        trabajadores_lista = trabajadores.objects.all()
        return render(
            request,
            "contratos_agiles/correoxusuario.html",
            {"trabajadores": trabajadores_lista},
        )
