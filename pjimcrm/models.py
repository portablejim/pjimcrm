from django.conf import settings
from django.db import models
from datetime import date as date_mod, timedelta
import math
import uuid

# Create your models here.
class Client(models.Model):
    name = models.CharField("Name", max_length=400)
    abn = models.CharField("ABN", max_length=15)
    email = models.EmailField("Email")
    address = models.TextField("Address", blank=True)
    payment_allowance = models.PositiveSmallIntegerField("Payment Allowance (days)")
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
    client = models.ForeignKey(Client, on_delete=models.RESTRICT)
    invoice_uuid = models.UUIDField("UUID", default=uuid.uuid4())
    gen_date = models.DateField("Date", default=date_mod.today)
    pay_date = models.DateField("Due Date")
    payment_terms = models.TextField("Payment Terms")
    is_paid = models.BooleanField("Paid", default=False)
    created_date = models.DateTimeField("Created Date", auto_now_add=True)
    modified_date = models.DateTimeField("Modified Date", auto_now=True)

    def __str__(self):
        return "Invoice #" + self.invoice_num + " (" + self.client.name + ")"

    def save(self, **kwargs):
        if self.pay_date is None:
            self.pay_date = self.gen_date
            if self.client.payment_allowance > 0:
                self.pay_date = self.gen_date + timedelta(days=self.client.payment_allowance)
        return super().save(**kwargs)

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

    def save(self, **kwargs):
        if self.price is None:
            self.price = 0
            if self.invoice.client.pay_rate > 0:
                self.price = self.invoice.client.pay_rate
        if self.quantity is None:
            self.quantity = 0

        self.total = self.price * self.quantity

        return super().save(**kwargs)

class TimesheetEntry(models.Model):
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(Project, on_delete=models.RESTRICT)
    description = models.CharField("Description")
    description_set = models.BooleanField("Description has been set", default=False)
    length_raw = models.DurationField("Length (raw)", default=timedelta())
    length_rounded = models.DurationField("Length (rounded)", default=timedelta())
    timestamp_started = models.DateTimeField("Time Started", null=True, blank=True)
    timestamp_stopped = models.DateTimeField("Time Stopped", null=True, blank=True)
    timestamp_started_old = models.DateTimeField("Previously Started", null=True, blank=True)
    timestamp_stopped_old = models.DateTimeField("Previously Stopped", null=True, blank=True)
    is_invoiced = models.BooleanField("Invoiced", default=False)
    invoice_reference = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateTimeField("Created Date", auto_now_add=True)
    modified_date = models.DateTimeField("Modified Date", auto_now=True)

    def __str__(self):
        return "Timesheet Entry" + self.description

    def save(self, **kwargs):
        if self.timestamp_started is not None and self.timestamp_stopped is not None:
            # Both timestamp fields set.
            new_timedelta = timedelta()
            if self.length_raw is not None and self.length_raw > timedelta():
                new_timedelta += self.length_raw
            if self.timestamp_stopped > self.timestamp_started:
                new_timedelta += (self.timestamp_stopped - self.timestamp_started)
            
            # Round to second.
            new_timedelta = timedelta(seconds=new_timedelta.seconds)

            self.length_raw = new_timedelta

            raw_minute_fraction = (new_timedelta.seconds / 60) / 15
            rounded_minute_fraction= math.ceil(raw_minute_fraction)
            minutes_difference = (rounded_minute_fraction * 15) - (self.length_raw.seconds / 60)
            self.length_rounded = self.length_raw + timedelta(seconds=minutes_difference * 60)
            

            self.timestamp_started_old = self.timestamp_started
            self.timestamp_stopped_old = self.timestamp_stopped
            self.timestamp_started = None
            self.timestamp_stopped = None
        return super().save(**kwargs)


