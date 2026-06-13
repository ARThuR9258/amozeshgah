from .utils import build_seo


class SEOMixin:
    """Mixin برای Class-Based Views — متای SEO در context."""

    seo_title = ''
    seo_description = ''
    seo_keywords = ''
    seo_canonical = ''
    seo_noindex = None
    seo_og_type = 'website'
    seo_og_image = ''
    seo_breadcrumbs = None
    seo_faq_items = None
    seo_article_schema = None

    def get_seo_override(self) -> dict:
        data = {}
        if self.seo_title:
            data['title'] = self.seo_title
        if self.seo_description:
            data['description'] = self.seo_description
        if self.seo_keywords:
            data['keywords'] = self.seo_keywords
        if self.seo_canonical:
            data['canonical'] = self.seo_canonical
        if self.seo_noindex is not None:
            data['noindex'] = self.seo_noindex
        if self.seo_og_type:
            data['og_type'] = self.seo_og_type
        if self.seo_og_image:
            data['og_image'] = self.seo_og_image
        if self.seo_breadcrumbs is not None:
            data['breadcrumbs'] = self.seo_breadcrumbs
        if self.seo_faq_items is not None:
            data['faq_items'] = self.seo_faq_items
        if self.seo_article_schema is not None:
            data['article_schema'] = self.seo_article_schema
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        override = self.get_seo_override()
        if override:
            context['seo'] = build_seo(self.request, override=override)
        return context


def seo_override(request, **kwargs):
    """برای function-based views قبل از render."""
    request._seo_override = kwargs
