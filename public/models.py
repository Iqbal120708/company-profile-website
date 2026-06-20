from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\-\s]{8,20}$",
    message="Format nomor telepon tidak valid.",
)

whatsapp_validator = RegexValidator(
    regex=r"^[0-9]{10,15}$",
    message="Isi nomor WhatsApp tanpa tanda +, spasi, atau strip. Contoh: 6281234567890",
)

class BusinessDay(models.TextChoices):
    MONDAY = "MO", "Senin"
    TUESDAY = "TU", "Selasa"
    WEDNESDAY = "WE", "Rabu"
    THURSDAY = "TH", "Kamis"
    FRIDAY = "FR", "Jumat"
    SATURDAY = "SA", "Sabtu"
    SUNDAY = "SU", "Minggu"


class SiteSetting(TimeStampedModel):
    company_name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255)

    logo = models.ImageField(
        upload_to="settings/logo/",
        default="defaults/default.webp",
        help_text="Logo utama perusahaan. Disarankan gunakan gambar horizontal.",
    )
    favicon = models.ImageField(
        upload_to="settings/favicon/",
        blank=True,
        null=True,
        help_text="Ikon kecil website untuk browser tab. Gunakan gambar persegi (32x32 atau 48x48 px), format PNG atau ICO.",
    )

    phone = models.CharField(max_length=30, validators=[phone_validator])
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=30, validators=[whatsapp_validator])

    # Address terstruktur — satu-satunya sumber kebenaran untuk alamat.
    street_address = models.CharField(
        max_length=255,
        help_text="Contoh: Jl. Merdeka No. 5.",
    )
    address_locality = models.CharField(max_length=100, help_text="Kota/Kabupaten.")
    address_region = models.CharField(max_length=100, help_text="Provinsi.")
    postal_code = models.CharField(max_length=10, blank=True)
    address_country = models.CharField(max_length=2, default="ID")

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Buka Google Maps, tahan/tap lama titik lokasi sampai muncul pin merah, maka akan muncul koordinat dikotak pencarian. Angka pertama (sebelum koma) adalah latitude, isi di sini.",
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Angka kedua (setelah koma) dari hasil copy Google Maps, isi di sini sebagai longitude.",
    )

    google_business_profile_url = models.URLField(
        blank=True,
        help_text="Link listing Google Business Profile, dipakai di Schema sameAs.",
    )

    # Jam operasional terstruktur — satu jam buka/tutup berlaku untuk semua
    # hari yang dipilih di opening_days. Tidak mendukung jam berbeda per hari.
    opening_days = models.CharField(
        max_length=50,
        blank=True,
        help_text="Kode hari dipisah koma sesuai BusinessDay, contoh: MO,TU,WE,TH,FR,SA",
    )
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    seo_title = models.CharField(max_length=255)
    seo_description = models.TextField()

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Setting"

    def __str__(self):
        return self.company_name

    def clean(self):
        if not self.pk and SiteSetting.objects.exists():
            raise ValidationError(
                "SiteSetting sudah ada. Hanya satu row yang diperbolehkan, edit yang sudah ada."
            )

        if self.opening_days:
            valid_codes = set(BusinessDay.values)
            input_codes = [day.strip() for day in self.opening_days.split(",") if day.strip()]
            invalid = [code for code in input_codes if code not in valid_codes]
            if invalid:
                raise ValidationError(
                    {"opening_days": f"Kode hari tidak valid: {', '.join(invalid)}. "
                                      f"Gunakan: {', '.join(BusinessDay.values)}."}
                )

        if self.opening_days and not (self.opening_time and self.closing_time):
            raise ValidationError(
                "opening_time dan closing_time wajib diisi jika opening_days diisi."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("SiteSetting tidak boleh dihapus.")

    @classmethod
    def load(cls):
        obj = cls.objects.first()
        if obj is None:
            raise cls.DoesNotExist("SiteSetting belum diisi. Buat satu row lewat Django Admin.")
        return obj

    @property
    def full_address(self):
        parts = [self.street_address, self.address_locality, self.address_region, self.postal_code]
        return ", ".join(p for p in parts if p)

    @property
    def whatsapp_link(self):
        if not self.whatsapp_number:
            return ""
        return f"https://wa.me/{self.whatsapp_number}"

    @property
    def opening_days_list(self):
        if not self.opening_days:
            return []
        return [day.strip() for day in self.opening_days.split(",") if day.strip()]

    @property
    def operating_hours_display(self):
        """
        Generate teks jam operasional untuk ditampilkan ke pengunjung.
        Contoh hasil: "Senin - Sabtu, 08:00 - 17:00"
        Tidak menangani jam berbeda per hari atau hari libur tidak berurutan
        secara rapi (akan ditampilkan sebagai daftar nama hari, bukan rentang).
        """
        if not (self.opening_days_list and self.opening_time and self.closing_time):
            return ""

        day_labels = dict(BusinessDay.choices)
        codes = self.opening_days_list
        ordered_codes = [code for code, _ in BusinessDay.choices if code in codes]

        if self._is_contiguous(ordered_codes):
            day_text = f"{day_labels[ordered_codes[0]]} - {day_labels[ordered_codes[-1]]}"
        else:
            day_text = ", ".join(day_labels[code] for code in ordered_codes)

        time_text = f"{self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
        return f"{day_text}, {time_text}"

    @staticmethod
    def _is_contiguous(ordered_codes):
        all_codes = [code for code, _ in BusinessDay.choices]
        if not ordered_codes:
            return False
        start = all_codes.index(ordered_codes[0])
        expected = all_codes[start:start + len(ordered_codes)]
        return expected == ordered_codes

    @property
    def to_local_business_schema(self):
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": self.company_name,
            "telephone": self.phone,
            "description": self.seo_description,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": self.street_address,
                "addressLocality": self.address_locality,
                "addressRegion": self.address_region,
                "addressCountry": self.address_country,
            },
        }

        if self.postal_code:
            schema["address"]["postalCode"] = self.postal_code

        if self.email:
            schema["email"] = self.email

        if self.latitude is not None and self.longitude is not None:
            schema["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": float(self.latitude),
                "longitude": float(self.longitude),
            }

        if self.logo:
            schema["image"] = self.logo.url

        if self.opening_days_list and self.opening_time and self.closing_time:
            schema["openingHoursSpecification"] = {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": self.opening_days_list,
                "opens": self.opening_time.strftime("%H:%M"),
                "closes": self.closing_time.strftime("%H:%M"),
            }

        same_as = [
            url for url in [
                self.google_business_profile_url,
                self.facebook_url,
                self.instagram_url,
                self.tiktok_url,
            ] if url
        ]
        if same_as:
            schema["sameAs"] = same_as

        return schema


