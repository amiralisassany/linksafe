import uuid
import base64
from django.conf import settings
from django.db import models, IntegrityError
from django.utils import timezone


class Links(models.Model):
    title = models.CharField(max_length=200, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    short_id = models.CharField(
        max_length=6,
        unique=True,
        editable=False,
        blank=True,
    )
    url = models.URLField(max_length=500)
    expire_at = models.DateTimeField(blank=True, null=True)
    max_clicks = models.PositiveIntegerField(blank=True, null=True)
    clicks = models.PositiveIntegerField(default=0)

    @classmethod
    def _generate_candidate(cls) -> str:
        """Generate a 6-char ID derived from a UUID."""
        raw = base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b"=").decode("utf-8")
        return raw[:6]  # change to [:4] if you want 4 chars

    @classmethod
    def _generate_unique_short_id(cls) -> str:
        """Generate a short_id that does not exist in the DB."""
        while True:
            candidate = cls._generate_candidate()
            if not cls.objects.filter(short_id=candidate).exists():
                return candidate

    def save(self, *args, **kwargs):
        """
        On save:
        - If short_id is empty → generate one
        - Ensure uniqueness in Python
        - Also rely on DB unique constraint and retry on rare race-condition collisions
        """
        if not self.short_id:
            # Try a few times in case of race-condition IntegrityError
            for _ in range(5):
                self.short_id = type(self)._generate_unique_short_id()
                try:
                    return super().save(*args, **kwargs)
                except IntegrityError:
                    # Collision slipped in between exists() check and save()
                    # Clear and try again
                    self.short_id = None
            # If we get here, something is really off
            raise RuntimeError(
                "Could not generate a unique short_id after several attempts"
            )

        # If short_id already set (e.g. existing row), just save
        return super().save(*args, **kwargs)

    # ---------- expiry / limit helpers ----------

    def has_time_limit(self) -> bool:
        """Return True if this link has a time-based expiry configured."""
        return self.expire_at is not None

    def has_click_limit(self) -> bool:
        """Return True if this link has a click-based limit configured."""
        return self.max_clicks is not None

    def is_expired(self) -> bool:
        """
        Check if this link is expired based on time or clicks.
        Safe to call from views; doesn't mutate state.
        """
        # time-based
        if self.expire_at and timezone.now() >= self.expire_at:
            return True
        # click-based
        if self.max_clicks is not None and self.clicks >= self.max_clicks:
            return True
        return False

    def register_click(self, save: bool = True) -> bool:
        """
        Increment clicks if not expired yet.

        Returns:
            bool: True if the click was counted and redirect is allowed,
                  False if the link is already expired (no increment).
        """
        if self.is_expired():
            return False

        self.clicks += 1
        if save:
            # Only update the clicks field for efficiency
            self.save(update_fields=["clicks"])
        return True

    def __str__(self):
        """
        Return a shareable URL like 'example.com/abc123'.

        Uses ALLOWED_HOSTS[0] when available, but falls back to a safe default
        so it doesn't blow up in development when ALLOWED_HOSTS is empty.
        """
        hosts = getattr(settings, "ALLOWED_HOSTS", [])
        if hosts:
            host = hosts[0]
        else:
            host = "localhost"

        sid = self.short_id or ""
        return f"{host}/{sid}"
