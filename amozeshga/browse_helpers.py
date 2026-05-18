"""Shared helpers for browse/list pages (search, sort, pagination)."""


def get_search_query(request):
    return request.GET.get('q', '').strip()


def get_sort(request, default='newest'):
    return request.GET.get('sort', default).strip() or default


def get_filter(request, default='all'):
    return request.GET.get('filter', default).strip() or default


def build_query_string(request, exclude=('page',)):
    params = request.GET.copy()
    for key in exclude:
        params.pop(key, None)
    return params.urlencode()


def has_active_filters(request, *, search=True, filter_default='all'):
    if search and get_search_query(request):
        return True
    if get_filter(request, filter_default) != filter_default:
        return True
    if request.GET.get('sort') and request.GET.get('sort') != 'newest':
        return True
    return False
