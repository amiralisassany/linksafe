from django.utils.translation import gettext as _
from django.shortcuts import render, HttpResponse, get_object_or_404,redirect
from .forms import MakeLinkForm
from .models import Links
from django.utils import timezone

def index(request):
    return render(request, "index.html")


def make_link(request):
    if request.method == "POST":
        form = MakeLinkForm(request.POST)
        if form.is_valid():
            link = form.save()          # short_id is generated here
            return redirect("link_detail", short_id=link.short_id)
    else:
        form = MakeLinkForm()

    return render(request, "make_link.html", {"form": form})


def link_detail(request, short_id):
    link = get_object_or_404(Links, short_id=short_id)
    # {{ link }} -> uses __str__ -> domain/short_id
    # {{ link.url }} -> destination/original URL
    return render(request, "link_detail.html", {"link": link})

def redirect_link(request, short_id):
    link = get_object_or_404(Links, short_id=short_id)

    if not link.register_click():
        return render(request, "expired.html", {"link": link})

    return redirect(link.url)