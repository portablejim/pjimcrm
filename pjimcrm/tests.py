import datetime

from django.contrib.auth.models import User
from django.test import Client as TestClient
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import utils
from .models import Client, Project, TimesheetEntry

# Create your tests here.


class TimesheetModelTests(TestCase):
    def test_auto_calculate_length(self):
        time1 = timezone.now() + datetime.timedelta(minutes=-20)
        time2 = timezone.now() + datetime.timedelta(minutes=-5)

        testClient = Client(
            name="Test",
            abn="86059194368",
            address="Test St",
            email="test@example.com",
            payment_allowance=10,
            pay_rate=10,
            payment_terms="Test Payment terms",
        )
        testClient.save()
        testProject = Project(client=testClient, name="Project Name", description="Project Description")
        testProject.save()

        # Start a timer.
        testTimesheetEntry = TimesheetEntry(
            project=testProject, timestamp_started=time1, description="Test", description_set=False, is_invoiced=False
        )
        testTimesheetEntry.save()

        self.assertEqual(
            time1,
            testTimesheetEntry.timestamp_started,
            "With a single time (running), the started time should be present.",
        )
        self.assertIsNone(testTimesheetEntry.timestamp_stopped, "When running, the stopped time should be blank.")
        self.assertEqual(
            datetime.timedelta(), testTimesheetEntry.length_raw, "When initially running, raw length should be empty."
        )
        self.assertEqual(
            datetime.timedelta(),
            testTimesheetEntry.length_rounded,
            "When initially running, rounded length should be empty.",
        )
        self.assertIsNone(
            testTimesheetEntry.timestamp_started_old, "When initially running, old time started should be empty."
        )
        self.assertIsNone(
            testTimesheetEntry.timestamp_stopped_old, "When initially running, old time stopped should be empty."
        )

        # Stop the timer fresh.
        testTimesheetEntry.timestamp_stopped = time2
        testTimesheetEntry.save()

        self.assertIsNone(testTimesheetEntry.timestamp_started, "On stopping, the started time should be cleared")
        self.assertIsNone(testTimesheetEntry.timestamp_stopped, "On stopping, the stopped time should be cleared")
        self.assertEqual(
            datetime.timedelta(minutes=15), testTimesheetEntry.length_raw, "On stopping, the raw length should be set."
        )
        self.assertEqual(
            datetime.timedelta(minutes=15),
            testTimesheetEntry.length_rounded,
            "On stopping, the rounded length should be set.",
        )
        self.assertEqual(
            time1, testTimesheetEntry.timestamp_started_old, "On stopping, the start time should be in the old fields."
        )
        self.assertEqual(
            time2, testTimesheetEntry.timestamp_stopped_old, "On stopping, the start time should be in the old fields."
        )

        # Prented to start it and stop it.
        testTimesheetEntry.timestamp_started = time1
        testTimesheetEntry.timestamp_stopped = time2
        testTimesheetEntry.save()

        self.assertIsNone(testTimesheetEntry.timestamp_started, "On stopping, the started time should be cleared")
        self.assertIsNone(testTimesheetEntry.timestamp_stopped, "On stopping, the stopped time should be cleared")
        self.assertEqual(
            datetime.timedelta(minutes=30),
            testTimesheetEntry.length_raw,
            "On stopping again, the raw length should be added.",
        )
        self.assertEqual(
            datetime.timedelta(minutes=30),
            testTimesheetEntry.length_rounded,
            "On stopping again, the rounded length should be added.",
        )
        self.assertEqual(
            time1, testTimesheetEntry.timestamp_started_old, "On stopping, the start time should be in the old fields."
        )
        self.assertEqual(
            time2, testTimesheetEntry.timestamp_stopped_old, "On stopping, the start time should be in the old fields."
        )

        # Prented to start it and stop it. A minute should cause the rounded value to tick over.
        time1 = timezone.now() + datetime.timedelta(minutes=-6)
        time2 = timezone.now() + datetime.timedelta(minutes=-5)
        testTimesheetEntry.timestamp_started = time1
        testTimesheetEntry.timestamp_stopped = time2
        testTimesheetEntry.save()

        self.assertIsNone(testTimesheetEntry.timestamp_started, "On stopping, the started time should be cleared")
        self.assertIsNone(testTimesheetEntry.timestamp_stopped, "On stopping, the stopped time should be cleared")
        self.assertEqual(
            datetime.timedelta(minutes=31),
            testTimesheetEntry.length_raw,
            "On stopping again, the raw length should be added.",
        )
        self.assertEqual(
            datetime.timedelta(minutes=45),
            testTimesheetEntry.length_rounded,
            "On stopping again, the rounded length should be added.",
        )
        self.assertEqual(
            time1, testTimesheetEntry.timestamp_started_old, "On stopping, the start time should be in the old fields."
        )
        self.assertEqual(
            time2, testTimesheetEntry.timestamp_stopped_old, "On stopping, the start time should be in the old fields."
        )

    def test_timer_index(self):
        response = self.client.get(reverse("timer_index"))
        self.assertEqual(302, response.status_code)

        test_client = TestClient()
        test_user = User.objects.create_user("test")
        test_client.force_login(user=test_user)

        response = self.client.get(reverse("timer_index"))
        self.assertEqual(302, response.status_code)

    def test_parse_timesheet_length(self):
        self.assertIsNone(utils.parse_timer_length(""))
        self.assertIsNone(utils.parse_timer_length("1"))
        self.assertIsNone(utils.parse_timer_length("01"))
        self.assertIsNone(utils.parse_timer_length("0:01"))
        self.assertEqual(1, utils.parse_timer_length("0:00:01"))
        self.assertEqual(1, utils.parse_timer_length("00:00:01"))
        self.assertEqual(61, utils.parse_timer_length("00:01:01"))
        self.assertEqual(3661, utils.parse_timer_length("01:01:01"))
