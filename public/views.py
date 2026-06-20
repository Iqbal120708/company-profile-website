from django.shortcuts import render

from .models import (
    HeroBanner,
    Service,
    Gallery,
    FAQ,
    About, 
    CompanyValue
)

def home(request):
    hero = HeroBanner.objects.filter(
        is_active=True
    ).first()

    services = Service.objects.filter(
        is_active=True
    )[:3]

    galleries = Gallery.objects.filter(
        is_featured=True
    )[:6]

    faqs = FAQ.objects.filter(
        is_active=True
    )

    context = {
        "hero": hero,
        "services": services,
        "galleries": galleries,
        "faqs": faqs
    }

    return render(
        request,
        "home.html",
        context
    )

def about(request):
    about = About.objects.filter(
        is_active=True
    ).first()

    company_values = CompanyValue.objects.filter(
        is_active=True
    )

    context = {
        "about": about,
        "company_values": company_values,
    }

    return render(
        request,
        "about.html",
        context
    )

def services(request):
    services = Service.objects.filter(
        is_active=True
    )

    context = {
        "services": services,
    }

    return render(
        request,
        "services.html",
        context
    )
    
def contact(request):
    return render(
        request,
        "contact.html"
    )