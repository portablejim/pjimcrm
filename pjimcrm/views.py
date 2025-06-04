from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return HttpResponse("Hello Authed World. This is the crm index.")
    else:
        return HttpResponse("Hello Non-Authed World. This is the crm index.")


def client_detail(request, client_id):
    return HttpResponse("Hello World. Client id:" + client_id)


def project_detail(request, client_id, project_id):
    return HttpResponse("Hello World. Project id:" + project_id)

def project_create(request, client_id, project_id):
    return HttpResponse("Hello World. Project id:" + project_id)

def project_edit(request, client_id, project_id):
    return HttpResponse("Hello World. Project id:" + project_id)


def invoice_detail(request, invoice_id):
    return HttpResponse("Hello World. Invoice id:" + invoice_id)


def invoice_build(request, client_id):
    return HttpResponse("Build invoice. Client id:" + client_id)


def timer_index(request):
    return HttpResponse("Hello World. Timesheet index.")

