from django.contrib import admin
from django.utils.html import format_html

from .models import FAQ, Gallery, HeroBanner, Service, SiteSetting, Testimonial

def image_preview(url, width=60):
    if url:
        return format_html(
            '<img src="{}" width="{}" style="border-radius:4px;" />',
            url,
            width,
        )
    return "-"

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identitas Perusahaan", {
            "fields": ("company_name", "tagline", "logo", "favicon"),
        }),
        ("Kontak", {
            "fields": ("phone", "email", "whatsapp_number", "address"),
        }),
        ("Media Sosial", {
            "fields": ("facebook_url", "instagram_url", "tiktok_url"),
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_description"),
        }),
    )
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()
        
    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change and SiteSetting.objects.exists():
            raise ValidationError("SiteSetting hanya boleh satu data.")
            
        obj.pk = 1  # enforce singleton
        super().save_model(request, obj, form, change)

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "banner_preview", "is_active", "created_at")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")
    fieldsets = (
        ("Konten Banner", {
            "fields": ("title", "subtitle", "image"),
        }),
        ("Tombol CTA", {
            "fields": ("button_text", "button_url"),
        }),
        ("Pengaturan", {
            "fields": ("is_active",),
        }),
    )

    def banner_preview(self, obj):
        return image_preview(obj.image.url if obj.image else None, width=80)

    banner_preview.short_description = "Preview"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "service_preview",
        "short_description",
        "formatted_price",
        "is_active",
        "created_at",
    )
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("name", "short_description", "description")
    fieldsets = (
        ("Paket Catering", {
            "fields": ("name", "image", "short_description", "description"),
        }),
        ("Harga", {
            "fields": ("price_start_from",),
            "description": "Harga mulai dari. Contoh: 25000.",
        }),
        ("Pengaturan", {
            "fields": ("is_active",),
        }),
    )

    def service_preview(self, obj):
        return image_preview(obj.image.url if obj.image else None)

    service_preview.short_description = "Foto"

    def formatted_price(self, obj):
        if obj.price_start_from:
            return "Rp {:,.0f}".format(obj.price_start_from)
        return "-"

    formatted_price.short_description = "Harga Mulai"
    formatted_price.admin_order_field = "price_start_from"

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "gallery_preview", "is_featured", "created_at")
    list_editable = ("is_featured",)
    list_filter = ("is_featured",)
    search_fields = ("title", "description")
    fieldsets = (
        ("Foto", {
            "fields": ("title", "image", "description"),
        }),
        ("Pengaturan", {
            "fields": ("is_featured",),
            "description": "Centang untuk menampilkan foto ini di halaman utama.",
        }),
    )

    def gallery_preview(self, obj):
        return image_preview(obj.image.url if obj.image else None, width=70)

    gallery_preview.short_description = "Preview"

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "photo_preview",
        "customer_position",
        "rating",
        "is_active",
        "created_at",
    )
    list_editable = ("is_active",)
    list_filter = ("is_active", "rating")
    search_fields = ("customer_name", "customer_position", "review")
    fieldsets = (
        ("Data Pelanggan", {
            "fields": ("customer_name", "customer_position", "photo"),
        }),
        ("Ulasan", {
            "fields": ("rating", "review"),
        }),
        ("Pengaturan", {
            "fields": ("is_active",),
        }),
    )

    def photo_preview(self, obj):
        return image_preview(obj.photo.url if obj.photo else None, width=50)

    photo_preview.short_description = "Foto"

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    ordering = ("order",)
    fieldsets = (
        ("Pertanyaan & Jawaban", {
            "fields": ("question", "answer"),
        }),
        ("Pengaturan", {
            "fields": ("order", "is_active"),
            "description": "Urutan tampil FAQ. Angka lebih kecil tampil lebih dulu.",
        }),
    )
