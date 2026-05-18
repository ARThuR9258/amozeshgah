"""ابزارهای مشترک لیست‌های پنل مدیریت."""


def build_pagination_query(request, exclude=('page',)):
    q = request.GET.copy()
    for key in exclude:
        q.pop(key, None)
    return q.urlencode()
