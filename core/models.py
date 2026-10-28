from django.db import models

IMAGE_URL_HELP = "Or paste an image link (e.g. from Unsplash). An uploaded image takes priority."


def pick_image(upload, url, fallback=""):
    """Return the uploaded file URL if present, otherwise the external URL."""
    if upload:
        try:
            return upload.url
        except ValueError:
            pass
    return url or fallback


class SingletonModel(models.Model):
    """A model that only ever has one row (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    # Brand
    site_name = models.CharField(max_length=100, default="Crystal Bay Estates")
    tagline = models.CharField(max_length=200, default="Luxury Real Estate in South Florida")
    logo = models.ImageField(upload_to="brand/", blank=True, help_text="Optional. If empty, the site name is shown as a text logo.")
    favicon = models.ImageField(upload_to="brand/", blank=True)
    primary_color = models.CharField(max_length=7, default="#0E2A47", help_text="Main dark color (hex), e.g. #0E2A47")
    accent_color = models.CharField(max_length=7, default="#12A4B0", help_text="Highlight color for buttons & links (hex)")
    meta_description = models.CharField(max_length=300, blank=True)

    # Contact
    phone = models.CharField(max_length=50, default="(305) 555-0187")
    email = models.EmailField(default="hello@crystalbayestates.com")
    address = models.CharField(max_length=255, default="1200 Brickell Bay Drive, Suite 1800, Miami, FL 33131")
    office_hours = models.CharField(max_length=120, default="Mon – Sat: 9:00 AM – 7:00 PM")
    map_embed_url = models.URLField(max_length=1000, blank=True, help_text="Google Maps embed URL for the contact page")

    # Social
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True, verbose_name="X / Twitter")
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    # Header
    topbar_text = models.CharField(max_length=200, blank=True, default="Award-winning brokerage serving Miami, Fort Lauderdale, Tampa & Fort Myers")
    header_button_text = models.CharField(max_length=40, default="List Your Property")
    header_button_link = models.CharField(max_length=200, default="/contact/")

    # Hero
    hero_badge = models.CharField(max_length=100, default="South Florida's Trusted Luxury Brokerage")
    hero_title = models.CharField(max_length=200, default="Find a Home That Reflects the Life You Want")
    hero_subtitle = models.TextField(default="Waterfront villas, sky-high penthouses and family homes — hand-picked by local experts.")

    # Home sections (title / subtitle / visibility)
    featured_title = models.CharField(max_length=150, default="Discover Our Featured Properties")
    featured_subtitle = models.CharField(max_length=300, blank=True)
    show_featured = models.BooleanField(default=True)

    features_title = models.CharField(max_length=150, default="Why Clients Choose Crystal Bay")
    features_subtitle = models.CharField(max_length=300, blank=True)
    show_features = models.BooleanField(default=True)

    latest_title = models.CharField(max_length=150, default="Recently Listed")
    latest_subtitle = models.CharField(max_length=300, blank=True)
    show_latest = models.BooleanField(default=True)

    types_title = models.CharField(max_length=150, default="Discover Different Lifestyles")
    types_subtitle = models.CharField(max_length=300, blank=True)
    show_types = models.BooleanField(default=True)

    cities_title = models.CharField(max_length=150, default="Explore Cities in South Florida")
    cities_subtitle = models.CharField(max_length=300, blank=True)
    show_cities = models.BooleanField(default=True)

    pricing_title = models.CharField(max_length=150, default="Join Us to List Your Properties")
    pricing_subtitle = models.CharField(max_length=300, blank=True)
    show_pricing = models.BooleanField(default=True)

    testimonials_title = models.CharField(max_length=150, default="What Our Clients Say")
    testimonials_subtitle = models.CharField(max_length=300, blank=True)
    show_testimonials = models.BooleanField(default=True)

    agents_title = models.CharField(max_length=150, default="Meet Our Agents")
    agents_subtitle = models.CharField(max_length=300, blank=True)
    show_agents = models.BooleanField(default=True)

    blog_title = models.CharField(max_length=150, default="Market Insights & News")
    blog_subtitle = models.CharField(max_length=300, blank=True)
    show_blog = models.BooleanField(default=True)

    # Call-to-action band
    cta_title = models.CharField(max_length=150, default="Thinking of Selling Your Home?")
    cta_text = models.TextField(blank=True)
    cta_button_text = models.CharField(max_length=40, default="Get a Free Valuation")
    cta_button_link = models.CharField(max_length=200, default="/contact/")
    cta_image = models.ImageField(upload_to="sections/", blank=True)
    cta_image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    show_cta = models.BooleanField(default=True)

    # Contact section
    contact_title = models.CharField(max_length=150, default="Get in Touch")
    contact_subtitle = models.CharField(max_length=300, blank=True)
    contact_image = models.ImageField(upload_to="sections/", blank=True)
    contact_image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    show_contact = models.BooleanField(default=True)

    # Footer
    footer_about = models.TextField(blank=True)
    copyright_text = models.CharField(max_length=200, default="© Crystal Bay Estates. All rights reserved.")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @property
    def cta_img(self):
        return pick_image(self.cta_image, self.cta_image_url)

    @property
    def contact_img(self):
        return pick_image(self.contact_image, self.contact_image_url)


class HeroSlide(models.Model):
    image = models.ImageField(upload_to="hero/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    caption = models.CharField(max_length=120, blank=True, help_text="Small caption shown on the slide (optional)")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Hero Slide"

    def __str__(self):
        return self.caption or f"Slide #{self.pk}"

    @property
    def img(self):
        return pick_image(self.image, self.image_url)


class PageHeader(models.Model):
    PAGE_CHOICES = [
        ("properties", "Properties"),
        ("agents", "Agents"),
        ("about", "About"),
        ("blog", "Blog"),
        ("contact", "Contact"),
        ("favorites", "Favorites"),
    ]
    page = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to="headers/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)

    class Meta:
        verbose_name = "Page Banner"

    def __str__(self):
        return self.get_page_display()

    @property
    def img(self):
        return pick_image(self.image, self.image_url)


class Feature(models.Model):
    icon = models.CharField(max_length=60, default="bi-house-heart", help_text="Bootstrap icon class, e.g. bi-house-heart (see icons.getbootstrap.com)")
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Why-Us Feature"

    def __str__(self):
        return self.title


class Stat(models.Model):
    value = models.PositiveIntegerField()
    suffix = models.CharField(max_length=10, blank=True, help_text="e.g. +, %, B")
    prefix = models.CharField(max_length=10, blank=True, help_text="e.g. $")
    label = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.prefix}{self.value}{self.suffix} {self.label}"


class PricingPlan(models.Model):
    name = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=30, default="per month")
    description = models.CharField(max_length=200, blank=True)
    features = models.TextField(help_text="One feature per line")
    is_popular = models.BooleanField(default=False, help_text="Highlight this plan")
    button_text = models.CharField(max_length=40, default="Get Started")
    button_link = models.CharField(max_length=200, default="/contact/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Pricing Plan"

    def __str__(self):
        return self.name

    @property
    def feature_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, help_text="e.g. Bought a villa in Miami")
    photo = models.ImageField(upload_to="testimonials/", blank=True)
    photo_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5, choices=[(i, f"{i} stars") for i in range(1, 6)])
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    @property
    def img(self):
        return pick_image(self.photo, self.photo_url)


class AboutPage(SingletonModel):
    intro_eyebrow = models.CharField(max_length=80, default="About Crystal Bay")
    intro_title = models.CharField(max_length=200, default="Two Decades of Opening Doors Across South Florida")
    intro_text = models.TextField(blank=True)
    intro_image = models.ImageField(upload_to="about/", blank=True)
    intro_image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    second_image = models.ImageField(upload_to="about/", blank=True)
    second_image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    years_experience = models.PositiveIntegerField(default=20)

    mission_title = models.CharField(max_length=100, default="Our Mission")
    mission_text = models.TextField(blank=True)
    vision_title = models.CharField(max_length=100, default="Our Vision")
    vision_text = models.TextField(blank=True)
    values_title = models.CharField(max_length=100, default="Our Promise")
    values_text = models.TextField(blank=True)

    show_team = models.BooleanField(default=True)
    show_testimonials = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return "About Page"

    @property
    def intro_img(self):
        return pick_image(self.intro_image, self.intro_image_url)

    @property
    def second_img(self):
        return pick_image(self.second_image, self.second_image_url)


class Popup(models.Model):
    FREQUENCY_CHOICES = [
        ("always", "Every page load"),
        ("session", "Once per browser session"),
        ("day", "Once per day"),
        ("week", "Once per week"),
    ]
    PAGE_CHOICES = [("all", "All pages"), ("home", "Home page only")]

    name = models.CharField(max_length=100, help_text="Internal name (not shown to visitors)")
    is_active = models.BooleanField(default=True, help_text="Only the most recently updated active popup is shown")
    eyebrow = models.CharField(max_length=80, blank=True)
    title = models.CharField(max_length=150)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="popups/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text=IMAGE_URL_HELP)
    show_form = models.BooleanField(default=True, help_text="Show a name / email / phone form inside the popup")
    form_button_text = models.CharField(max_length=40, default="Send Me Listings")
    button_text = models.CharField(max_length=40, blank=True, help_text="Used when the form is hidden")
    button_link = models.CharField(max_length=200, blank=True)
    note = models.CharField(max_length=150, blank=True, help_text="Small print under the form")
    delay_seconds = models.PositiveIntegerField(default=4)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="session")
    pages = models.CharField(max_length=10, choices=PAGE_CHOICES, default="all")
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated"]

    def __str__(self):
        return self.name

    @property
    def img(self):
        return pick_image(self.image, self.image_url)


class ContactMessage(models.Model):
    SOURCE_CHOICES = [
        ("contact", "Contact form"),
        ("property", "Property inquiry"),
        ("agent", "Agent contact"),
        ("home", "Home page form"),
        ("popup", "Popup"),
    ]
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="contact")
    property = models.ForeignKey("properties.Property", null=True, blank=True, on_delete=models.SET_NULL, related_name="inquiries")
    agent = models.ForeignKey("properties.Agent", null=True, blank=True, on_delete=models.SET_NULL, related_name="messages")
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Message / Lead"
        verbose_name_plural = "Messages & Leads"

    def __str__(self):
        return f"{self.name} — {self.get_source_display()}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Newsletter Subscriber"

    def __str__(self):
        return self.email
