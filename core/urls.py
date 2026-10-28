from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("lead/", views.lead, name="lead"),
    path("favorites/", views.favorites, name="favorites"),
    path("favorites/toggle/<int:pk>/", views.toggle_favorite, name="toggle_favorite"),
]
