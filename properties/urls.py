from django.urls import path

from . import views

app_name = "properties"

urlpatterns = [
    path("", views.property_list, name="list"),
    path("agents/", views.agent_list, name="agent_list"),
    path("agents/<slug:slug>/", views.agent_detail, name="agent_detail"),
    path("<slug:slug>/", views.property_detail, name="detail"),
]
