import datetime

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from .models import Client,Project,TimesheetEntry

# Create your tests here.

class TimesheetModelTests(TestCase):
    def test_auto_calculate_length(self):
        time1 = timezone.now() + datetime.timedelta(minutes=-20)
        time2 = timezone.now() + datetime.timedelta(minutes=-5)

        testClient = Client(name="Test", abn="86059194368", address="Test St", email="test@example.com", payment_allowance=10, pay_rate=10, payment_terms="Test Payment terms")
        testProject = Project(client=testClient, name="Project Name", description="Project Description")
        testTimesheetEntry = TimesheetEntry(project=testProject, timestamp_started=time1)

        self.assertEqual(time1, testTimesheetEntry.timestamp_started, "With a single time (running), the started time should be present.")
        self.assertIsNone(testTimesheetEntry.timestamp_stopped, "When running, the stopped time should be blank.")
        self.assertIsNone(testTimesheetEntry.length_raw, "When initially running, raw length should be empty.")
        self.assertIsNone(testTimesheetEntry.length_rounded, "When initially running, rounded length should be empty.")
        self.assertIsNone(testTimesheetEntry.timestamp_started_old, "When initially running, old time started should be empty.")
        self.assertIsNone(testTimesheetEntry.timestamp_stopped_old, "When initially running, old time stopped should be empty.")

        testTimesheetEntry.timestamp_stopped = time2
        self.assertIsNone(testTimesheetEntry.timestamp_started, "On stopping, the started time should be cleared")
        self.assertIsNone(testTimesheetEntry.timestamp_stopped, "On stopping, the stopped time should be cleared")
        self.assertEqual(datetime.timedelta(minutes=15), testTimesheetEntry.length_raw, "On stopping, the raw length should be set.")
        self.assertEqual(datetime.timedelta(minutes=15), testTimesheetEntry.length_rounde, "On stopping, the rounded length should be set.")
        self.assertEqual(time1, testTimesheetEntry.timestamp_started_old, "On stopping, the start time should be in the old fields.")
        self.assertEqual(time2, testTimesheetEntry.timestamp_stopped_old, "On stopping, the start time should be in the old fields.")

