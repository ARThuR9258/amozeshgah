from django import template

register = template.Library()

FIELD_ICONS = {
    'name': 'fa-tag',
    'slug': 'fa-link',
    'title': 'fa-heading',
    'text': 'fa-align-right',
    'description': 'fa-align-left',
    'username': 'fa-at',
    'phone_number': 'fa-mobile-alt',
    'email': 'fa-envelope',
    'password': 'fa-key',
    'confirm_password': 'fa-lock',
    'first_name': 'fa-user',
    'last_name': 'fa-user',
    'credits': 'fa-coins',
    'subscription_status': 'fa-crown',
    'category': 'fa-folder',
    'difficulty': 'fa-signal',
    'correct_answer': 'fa-check-circle',
    'image': 'fa-image',
    'pdf_file': 'fa-file-pdf',
    'option_1': 'fa-list-ol',
    'option_2': 'fa-list-ol',
    'option_3': 'fa-list-ol',
    'option_4': 'fa-list-ol',
    'option_1_image': 'fa-image',
    'option_2_image': 'fa-image',
    'option_3_image': 'fa-image',
    'option_4_image': 'fa-image',
    'display_order': 'fa-sort-numeric-down',
    'price': 'fa-money-bill-wave',
    'plan_type': 'fa-layer-group',
    'plan': 'fa-gem',
    'user': 'fa-user',
    'status': 'fa-info-circle',
    'amount': 'fa-coins',
    'authority': 'fa-barcode',
    'ref_id': 'fa-receipt',
    'paid_at': 'fa-calendar-check',
    'started_at': 'fa-play',
    'expires_at': 'fa-hourglass-end',
    'duration_days': 'fa-calendar-day',
    'credits_amount': 'fa-ticket-alt',
    'daily_free_attempts': 'fa-redo',
    'features_text': 'fa-list-ul',
}


@register.filter
def glass_icon(field):
    return FIELD_ICONS.get(field.name, 'fa-pen')


@register.filter
def is_checkbox(field):
    return field.field.widget.__class__.__name__ in (
        'CheckboxInput', 'NullBooleanSelect',
    )


@register.filter
def is_textarea(field):
    return field.field.widget.__class__.__name__ == 'Textarea'


@register.filter
def is_file(field):
    return field.field.widget.__class__.__name__ in (
        'ClearableFileInput', 'FileInput',
    )


@register.filter
def is_select(field):
    return field.field.widget.__class__.__name__ in (
        'Select', 'SelectMultiple',
    )


@register.simple_tag
def form_has_checkboxes(form):
    for field in form:
        if is_checkbox(field):
            return True
    return False
