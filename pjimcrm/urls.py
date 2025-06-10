from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("client/<int:client_id>/", views.client_detail, name="client_detail"),
    path("client/<int:client_id>/project/<int:project_id>/", views.project_detail, name="project_detail"),
    path("client/<int:client_id>/create-project", views.project_create, name="project_create"),
    path("client/<int:client_id>/project/<int:project_id>/edit", views.project_edit, name="project_edit"),
    path("client/<int:client_id>/invoice/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path("client/<int:client_id>/build-invoice", views.invoice_build, name="invoice_build"),
    path("timer/", views.timer_index, name="timer_index"),
]