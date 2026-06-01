import json

from django.http import HttpResponse
from django.template.response import TemplateResponse


def htmx_trigger(payload: dict) -> HttpResponse:
    return HttpResponse(status=204, headers={'HX-Trigger': json.dumps(payload, ensure_ascii=False)})


def render_modal_form(request, template, context):
    return TemplateResponse(request, template, context)
