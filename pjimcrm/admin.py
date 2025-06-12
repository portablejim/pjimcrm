from django.contrib import admin

# Register your models here.
from .models import Client
from .models import Project
from .models import Invoice
from .models import InvoiceLine
from .models import TimesheetEntry

class TimesheetEntryInline(admin.StackedInline):
    model = TimesheetEntry
    fields = ["target_user", "project", "description", "description_set", "length_raw", "timestamp_started"]
    extra = 1
    

class ProjectAdmin(admin.ModelAdmin):
    inlines = [TimesheetEntryInline]

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class ClientAdmin(admin.ModelAdmin):
    inlines = [ProjectInline]

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 3

class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceLineInline]

admin.site.register(Client, ClientAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceLine)
admin.site.register(TimesheetEntry)
