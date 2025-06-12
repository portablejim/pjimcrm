from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Client, Project

# Create your views here.
@login_required()
def index(request):
    client_list = Client.objects.all().order_by("name")
    return render(request, "pjimcrm/home.html", {"client_list": client_list})


@login_required()
def client_detail(request, client_id):
    client_record = get_object_or_404(Client, pk=client_id)
    project_list = client_record.project_set.all()
    return render(request, "pjimcrm/client_detail.html", {"client_record": client_record, "project_list": project_list})


@login_required()
def project_detail(request, client_id, project_id):
    project_record = get_object_or_404(Project, pk=project_id)
    return render(request, "pjimcrm/project_detail.html", {"project_record": project_record})

@login_required()
def project_create(request, client_id, project_id):
    return HttpResponse("Hello World. Project id:" + str(project_id))

@login_required()
def project_edit(request, client_id, project_id):
    return HttpResponse("Hello World. Project id:" + str(project_id))


@login_required()
def invoice_detail(request, invoice_id):
    return HttpResponse("Hello World. Invoice id:" + str(invoice_id))


@login_required()
def invoice_build(request, client_id):
    return HttpResponse("Build invoice. Client id:" + str(client_id))


@login_required()
def timer_index(request):
    return HttpResponse("Hello World. Timesheet index.")

