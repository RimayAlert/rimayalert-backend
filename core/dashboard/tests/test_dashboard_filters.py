from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.dashboard.templatetags.dashboard_filters import timesince_short, incident_type_icon


class DashboardFiltersTests(TestCase):
    def test_timesince_short_none_or_recent(self):
        self.assertEqual(timesince_short(None), "")
        now = timezone.now()
        self.assertEqual(timesince_short(now), "Justo ahora")

        future = now + timedelta(minutes=5)
        self.assertEqual(timesince_short(future), "Justo ahora")

    def test_timesince_short_minutes_hours_days_weeks_months(self):
        now = timezone.now()

        five_min_ago = now - timedelta(minutes=5)
        self.assertEqual(timesince_short(five_min_ago), "Hace 5 min")
        two_hours_ago = now - timedelta(hours=2)
        self.assertEqual(timesince_short(two_hours_ago), "Hace 2 horas")
        three_days_ago = now - timedelta(days=3)
        self.assertEqual(timesince_short(three_days_ago), "Hace 3 días")
        two_weeks_ago = now - timedelta(weeks=2)
        self.assertEqual(timesince_short(two_weeks_ago), "Hace 2 semanas")
        two_months_ago = now - timedelta(days=65)
        self.assertEqual(timesince_short(two_months_ago), "Hace 2 meses")

    def test_incident_type_icon_none_and_with_icon(self):
        class Dummy:
            pass

        self.assertEqual(incident_type_icon(None), "fas fa-exclamation-circle")

        d = Dummy()
        self.assertEqual(incident_type_icon(d), "fas fa-exclamation-triangle")
        d2 = Dummy()
        d2.icon = ''
        self.assertEqual(incident_type_icon(d2), "fas fa-exclamation-triangle")
        d3 = Dummy()
        d3.icon = 'custom-icon-class'
        self.assertEqual(incident_type_icon(d3), 'custom-icon-class')

