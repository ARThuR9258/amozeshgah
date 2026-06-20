"""ابزارهای SEO — canonical، meta، schema."""

import json
from urllib.parse import urljoin

from django.urls import NoReverseMatch, reverse

from . import seo_config as cfg


def absolute_url(path_or_url: str, request=None) -> str:
    if path_or_url.startswith(('http://', 'https://')):
        return path_or_url
    base = cfg.SITE_URL.rstrip('/')
    if request:
        return request.build_absolute_uri(path_or_url)
    return urljoin(base + '/', path_or_url.lstrip('/'))


def should_noindex(path: str, url_name: str | None = None) -> bool:
    if path in cfg.NOINDEX_EXACT:
        return True
    for prefix in cfg.NOINDEX_PREFIXES:
        if path.startswith(prefix):
            return True
    if url_name and url_name in cfg.PAGE_META:
        return cfg.PAGE_META[url_name].get('noindex', False)
    return False


def resolve_page_meta(url_name: str | None) -> dict:
    if url_name and url_name in cfg.PAGE_META:
        return dict(cfg.PAGE_META[url_name])
    return {}


def build_seo(request, *, override: dict | None = None) -> dict:
    """ساخت دیکشنری SEO برای قالب — override از view اولویت دارد."""
    override = override or {}
    url_name = None
    if request.resolver_match:
        url_name = request.resolver_match.view_name

    page_meta = resolve_page_meta(url_name)
    path = request.path

    title = override.get('title') or page_meta.get('title') or cfg.DEFAULT_TITLE
    description = override.get('description') or page_meta.get('description') or cfg.DEFAULT_DESCRIPTION
    keywords = override.get('keywords') or page_meta.get('keywords') or cfg.DEFAULT_KEYWORDS

    canonical = override.get('canonical')
    if not canonical:
        canonical = request.build_absolute_uri(request.path)
        if request.GET:
            # پارامترهای فیلتر را از canonical حذف کن
            canonical = request.build_absolute_uri(request.path)

    noindex = override.get('noindex')
    if noindex is None:
        noindex = page_meta.get('noindex', False) or should_noindex(path, url_name)

    og_type = override.get('og_type', 'website')
    og_image = override.get('og_image') or cfg.OG_IMAGE
    if og_image and not og_image.startswith('http'):
        og_image = absolute_url(og_image, request)

    breadcrumbs = override.get('breadcrumbs', [])
    faq_items = override.get('faq_items', [])
    article_schema = override.get('article_schema')
    extra_schemas = override.get('extra_schemas', [])

    schemas = _build_schemas(
        request, title, description, canonical,
        breadcrumbs=breadcrumbs,
        faq_items=faq_items,
        article_schema=article_schema,
        og_type=og_type,
        extra_schemas=extra_schemas,
    )

    return {
        'title': title,
        'description': description,
        'keywords': keywords,
        'canonical': canonical,
        'noindex': noindex,
        'nofollow': override.get('nofollow', False),
        'og_type': og_type,
        'og_image': og_image,
        'og_image_alt': override.get('og_image_alt', cfg.SITE_NAME),
        'twitter_card': override.get('twitter_card', 'summary_large_image'),
        'breadcrumbs': breadcrumbs,
        'schemas': schemas,
        'site_name': cfg.SITE_NAME,
        'site_url': cfg.SITE_URL,
        'theme_color': cfg.THEME_COLOR,
    }


def _build_schemas(request, title, description, canonical, **kwargs):
    schemas = []
    site_url = cfg.SITE_URL

    schemas.append({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': cfg.SITE_NAME,
        'url': site_url,
        'description': cfg.DEFAULT_DESCRIPTION,
        'inLanguage': 'fa-IR',
        # نمونه سوالات — موقتاً غیرفعال
        # 'potentialAction': {
        #     '@type': 'SearchAction',
        #     'target': {
        #         '@type': 'EntryPoint',
        #         'urlTemplate': f'{site_url}/questions/?q={{search_term_string}}',
        #     },
        #     'query-input': 'required name=search_term_string',
        # },
    })

    schemas.append({
        '@context': 'https://schema.org',
        '@type': 'Organization',
        'name': cfg.SITE_NAME,
        'url': site_url,
        'logo': absolute_url('/static/images/logo-full.png', request),
        'description': cfg.DEFAULT_DESCRIPTION,
        'sameAs': [],
    })

    breadcrumbs = kwargs.get('breadcrumbs') or []
    if breadcrumbs:
        items = []
        for i, crumb in enumerate(breadcrumbs, start=1):
            items.append({
                '@type': 'ListItem',
                'position': i,
                'name': crumb['name'],
                'item': absolute_url(crumb.get('url', ''), request) if crumb.get('url') else None,
            })
        schemas.append({
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': items,
        })

    faq_items = kwargs.get('faq_items') or []
    if faq_items:
        schemas.append({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            'mainEntity': [
                {
                    '@type': 'Question',
                    'name': item['question'],
                    'acceptedAnswer': {
                        '@type': 'Answer',
                        'text': item['answer'],
                    },
                }
                for item in faq_items
            ],
        })

    article_schema = kwargs.get('article_schema')
    if article_schema:
        schemas.append(article_schema)

    for extra in kwargs.get('extra_schemas') or []:
        schemas.append(extra)

    return schemas


def schemas_to_json(schemas: list) -> str:
    return json.dumps(schemas, ensure_ascii=False, separators=(',', ':'))


def reverse_or_none(viewname, *args, **kwargs) -> str | None:
    try:
        return reverse(viewname, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return None
