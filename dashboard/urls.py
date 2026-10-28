from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "dashboard"


class LoginView(auth_views.LoginView):
    template_name = "dashboard/login.html"
    redirect_authenticated_user = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for f in form.fields.values():
            f.widget.attrs["class"] = "form-control form-control-lg"
        return form

    def get_default_redirect_url(self):
        return reverse_lazy("dashboard:overview")


urlpatterns = [
    path("", views.overview, name="overview"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page=reverse_lazy("dashboard:login")), name="logout"),
    path("password/", views.password, name="password"),
    path("search/", views.search, name="search"),
    path("settings/<slug:key>/", views.singleton, name="singleton"),
    path("<slug:key>/", views.resource_list, name="list"),
    path("<slug:key>/add/", views.add, name="add"),
    path("<slug:key>/bulk/", views.bulk_action, name="bulk"),
    path("<slug:key>/export/", views.export_csv, name="export"),
    path("<slug:key>/<int:pk>/", views.edit, name="edit"),
    path("<slug:key>/<int:pk>/delete/", views.delete, name="delete"),
    path("<slug:key>/<int:pk>/toggle/<str:field>/", views.toggle, name="toggle"),
]
