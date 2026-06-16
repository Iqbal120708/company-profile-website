from .models import SiteSetting

def site_settings(request):
    site = SiteSetting.objects.first()
    return {
        "site": site
    }