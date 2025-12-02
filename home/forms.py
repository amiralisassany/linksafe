# app/forms.py
from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Links


class MakeLinkForm(forms.ModelForm):
    expire_days = forms.IntegerField(
        required=False,
        min_value=1,
        label="Expire after days",
    )

    expire_clicks = forms.IntegerField(
        required=False,
        min_value=1,
        label="Expire after clicks",
    )

    class Meta:
        model = Links
        fields = ["title", "url"]  # url = original/destination URL

    def clean(self):
        cleaned = super().clean()

        expire_days = cleaned.get("expire_days")
        expire_clicks = cleaned.get("expire_clicks")

        if expire_days:
            cleaned["expire_at"] = timezone.now() + timedelta(days=expire_days)
        else:
            cleaned["expire_at"] = None

        cleaned["max_clicks"] = expire_clicks or None
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.expire_at = self.cleaned_data.get("expire_at")
        instance.max_clicks = self.cleaned_data.get("max_clicks")

        if commit:
            instance.save()
        return instance
