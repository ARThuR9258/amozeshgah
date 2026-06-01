import json

from django.http import HttpResponse
from django.template.response import TemplateResponse


def is_htmx(request) -> bool:
    return request.headers.get('HX-Request') == 'true'


def htmx_trigger(payload: dict) -> HttpResponse:
    """
    پاسخ موفق HTMX. JSON هدر باید ASCII باشد (متن فارسی toast با \\u escape می‌شود)
    وگرنه مرورگر HX-Trigger را نادیده می‌گیرد و مودال باز می‌ماند.
    """
    return HttpResponse(
        '',
        status=200,
        headers={
            'HX-Trigger': json.dumps(payload, ensure_ascii=True),
            'HX-Reswap': 'none',
        },
    )


def render_modal_form(request, template, context):
    return TemplateResponse(request, template, context)
