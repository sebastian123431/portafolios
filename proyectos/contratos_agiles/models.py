from django.db import models


class Login(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def nombre_usuario(self):
        return "{}".format(self.username)

    def __str__(self):
        return self.nombre_usuario()

    class Meta:
        db_table = "contratoApp_login"


class trabajadores(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    rut = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)
    afp = models.CharField(max_length=50)
    estado_civil = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    previcion_salud = models.CharField(max_length=50)
    foto = models.ImageField(upload_to="trabajadores", null=True, blank=True)
    correo = models.EmailField(max_length=50)
    sent = models.CharField(max_length=50, default="no_enviado")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Cargo(models.Model):
    trabajadores = models.ForeignKey(trabajadores, on_delete=models.CASCADE)
    labor = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()
    sueldo = models.IntegerField()
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    vigente_choices = [
        ("Vigente", "Vigente"),
        ("No vigente", "No vigente"),
    ]
    vigente = models.CharField(
        max_length=50, choices=vigente_choices, default="Vigente"
    )

    def __str__(self):
        return f"{self.labor} - {self.trabajadores}"


class antecedentes(models.Model):
    trabajador = models.ForeignKey(trabajadores, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=50)
    fecha = models.DateField()


class Contrato(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to="contratos/")

    def __str__(self):
        return self.nombre


class ContratoTrabajador(models.Model):
    trabajador = models.ForeignKey(trabajadores, on_delete=models.CASCADE)
    ArchivoContrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_termino = models.DateField()

    def __str__(self):
        return f"Contrato de {self.trabajador.nombre} {self.trabajador.apellido} - {self.ArchivoContrato.nombre}"


class ArchivoContrato(models.Model):
    contrato_trabajador = models.ForeignKey(
        ContratoTrabajador, on_delete=models.CASCADE, related_name="archivos"
    )
    archivo = models.FileField(upload_to="contratos_generados/")
    fecha_subida = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Archivo de {self.contrato_trabajador}"


class Asistencia(models.Model):
    trabajador = models.ForeignKey(trabajadores, on_delete=models.CASCADE)
    fecha = (
        models.DateField()
    )  # Se quitará auto_now_add para que la fecha se elija manualmente
    presente = models.BooleanField(default=False)

    # opciones para el campo presente en el formulario
    presente_choices = [
        ("Presente", "Presente"),
        ("Ausente", "Ausente"),
    ]

    def trabajador_vigente(self):
        return Cargo.objects.filter(
            trabajadores=self.trabajador,
            fecha_ingreso__lte=self.fecha,
            vigente="Vigente",
        ).exists()

    def __str__(self):
        return f"Asistencia de {self.trabajador.nombre} {self.trabajador.apellido} - {'Presente' if self.presente else 'Ausente'} el {self.fecha}"
