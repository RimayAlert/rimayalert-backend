from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.dashboard.views.dashboard.dashboard import DashboardView
from core.incident.models.incident.incident import Incident
from core.incident.models.incident_type.incident_type import IncidentType
from core.incident.models.incident_status.incident_status import IncidentStatus
from core.authentication.models.user.user import User


class DashboardViewTests(TestCase):
    def setUp(self):
        # create supporting objects
        self.user = User.objects.create(username='u1', email='u1@example.com', dni='111', first_name='A', last_name='B')
        self.inc_type = IncidentType.objects.create(name='Tipo1')
        self.inc_status = IncidentStatus.objects.create(name='Estado1', code='E1')

        now = timezone.now()

        # create incidents without trying to set auto_now_add field
        self.i1 = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.inc_type,
            incident_status=self.inc_status,
            title='Inc 1',
            description='desc',
            is_active=True,
        )

        self.i2 = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.inc_type,
            incident_status=self.inc_status,
            title='Inc 2',
            description='desc',
            is_active=True,
        )

        self.i3 = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.inc_type,
            incident_status=self.inc_status,
            title='Inc 3',
            description='desc',
            is_active=False,
        )

        # update reported_at afterwards (update bypasses auto_now_add)
        Incident.objects.filter(pk=self.i1.pk).update(reported_at=now - timedelta(minutes=1))
        Incident.objects.filter(pk=self.i2.pk).update(reported_at=now - timedelta(days=1))
        Incident.objects.filter(pk=self.i3.pk).update(reported_at=now - timedelta(hours=1))

    def test_get_context_data_contains_title_and_recent_incidents(self):
        view = DashboardView()
        ctx = view.get_context_data()

        self.assertIn('title', ctx)
        self.assertEqual(ctx['title'], 'Dashboard')

        self.assertIn('recent_incidents', ctx)
        recent = list(ctx['recent_incidents'])

        # should only include active incidents
        self.assertTrue(all(i.is_active for i in recent))

        # should contain the created active incidents
        titles = [i.title for i in recent]
        self.assertIn('Inc 1', titles)
        self.assertIn('Inc 2', titles)

        # ensure the list is ordered by reported_at descending
        reported_times = [i.reported_at for i in recent]
        self.assertEqual(reported_times, sorted(reported_times, reverse=True))

    def test_recent_incidents_limited_to_five(self):
        # create 5 more active incidents to exceed the slice of 5
        now = timezone.now()
        created = []
        for n in range(3, 10):
            obj = Incident.objects.create(
                reported_by_user=self.user,
                incident_type=self.inc_type,
                incident_status=self.inc_status,
                title=f'Inc {n}',
                description='desc',
                is_active=True,
            )
            created.append((obj.pk, now - timedelta(minutes=n)))

        # update reported_at on the newly created incidents
        for pk, dt in created:
            Incident.objects.filter(pk=pk).update(reported_at=dt)

        view = DashboardView()
        ctx = view.get_context_data()
        recent = list(ctx['recent_incidents'])
        # should be at most 5
        self.assertLessEqual(len(recent), 5)
