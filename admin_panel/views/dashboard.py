from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin


class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        from index_module.dashboard_services import (
            get_dashboard_charts_data,
            get_dashboard_stats,
            get_recent_contact_messages,
            get_recent_orders,
            get_recent_users,
        )

        ctx = super().get_context_data(**kwargs)
        ctx['stats'] = get_dashboard_stats()
        ctx['chart_data'] = get_dashboard_charts_data(14)
        ctx['recent_messages'] = get_recent_contact_messages()
        ctx['recent_orders'] = get_recent_orders()
        ctx['recent_users'] = get_recent_users()
        return ctx
