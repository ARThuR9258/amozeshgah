"""میان‌افزارهای SEO و Performance."""

from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


class SEOSecurityHeadersMiddleware(MiddlewareMixin):
    """هدرهای امنیتی و کش برای بهبود Performance و Best Practices."""

    STATIC_CACHE_SECONDS = 31536000  # 1 year
    HTML_CACHE_SECONDS = 3600

    def process_response(self, request, response):
        path = request.path

        if path.startswith('/static/') or path.endswith((
            '.css', '.js', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.woff2', '.ico',
        )):
            if 'Cache-Control' not in response:
                response['Cache-Control'] = f'public, max-age={self.STATIC_CACHE_SECONDS}, immutable'
        elif (
            response.get('Content-Type', '').startswith('text/html')
            and response.status_code == 200
            and not request.user.is_authenticated
            and not path.startswith(('/dashboard/', '/admin/', '/account/panel/'))
        ):
            if 'Cache-Control' not in response:
                response['Cache-Control'] = f'public, max-age={self.HTML_CACHE_SECONDS}'

        if 'X-Content-Type-Options' not in response:
            response['X-Content-Type-Options'] = 'nosniff'
        if 'Referrer-Policy' not in response:
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        patch_vary_headers(response, ('Accept-Encoding',))
        return response
