from django.db import models
from django.utils.text import slugify

# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSetting(TimeStampedModel):
    company_name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255)

    logo = models.ImageField(upload_to="settings/logo/", help_text="Logo utama perusahaan. Disarankan gunakan gambar horizontal.")
    favicon = models.ImageField(
        upload_to="settings/favicon/",
        blank=True,
        null=True,
        help_text="Ikon kecil website untuk browser tab. Gunakan gambar persegi (32x32 atau 48x48 px), format PNG atau ICO.",
    )

    phone = models.CharField(max_length=30)
    email = models.EmailField()

    address = models.TextField()

    whatsapp_number = models.CharField(max_length=30)

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    seo_title = models.CharField(max_length=255)
    seo_description = models.TextField()

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name
        
class HeroBanner(TimeStampedModel):
    title = models.CharField(max_length=255)
    subtitle = models.TextField()

    image = models.ImageField(
        upload_to="hero/",
    )

    button_text = models.CharField(
        max_length=100
    )

    button_url = models.CharField(
        max_length=255
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.title
        
class Service(TimeStampedModel):
    name = models.CharField(max_length=255)

    short_description = models.CharField(
        max_length=255
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to="services/",
        help_text="Gunakan gambar kotak (1:1) atau landscape ringan (4:3). Tampilkan makanan atau packaging layanan."
    )

    price_start_from = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name
        
class Gallery(TimeStampedModel):
    title = models.CharField(
        max_length=255
    )

    image = models.ImageField(
        upload_to="gallery/"
    )

    description = models.TextField(
        blank=True
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Centang jika gambar ini ingin ditampilkan sebagai unggulan di halaman utama (home page)."
    )

    def __str__(self):
        return self.title
        
class Testimonial(TimeStampedModel):
    customer_name = models.CharField(
        max_length=255
    )

    customer_position = models.CharField(
        max_length=255,
        blank=True
    )

    photo = models.ImageField(
        upload_to="testimonials/",
        blank=True,
        null=True
    )

    rating = models.PositiveSmallIntegerField(
        default=5
    )

    review = models.TextField()

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.customer_name
        
class FAQ(TimeStampedModel):
    question = models.CharField(
        max_length=255
    )

    answer = models.TextField()

    order = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question
        