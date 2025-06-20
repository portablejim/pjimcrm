from datetime import datetime, timedelta
import uuid
from zoneinfo import ZoneInfo
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import resolve
from django.utils import timezone
from django.db.models import Q, Sum
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
    timer_status_object = get_running_timers()
    timer_status = json.dumps(timer_status_object)
    client_record = get_object_or_404(Client, pk=client_id)
    project_list = client_record.project_set.filter(is_active=True)
    pending_entries = Sum("timesheetentry__length_rounded", filter=Q(timesheetentry__is_invoiced=False))
    pending_hours = client_record.project_set.annotate(hours_sum=pending_entries).filter(hours_sum__gt=timedelta())
    total_pending_hours = pending_hours.aggregate(Sum("hours_sum"))["hours_sum__sum"]
    invoices = client_record.invoice_set.order_by("gen_date")
    return render(request, "pjimcrm/client_detail.html", {
        "client_record": client_record,
        "project_list": project_list,
        "invoice_list": invoices,
        "timer_status": timer_status,
        "timer_status_object": timer_status_object,
        "pending_hours": pending_hours,
        "total_pending_hours": total_pending_hours
        })


@login_required()
def project_detail(request, client_id, project_id):
    project_record = get_object_or_404(Project, pk=project_id)
    timers_not_invoiced = project_record.timesheetentry_set.filter(invoice_reference=None).order_by("-entry_date", "-created_date")
    timers_invoiced = project_record.timesheetentry_set.exclude(invoice_reference=None).order_by("-entry_date", "-created_date")
    return render(request, "pjimcrm/project_detail.html", {
        "project_record": project_record,
        "timer_list": timers_not_invoiced,
        "timer_invoiced_list": timers_invoiced,
    })

@login_required()
def project_create(request, client_id):
    client_record = get_object_or_404(Client, pk=client_id)
    if request.method == 'POST':
        new_project = Project(client=client_record)
        if 'name' in request.POST:
            new_project.name = request.POST["name"]
        if 'description' in request.POST:
            new_project.description = request.POST["description"]
        if 'is_active' in request.POST:
            new_project.description = request.POST["is_active"] == "true"
        new_project.save()
        return redirect("client_detail", client_id=client_id)
    else:
        return render(request, "pjimcrm/project_create.html", {"client_record": client_record})

@login_required()
def project_delete(request, client_id, project_id):
    project_record = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        project_record.delete()
    return HttpResponse("Hello World. Project id:" + str(project_id))

@login_required()
def project_edit(request, client_id, project_id):
    project_record = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        changed = False
        if "name" in request.POST and request.POST["name"] != project_record.name:
            project_record.name =  request.POST["name"]
            changed = True
        if "description" in request.POST and request.POST["description"] != project_record.description:
            project_record.description =  request.POST["description"]
            changed = True
        if "is_active" in request.POST:
            input_is_active = request.POST["is_active"] == "true"
            project_record.is_active =  input_is_active
            changed = True
        
        if changed:
            project_record.save()
        
        return redirect("project_detail", client_id=client_id, project_id=project_id)
    else:
        return render(request, "pjimcrm/project_edit.html", {"project_record": project_record})

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
def project_timer_detail(request, client_id, project_id, timer_id):
    timesheet_record = get_object_or_404(TimesheetEntry, pk=timer_id)
    return render(request, "pjimcrm/timesheet_project_detail.html", {"timesheet_record": timesheet_record, "client_id": client_id})


@login_required()
def invoice_detail(request, client_id, invoice_id):
    invoice_record = get_object_or_404(Invoice, pk=invoice_id)
    return render(request, "pjimcrm/invoice_detail.html", {"invoice_record": invoice_record, "client_id": client_id})


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
    timer_status_object = get_running_timers()
    timer_status = json.dumps(timer_status_object)
    projects = Project.objects.filter(is_active=True)
    latest_project = None
    if len(TimesheetEntry.objects.all()) > 0:
        latest_project = TimesheetEntry.objects.filter(project__is_active=True).order_by("-modified_date","project__name").first().project
    day_start = datetime(timezone.now().year, timezone.now().month, timezone.now().day, tzinfo=ZoneInfo("Australia/NSW"))
    todays_timers = TimesheetEntry.objects.filter(project__is_active=True, created_date__gte=day_start)
    return render(request, "pjimcrm/timer.html", {
        "timer_status": timer_status,
        "timer_status_object": timer_status_object,
        "project_list": projects,
        "latest_project_id": latest_project.id,
        "timer_list": todays_timers,
    })


@login_required()
def timer_detail(request, timer_id):
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
def timer_restart(request, timer_id):
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
def timer_current_get(request):
    return JsonResponse(get_running_timers())


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

@login_required()
def timer_current_delete(request):
    if request.method == 'POST' and 'id' in request.POST:
        timesheet_record = get_object_or_404(TimesheetEntry, pk=request.POST["id"])
        timesheet_record.delete()

    if 'retUrl' in request.POST:
        testFunc, testArgs, testKwargs = resolve(request.POST["retUrl"])
        if testFunc is not None:
            return HttpResponseRedirect(request.POST["retUrl"])
        else:
            return HttpResponse("OK")
    return HttpResponse("OK")

