"""Proceso auxiliar de conversión Word; no configura ni inicia Django."""
import sys
from contextlib import suppress


def convert(source, destination):
    # Estos módulos se cargan únicamente en el proceso de conversión Windows.
    import pythoncom
    import win32com.client

    word = document = None
    pythoncom.CoInitialize()
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        document = word.Documents.Open(source)
        document.SaveAs(destination, FileFormat=17)
    finally:
        if document is not None:
            with suppress(Exception):
                document.Close(False)
            document = None
        if word is not None:
            with suppress(Exception):
                word.Quit()
            word = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    try:
        convert(sys.argv[1], sys.argv[2])
    except Exception:
        # El servicio principal devuelve el mensaje controlado al usuario.
        sys.exit(1)
