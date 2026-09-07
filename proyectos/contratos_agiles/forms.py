from django import forms

from .models import Cargo, Contrato, ContratoTrabajador, trabajadores


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ["nombre", "descripcion", "archivo"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Seleccionar archivo")


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ["labor", "fecha_ingreso", "sueldo", "observaciones", "vigente"]
        widgets = {
            "fecha_ingreso": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "observaciones": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "labor": forms.TextInput(attrs={"class": "form-control"}),
            "sueldo": forms.NumberInput(attrs={"class": "form-control"}),
            "vigente": forms.Select(attrs={"class": "form-control"}),
        }


class TrabajadorForm(forms.ModelForm):
    class Meta:
        model = trabajadores
        fields = [
            "nombre",
            "apellido",
            "rut",
            "direccion",
            "telefono",
            "afp",
            "estado_civil",
            "fecha_nacimiento",
            "previcion_salud",
            "foto",
            "correo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "rut": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "afp": forms.TextInput(attrs={"class": "form-control"}),
            "estado_civil": forms.Select(attrs={"class": "form-control"}),
            "previcion_salud": forms.TextInput(attrs={"class": "form-control"}),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ContratoTrabajadorForm(forms.ModelForm):
    class Meta:
        model = ContratoTrabajador
        fields = ["fecha_termino"]
        widgets = {
            "fecha_termino": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
