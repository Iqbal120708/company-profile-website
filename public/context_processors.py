from .models import SiteSetting


def site(request):
    """
    Tambahkan ke TEMPLATES[0]['OPTIONS']['context_processors'] di settings.py
    supaya {{ site }} tersedia di semua template.

    Contoh pakai di template:
        {{ site.company_name }}
        {{ site.full_address }}
        {{ site.operating_hours_display }}
        <a href="{{ site.whatsapp_link }}">WhatsApp</a>
    """
    try:
        site_setting = SiteSetting.load()
    except SiteSetting.DoesNotExist:
        site_setting = None

    return {"site": site_setting}
