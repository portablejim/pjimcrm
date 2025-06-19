import uuid
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import resolve
from django.utils import timezone
import json

from .models import Client, Project, Invoice, TimesheetEntry
from .utils import get_running_timers

# Create your views here.
@login_required()
def index(request):
    client_list = Client.objects.all().order_by("name")
    return render(request, "pjimcrm/home.html", {"client_list": client_list})


@login_required()
def client_detail(request, client_id):
    client_record = get_object_or_404(Client, pk=client_id)
    project_list = client_record.project_set.all()
    invoices = Invoice.objects.filter(client_id=client_record).order_by("gen_date")
    return render(request, "pjimcrm/client_detail.html", {"client_record": client_record, "project_list": project_list, "invoice_list": invoices})


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
def project_timer_start(request, client_id, project_id):
    if request.method == 'POST' and not get_running_timers()['running']:
        timesheet_record = TimesheetEntry()
        timesheet_record.target_user = request.user
        timesheet_record.project = Project(id=project_id)
        timesheet_record.description = uuid.uuid4()
        timesheet_record.description_set = False
        timesheet_record.timestamp_started = timezone.now()
        timesheet_record.save()

    if 'retUrl' in request.POST:
        testFunc, testArgs, testKwargs = resolve(request.POST["retUrl"])
        if testFunc is not None:
            return HttpResponseRedirect(request.POST["retUrl"])
        else:
            return HttpResponse("OK")
    return HttpResponse("OK")


@login_required()
def invoice_detail(request, client_id, invoice_id):
    return HttpResponse("Hello World. Invoice id:" + str(invoice_id))


@login_required()
def invoice_build(request, client_id):
    if 'retUrl' in request.POST:
        testFunc, testArgs, testKwargs = resolve(request.POST["retUrl"])
        if testFunc is not None:
            return HttpResponseRedirect(request.POST["retUrl"])
        else:
            return HttpResponse("OK")
    return HttpResponse("OK")


@login_required()
def timer_index(request):
    timer_status = json.dumps(get_running_timers())
    projects = Project.objects.filter(is_active=True)
    lastest_project = TimesheetEntry.objects.filter(project__is_active=True).order_by("-modified_date","project__name").first().project
    return render(request, "pjimcrm/timer.html", {"timer_status": timer_status, "project_list": projects, "latest_project_id": lastest_project.id})


@login_required()
def timer_current_get(request):
    return HttpResponse("Hello World. Timesheet index.")


@login_required()
def timer_current_add(request):
    if request.method == 'POST' and not get_running_timers()['running']:
        timesheet_record = TimesheetEntry()
        timesheet_record.target_user = request.user
        actionable = False
        if 'project' in request.POST and request.POST['project']:
            timesheet_record.project = Project(id=request.POST['project'])

        timesheet_record.description = uuid.uuid4()
        timesheet_record.description_set = False
        if 'description' in request.POST and request.POST['description'] and len(request.POST['description']) > 1:
            timesheet_record.description = request.POST['description']
            timesheet_record.description_set = True

        hours = 0
        minutes = 0
        if 'hours' in request.POST and request.POST['hours']:
            try:
                hours = int(request.POST['hours'])
                if hours > 0:
                    actionable = True
            except:
                pass
        if 'minutes' in request.POST and request.POST['minutes']:
            try:
                minutes = int(request.POST['minutes'])
                if minutes > 0:
                    actionable = True
            except:
                pass

        if 'startTimer' in request.POST and request.POST['startTimer'] == 'true':
            actionable = True
            timesheet_record.timestamp_started = timezone.now()

        if actionable:
            timesheet_record.save()
        else:
            return HttpResponse("not actionable", status=418)

    if 'retUrl' in request.POST:
        testFunc, testArgs, testKwargs = resolve(request.POST["retUrl"])
        if testFunc is not None:
            return HttpResponseRedirect(request.POST["retUrl"])
        else:
            return HttpResponse("OK")
    return HttpResponse("OK")


@login_required()
def timer_current_update(request):
    if request.method == 'POST' and 'id' in request.POST:
        timesheet_record = get_object_or_404(TimesheetEntry, pk=request.POST['id'])
        timesheet_record.target_user = request.user
        if 'description' in request.POST and request.POST['description'] and len(request.POST['description']) > 1:
            timesheet_record.description = request.POST['description']
            timesheet_record.description_set = True
            timesheet_record.save()
        return HttpResponse("OK")
    return HttpResponse("Invalid request", status=404)


@login_required()
def timer_current_stop(request):
    if request.method == 'POST' and 'id' in request.POST:
        timesheet_record = get_object_or_404(TimesheetEntry, pk=request.POST['id'])
        if 'description' in request.POST and request.POST['description'] and len(request.POST['description']) > 1:
            timesheet_record.description = request.POST['description']
            timesheet_record.description_set = True
        timesheet_record.target_user = request.user
        timesheet_record.timestamp_stopped = timezone.now()
        timesheet_record.save()
        if 'retUrl' in request.POST:
            testFunc, testArgs, testKwargs = resolve(request.POST["retUrl"])
            if testFunc is not None:
                return HttpResponseRedirect(request.POST["retUrl"])
                #return HttpResponse(request.POST["retUrl"])
            else:
                return HttpResponse("OK")
        return HttpResponse("OK")
    return HttpResponse("Invalid request", status=418)

