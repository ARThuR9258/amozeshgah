import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def to_json_ld(value):
    return mark_safe(json.dumps(value, ensure_ascii=False, separators=(',', ':')))


@register.inclusion_tag('shared/breadcrumbs.html', takes_context=True)
def render_breadcrumbs(context):
    seo = context.get('seo', {})
    return {'breadcrumbs': seo.get('breadcrumbs', [])}


@register.inclusion_tag('shared/internal_links.html', takes_context=True)
def render_internal_links(context):
    from blog_module.models import Article
    from quizbuilder_module.models import Category
    from seo_module.models import GuidePage

    return {
        'guides': GuidePage.objects.filter(is_published=True)[:6],
        'categories': Category.objects.filter(is_active=True)[:6],
        'articles': Article.objects.filter(is_published=True)[:4],
    }
