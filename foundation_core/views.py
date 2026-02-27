from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"


class AdminPanelView(TemplateView):
    template_name = 'admin/admin_panel.html'
