from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('make-link/', views.make_link, name='make_link'),
    path('make-link/', views.make_link, name='make_link'),
    # detail page (what you show after creating a link)
    path("link/<str:short_id>/", views.link_detail, name="link_detail"),

    # the actual redirect URL (what you share)
    path("<str:short_id>/", views.redirect_link, name="redirect_link"),
    # or "r/<str:short_id>/" if you want a prefix
]
