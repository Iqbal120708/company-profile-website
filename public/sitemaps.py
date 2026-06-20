from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """
    Sitemap untuk halaman statis (bukan dari database).
    Tambahkan nama url baru ke list `pages` kalau ada halaman baru.

    Catatan: kalau nanti ada fitur Article/blog, jangan tambahkan
    artikel ke sini. Buat sitemap class terpisah yang query dari
    model Article, supaya otomatis update tanpa edit file ini.
    """
    changefreq = "monthly"
    protocol = "https"

    pages = {
        "home": 1.0,
        "about": 0.8,
        "services": 0.8,
        "contact": 0.6,
    }

    def items(self):
        return list(self.pages.keys())

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.pages[item]
