"""Tests for PjimCRM."""
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
    """Main tests."""

    def test_auto_calculate_length(self) -> None:
        """Test the length is calculated correctly."""
        time1 = timezone.now() + datetime.timedelta(minutes=-20)
        time2 = timezone.now() + datetime.timedelta(minutes=-5)

        test_client = Client(
            name="Test",
            abn="86059194368",
            address="Test St",
            email="test@example.com",
            payment_allowance=10,
            pay_rate=10,
            payment_terms="Test Payment terms",
        )
        test_client.save()
        test_project = Project(client=test_client, name="Project Name", description="Project Description")
        test_project.save()

        # Start a timer.
        test_timesheet_entry = TimesheetEntry(
            project=test_project, timestamp_started=time1, description="Test", description_set=False, is_invoiced=False
        )
        test_timesheet_entry.save()

        self.assertEqual(
            time1,
            test_timesheet_entry.timestamp_started,
            "With a single time (running), the started time should be present.",
        )
        self.assertIsNone(test_timesheet_entry.timestamp_stopped, "When running, the stopped time should be blank.")
        self.assertEqual(
            datetime.timedelta(), test_timesheet_entry.length_raw, "When initially running, raw length should be empty."
        )
        self.assertEqual(
            datetime.timedelta(),
            test_timesheet_entry.length_rounded,
            "When initially running, rounded length should be empty.",
        )
        self.assertIsNone(
            test_timesheet_entry.timestamp_started_old, "When initially running, old time started should be empty."
        )
        self.assertIsNone(
            test_timesheet_entry.timestamp_stopped_old, "When initially running, old time stopped should be empty."
        )

        # Stop the timer fresh.
        test_timesheet_entry.timestamp_stopped = time2
        test_timesheet_entry.save()

        self.assertIsNone(test_timesheet_entry.timestamp_started, "On stopping, the started time should be cleared")
        self.assertIsNone(test_timesheet_entry.timestamp_stopped, "On stopping, the stopped time should be cleared")
        self.assertEqual(
            datetime.timedelta(minutes=15), test_timesheet_entry.length_raw, "On stopping, the raw length should be set."
        )
        self.assertEqual(
            datetime.timedelta(minutes=15),
            test_timesheet_entry.length_rounded,
            "On stopping, the rounded length should be set.",
        )
        self.assertEqual(
            time1, test_timesheet_entry.timestamp_started_old, "On stopping, the start time should be in the old fields."
        )
        self.assertEqual(
            time2, test_timesheet_entry.timestamp_stopped_old, "On stopping, the start time should be in the old fields."
        )

        # Prented to start it and stop it.
        test_timesheet_entry.timestamp_started = time1
        test_timesheet_entry.timestamp_stopped = time2
        test_timesheet_entry.save()

        self.assertIsNone(test_timesheet_entry.timestamp_started, "On stopping, the started time should be cleared")
        self.assertIsNone(test_timesheet_entry.timestamp_stopped, "On stopping, the stopped time should be cleared")
        self.assertEqual(
            datetime.timedelta(minutes=30),
            test_timesheet_entry.length_raw,
            "On stopping again, the raw length should be added.",
        )
        self.assertEqual(
            datetime.timedelta(minutes=30),
            test_timesheet_entry.length_rounded,
            "On stopping again, the rounded length should be added.",
        )
        self.assertEqual(
            time1, test_timesheet_entry.timestamp_started_old, "On stopping, the start time should be in the old fields."
        )
        self.assertEqual(
            time2, test_timesheet_entry.timestamp_stopped_old, "On stopping, the start time should be in the old fields."
        )

        # Pretend to start it and stop it. A minute should cause the rounded value to tick over.
        time1 = timezone.now() + datetime.timedelta(minutes=-6)
        time2 = timezone.now() + datetime.timedelta(minutes=-5)
        test_timesheet_entry.timestamp_started = time1
        test_timesheet_entry.timestamp_stopped = time2
        test_timesheet_entry.save()

        self.assertIsNone(test_timesheet_entry.timestamp_started, "On stopping, the started time should be cleared")
        self.assertIsNone(test_timesheet_entry.timestamp_stopped, "On stopping, the stopped time should be cleared")
        self.assertEqual(
            datetime.timedelta(minutes=31),
            test_timesheet_entry.length_raw,
            "On stopping again, the raw length should be added.",
        )
        self.assertEqual(
            datetime.timedelta(minutes=45),
            test_timesheet_entry.length_rounded,
            "On stopping again, the rounded length should be added.",
        )
        self.assertEqual(
            time1, test_timesheet_entry.timestamp_started_old, "On stopping, the start time should be in the old fields."
        )
        self.assertEqual(
            time2, test_timesheet_entry.timestamp_stopped_old, "On stopping, the start time should be in the old fields."
        )

    def test_timer_index(self) -> None:
        response = self.client.get(reverse("timer_index"))
        self.assertEqual(302, response.status_code)

        test_client = TestClient()
        test_user = User.objects.create_user("test")
        test_client.force_login(user=test_user)

        response = self.client.get(reverse("timer_index"))
        self.assertEqual(302, response.status_code)

    def test_parse_timesheet_length(self) -> None:
        self.assertIsNone(utils.parse_timer_length(""))
        self.assertIsNone(utils.parse_timer_length("1"))
        self.assertIsNone(utils.parse_timer_length("01"))
        self.assertIsNone(utils.parse_timer_length("0:01"))
        self.assertEqual(1, utils.parse_timer_length("0:00:01"))
        self.assertEqual(1, utils.parse_timer_length("00:00:01"))
        self.assertEqual(61, utils.parse_timer_length("00:01:01"))
        self.assertEqual(3661, utils.parse_timer_length("01:01:01"))
