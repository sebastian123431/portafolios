from functools import wraps
from django.http import HttpResponse
from .documents import DocumentConversionUnavailable, DocumentProcessingError


class EmailUnavailable(RuntimeError):
    pass


def handle_service_errors(view):
    """Presenta únicamente fallos conocidos de los servicios opcionales."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except DocumentProcessingError as exc:
            return HttpResponse(str(exc), status=400, content_type="text/plain; charset=utf-8")
        except (DocumentConversionUnavailable, EmailUnavailable) as exc:
            return HttpResponse(str(exc), status=503, content_type="text/plain; charset=utf-8")
    return wrapped
