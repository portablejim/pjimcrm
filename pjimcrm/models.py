from django.conf import settings
from django.db import models
from datetime import date as date_mod, timedelta
import uuid

# Create your models here.
class Client(models.Model):
    name = models.CharField("Name", max_length=400)
    abn = models.CharField("ABN", max_length=15)
    email = models.EmailField("Email")
    address = models.TextField("Address", blank=True)
    payment_allowance = models.IntegerField("Payment Allowance (days)")
    pay_rate = models.DecimalField("Pay Rate", decimal_places=2, max_digits=10)
    payment_terms = models.TextField("Payment Terms")
    created_date = models.DateTimeField("Created Date", auto_now_add=True)
    modified_date = models.DateTimeField("Modified Date", auto_now=True)

    def __str__(self):
        return self.name + "(" + self.abn + ")"

class Project(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField("Name")
    description = models.CharField("Description")
    is_active = models.BooleanField("Is Active", default=True)
    created_date = models.DateTimeField("Created Date", auto_now_add=True)
    modified_date = models.DateTimeField("Modified Date", auto_now=True)

    def __str__(self):
        return self.name + "(" + self.client.name + ")"

class Invoice(models.Model):
    invoice_num = models.CharField("Invoice #", unique=True)
    invoice_uuid = models.UUIDField("UUID", default=uuid.uuid4())
    gen_date = models.DateField("Date", default=date_mod.today)
    pay_date = models.DateField("Due Date")
    payment_terms = models.TextField("Payment Terms")
    is_paid = models.BooleanField("Paid")
    created_date = models.DateTimeField("Created Date", auto_now_add=True)
    modified_date = models.DateTimeField("Modified Date", auto_now=True)

    def __str__(self):
        return "Invoice #" + self.invoice_num

class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    description = models.CharField("Description")
    description_extra = models.CharField("Extended Description")
    price = models.DecimalField("Rate/hr", decimal_places=2, max_digits=10)
    quantity = models.DecimalField("Hours", decimal_places=3, max_digits=10)
    total = models.DecimalField("Total", decimal_places=2, max_digits=10)
    created_date = models.DateTimeField("Created Date", auto_now_add=True)
    modified_date = models.DateTimeField("Modified Date", auto_now=True)

    def __str__(self):
        return "Line Item #" + self.invoice.invoice_num + ": " + self.description

class TimesheetEntry(models.Model):
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(Project, on_delete=models.RESTRICT)
    description = models.CharField("Description")
    description_set = models.BooleanField("Description has been set")
    length_raw = models.DurationField("Length (raw)", default=timedelta())
    length_rounded = models.DurationField("Length (rounded)", default=timedelta())
    timestamp_started = models.DateTimeField("Time Started", null=True, blank=True)
    timestamp_stopped = models.DateTimeField("Time Stopped", null=True, blank=True)
    timestamp_started_old = models.DateTimeField("Previously Started", null=True, blank=True)
    timestamp_stopped_old = models.DateTimeField("Previously Stopped", null=True, blank=True)
    is_invoiced = models.BooleanField("Invoiced")
    invoice_reference = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateTimeField("Created Date", auto_now_add=True)
    modified_date = models.DateTimeField("Modified Date", auto_now=True)

    def __str__(self):
        return "Timesheet Entry" + self.description


