import secrets
from django.test import TestCase
from django.db import IntegrityError

from core.authentication.models import User
from core.stats.models.user_stats.user_stats import UserStats


class TestUserStats(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=secrets.token_urlsafe(32),
            dni='1234567890'
        )

    def test_user_stats_string_representation(self):
        user_stats = UserStats.objects.create(
            user=self.user,
            total_alerts=5,
            total_alerts_resolved=3,
            total_alerts_pending=2
        )
        self.assertEqual(str(user_stats), "Stats for testuser")

    def test_user_stats_default_values(self):
        user_stats = UserStats.objects.create(user=self.user)
        self.assertEqual(user_stats.total_alerts, 0)
        self.assertEqual(user_stats.total_alerts_resolved, 0)
        self.assertEqual(user_stats.total_alerts_pending, 0)

    def test_user_stats_custom_values(self):
        user_stats = UserStats.objects.create(
            user=self.user,
            total_alerts=10,
            total_alerts_resolved=7,
            total_alerts_pending=3
        )
        self.assertEqual(user_stats.total_alerts, 10)
        self.assertEqual(user_stats.total_alerts_resolved, 7)
        self.assertEqual(user_stats.total_alerts_pending, 3)

    def test_user_stats_one_to_one_relationship(self):
        UserStats.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            UserStats.objects.create(user=self.user)

    def test_user_stats_string_representation_with_special_characters(self):
        user = User.objects.create_user(
            username='test_user_123',
            email='test123@example.com',
            password=secrets.token_urlsafe(32),
            dni='9876543210'
        )
        user_stats = UserStats.objects.create(
            user=user,
            total_alerts=8,
            total_alerts_resolved=5,
            total_alerts_pending=3
        )
        self.assertEqual(str(user_stats), "Stats for test_user_123")

    def test_user_stats_deletion_cascades_when_user_deleted(self):
        user = User.objects.create_user(
            username='deleteuser',
            email='delete@example.com',
            password=secrets.token_urlsafe(32),
            dni='1111111111'
        )
        user_stats = UserStats.objects.create(user=user)
        user_stats_id = user_stats.id
        user.delete()
        self.assertFalse(UserStats.objects.filter(id=user_stats_id).exists())

    def test_user_stats_can_update_alert_counts(self):
        user_stats = UserStats.objects.create(
            user=self.user,
            total_alerts=5,
            total_alerts_resolved=3,
            total_alerts_pending=2
        )
        user_stats.total_alerts = 10
        user_stats.total_alerts_resolved = 6
        user_stats.total_alerts_pending = 4
        user_stats.save()

        updated_stats = UserStats.objects.get(user=self.user)
        self.assertEqual(updated_stats.total_alerts, 10)
        self.assertEqual(updated_stats.total_alerts_resolved, 6)
        self.assertEqual(updated_stats.total_alerts_pending, 4)

    def test_user_stats_meta_verbose_name(self):
        self.assertEqual(UserStats._meta.verbose_name, "User Stats")
        self.assertEqual(UserStats._meta.verbose_name_plural, "User Stats")

    def test_user_stats_positive_integer_field_accepts_zero(self):
        user_stats = UserStats.objects.create(
            user=self.user,
            total_alerts=0,
            total_alerts_resolved=0,
            total_alerts_pending=0
        )
        self.assertEqual(user_stats.total_alerts, 0)
        self.assertEqual(user_stats.total_alerts_resolved, 0)
        self.assertEqual(user_stats.total_alerts_pending, 0)

    def test_user_stats_positive_integer_field_accepts_large_values(self):
        user_stats = UserStats.objects.create(
            user=self.user,
            total_alerts=999999,
            total_alerts_resolved=500000,
            total_alerts_pending=499999
        )
        self.assertEqual(user_stats.total_alerts, 999999)
        self.assertEqual(user_stats.total_alerts_resolved, 500000)
        self.assertEqual(user_stats.total_alerts_pending, 499999)

    def test_user_stats_can_retrieve_user_from_stats(self):
        user_stats = UserStats.objects.create(
            user=self.user,
            total_alerts=5,
            total_alerts_resolved=3,
            total_alerts_pending=2
        )
        self.assertEqual(user_stats.user, self.user)
        self.assertEqual(user_stats.user.username, 'testuser')

    def test_user_stats_can_access_stats_from_user(self):
        user_stats = UserStats.objects.create(
            user=self.user,
            total_alerts=5,
            total_alerts_resolved=3,
            total_alerts_pending=2
        )
        self.assertEqual(self.user.u_stats_by_user, user_stats)
        self.assertEqual(self.user.u_stats_by_user.total_alerts, 5)