class HeroBanner(TimeStampedModel):
    title = models.CharField(max_length=255)
    subtitle = models.TextField()

    image = models.ImageField(
        upload_to="hero/",
        default="defaults/default.webp",
        help_text="Disarankan ukuran foto tidak lebih dari 200 KB (WebP lebih baik).",
    )
    
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        help_text="Deskripsi foto ini untuk aksesibilitas dan SEO, contoh: Hidangan nasi kotak Dapur Nusantara Catering. Kosongkan untuk pakai nama bisnis sebagai fallback.",
    )

    # button_text = models.CharField(
    #     max_length=100,
    #     help_text="Teks tombol CTA (contoh: Pesan Sekarang, Hubungi Kami)",
    # )
    # button_url = models.URLField(
    #     max_length=255,
    #     help_text="Link tujuan tombol CTA (contoh: https://wa.me/628xxx atau https://domain.com/page)",
    # )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Service(TimeStampedModel):
    title = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    description = models.TextField()

    image = models.ImageField(
        upload_to="services/",
        default="defaults/default.webp",
        help_text="Disarankan ukuran foto tidak lebih dari 100 KB (WebP lebih baik). Gunakan gambar kotak (1:1) atau landscape ringan (4:3).",
    )
    
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        help_text="Deskripsi foto ini. Kosongkan jika foto memang persis menggambarkan nama layanan (otomatis pakai judul layanan).",
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Gallery(TimeStampedModel):
    title = models.CharField(max_length=255)

    image = models.ImageField(
        upload_to="gallery/",
        default="defaults/default.webp",
        help_text="Disarankan ukuran foto tidak lebih dari 100 KB (WebP lebih baik).",
    )
    
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        help_text="Deskripsi foto ini. Kosongkan jika foto memang persis menggambarkan nama layanan (otomatis pakai judul layanan).",
    )

    description = models.TextField(blank=True)

    is_featured = models.BooleanField(
        default=False,
        help_text="Centang jika gambar ini ingin ditampilkan sebagai unggulan di halaman utama (home page).",
    )

    def __str__(self):
        return self.title


class FAQ(TimeStampedModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question


class About(TimeStampedModel):
    description = models.TextField()
    vision = models.TextField()
    mission = models.TextField()

    image = models.ImageField(
        upload_to="about/",
        default="defaults/default.webp",
        help_text="Disarankan ukuran foto tidak lebih dari 200 KB (WebP lebih baik).",
    )
    
    about_image_alt = models.CharField(
        max_length=255,
        blank=True,
        help_text="Deskripsi singkat foto ini, contoh: Tim dapur menyiapkan hidangan catering. Untuk aksesibilitas dan SEO gambar.",
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.about_image_alt


class CompanyValue(TimeStampedModel):
    title = models.CharField(max_length=100)
    description = models.TextField()

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title