import builtins
from urllib.parse import quote_plus

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import IMAGE_URL_HELP, pick_image


def unique_slug(instance, value, field="slug"):
    base = slugify(value)[:200] or "item"
    slug, n = base, 2
    model = type(instance)
    while model.objects.filter(**{field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


class SlugMixin(models.Model):
    slug_source = "name"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, getattr(self, self.slug_source))
        super().save(*args, **kwargs)


class City(SlugMixin):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    state = models.CharField(max_length=60, default="Florida")
    image = models.ImageField(upload_to="cities/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name

    @property
    def img(self):
        return pick_image(self.image, self.image_url)

    def get_absolute_url(self):
        return reverse("properties:list") + f"?city={self.slug}"


class PropertyType(SlugMixin):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=60, default="bi-house", help_text="Bootstrap icon class")
    image = models.ImageField(upload_to="types/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Property Type"

    def __str__(self):
        return self.name

    @property
    def img(self):
        return pick_image(self.image, self.image_url)

    def get_absolute_url(self):
        return reverse("properties:list") + f"?type={self.slug}"


class Label(SlugMixin):
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    color = models.CharField(max_length=7, default="#E8A33D", help_text="Badge color (hex)")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("properties:list") + f"?label={self.slug}"


class Amenity(models.Model):
    name = models.CharField(max_length=80, unique=True)
    icon = models.CharField(max_length=60, default="bi-check2-circle", help_text="Bootstrap icon class")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name


class Agent(SlugMixin):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    title = models.CharField(max_length=120, default="Real Estate Advisor")
    photo = models.ImageField(upload_to="agents/", blank=True)
    photo_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    bio = models.TextField(blank=True)
    languages = models.CharField(max_length=120, blank=True, help_text="e.g. English, Spanish")
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def img(self):
        return pick_image(self.photo, self.photo_url)

    def get_absolute_url(self):
        return reverse("properties:agent_detail", args=[self.slug])


class PropertyQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Property(SlugMixin):
    STATUS_SALE = "sale"
    STATUS_RENT = "rent"
    STATUS_CHOICES = [(STATUS_SALE, "For Sale"), (STATUS_RENT, "For Rent")]

    slug_source = "title"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_SALE)
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, blank=True, related_name="properties")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="properties")
    label = models.ForeignKey(Label, on_delete=models.SET_NULL, null=True, blank=True, related_name="properties")
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="properties")

    price = models.DecimalField(max_digits=14, decimal_places=0)
    price_suffix = models.CharField(max_length=20, blank=True, help_text="e.g. /mo for rentals")
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20, blank=True)

    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    garages = models.PositiveSmallIntegerField(default=0)
    area = models.PositiveIntegerField(help_text="Living area in sq ft")
    lot_size = models.PositiveIntegerField(null=True, blank=True, help_text="Lot size in sq ft")
    year_built = models.PositiveSmallIntegerField(null=True, blank=True)

    excerpt = models.CharField(max_length=300, blank=True, help_text="Short summary for cards & SEO")
    description = models.TextField()
    amenities = models.ManyToManyField(Amenity, blank=True, related_name="properties")

    image = models.ImageField(upload_to="properties/", blank=True, verbose_name="Main image")
    image_url = models.URLField(max_length=500, blank=True, verbose_name="Main image link", help_text=IMAGE_URL_HELP)
    video_url = models.URLField(blank=True, help_text="YouTube embed link (optional), e.g. https://www.youtube.com/embed/xxxx")

    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = PropertyQuerySet.as_manager()

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("properties:detail", args=[self.slug])

    @property
    def img(self):
        return pick_image(self.image, self.image_url)

    @property
    def is_rent(self):
        return self.status == self.STATUS_RENT

    @property
    def price_per_sqft(self):
        if self.area and not self.is_rent:
            return round(self.price / self.area)
        return None

    @property
    def baths_display(self):
        return int(self.bathrooms) if self.bathrooms == int(self.bathrooms) else self.bathrooms

    @property
    def full_address(self):
        parts = [self.address]
        if self.city:
            parts.append(f"{self.city.name}, FL")
        if self.zip_code:
            parts.append(self.zip_code)
        return ", ".join(parts)

    @property
    def map_embed_url(self):
        return f"https://maps.google.com/maps?q={quote_plus(self.full_address)}&z=14&output=embed"

    @property
    def gallery(self):
        images = [self.img] if self.img else []
        images += [g.img for g in self.images.all() if g.img]
        return images


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="properties/gallery/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Gallery image"

    def __str__(self):
        return f"Image for {self.property}"

    @builtins.property
    def img(self):
        return pick_image(self.image, self.image_url)
