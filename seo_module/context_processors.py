from index_module.site_info import SITE_INFO

from . import seo_config as cfg
from .utils import build_seo


def seo_context(request):
    """متای SEO سراسری — view می‌تواند با context['seo'] بازنویسی کند."""
    override = getattr(request, '_seo_override', None)
    seo = build_seo(request, override=override)
    return {
        'seo': seo,
        'site': SITE_INFO,
        'google_site_verification': cfg.GOOGLE_SITE_VERIFICATION,
        'google_analytics_id': cfg.GOOGLE_ANALYTICS_ID,
    }
