"""Context helpers for dashboard CRUD forms."""


def dashboard_form_context(
    *,
    page_title,
    page_heading,
    page_icon,
    breadcrumbs,
    cancel_url,
    submit_label='ذخیره',
    page_subtitle='',
    form_enctype='application/x-www-form-urlencoded',
    form_section_title='',
    form_section_icon='edit',
    form_readonly_info='',
):
    return {
        'page_title': page_title,
        'page_heading': page_heading,
        'page_icon': page_icon,
        'page_subtitle': page_subtitle,
        'breadcrumbs': breadcrumbs,
        'cancel_url': cancel_url,
        'submit_label': submit_label,
        'form_enctype': form_enctype,
        'form_section_title': form_section_title,
        'form_section_icon': form_section_icon,
        'form_readonly_info': form_readonly_info,
    }


def form_has_files(form):
    from django.forms import FileField, ImageField

    return any(
        isinstance(f, (FileField, ImageField))
        for f in form.fields.values()
    )
