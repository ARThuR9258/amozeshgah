from index_module.dashboard_services import get_dashboard_stats


def dashboard_sidebar(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    stats = get_dashboard_stats()
    return {
        'sidebar_unread_messages': stats['unread_messages_count'],
        'sidebar_pending_orders': stats['pending_orders_count'],
    }
