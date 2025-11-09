from django.db import models

from core.authentication.models import User
from core.community.models.community.community import Community


class CommunityMembership(models.Model):
    ROLE_CHOICES = [
        ("member", "Miembro"),
        ("moderator", "Moderador"),
        ("admin", "Administrador"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="c_memberships_by_user",
        verbose_name="Perfil de usuario",
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="Comunidad",
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="member", verbose_name="Rol")
    is_verified = models.BooleanField(default=False, verbose_name="Verificado")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de unión")

    class Meta:
        db_table = "community_membership"
        verbose_name = "Membresía de comunidad"
        verbose_name_plural = "Membresías de comunidades"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "community"],
                name="unique_user_community_membership",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.community} ({self.role})"
