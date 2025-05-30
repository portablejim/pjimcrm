from django.contrib import admin

# Register your models here.
from .models import Client
from .models import Project
from .models import Invoice
from .models import InvoiceLine
from .models import TimesheetEntry

admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Invoice)
admin.site.register(InvoiceLine)
admin.site.register(TimesheetEntry)
