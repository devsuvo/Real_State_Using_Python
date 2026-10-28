"""
Describes every model the dashboard manages: how it is listed, searched,
filtered and which form sections it has. Views and templates are generic and
driven entirely by these definitions.
"""
from dataclasses import dataclass, field

from django.utils.html import format_html
from django.utils.text import Truncator

from blog.models import Category, Post
from core.models import (
    AboutPage, ContactMessage, Feature, HeroSlide, PageHeader, Popup,
    PricingPlan, SiteSettings, Stat, Subscriber, Testimonial,
)
from properties.models import Agent, Amenity, City, Label, Property, PropertyType


# ---------------------------------------------------------------- columns
@dataclass
class Column:
    name: str
    label: str = ""
    kind: str = "text"  # text | title | image | avatar | bool | money | date | badge | color | icon | count
    sortable: bool = False

    def value(self, obj):
        value = obj
        for part in self.name.split("."):
            value = getattr(value, part, None) if value is not None else None
            if callable(value) and not hasattr(value, "all"):
                value = value()
        return value

    def render(self, obj):
        v = self.value(obj)
        k = self.kind
        if k in ("image", "avatar"):
            if not v:
                return format_html('<span class="cell-thumb is-empty"><i class="bi bi-image"></i></span>')
            src = v + ("&w=160&h=120&fit=crop&q=60" if "unsplash" in v else "")
            return format_html('<img class="cell-thumb{}" src="{}" alt="" loading="lazy">', " is-round" if k == "avatar" else "", src)
        if k == "bool":
            icon, cls = ("bi-check-circle-fill", "is-on") if v else ("bi-dash-circle", "is-off")
            return format_html('<span class="cell-bool {}"><i class="bi {}"></i></span>', cls, icon)
        if k == "money":
            return format_html('<span class="cell-money">${}{}</span>', f"{v:,.0f}" if v is not None else "—", getattr(obj, "price_suffix", ""))
        if k == "date":
            return format_html('<span class="cell-muted">{}</span>', v.strftime("%b %d, %Y") if v else "—")
        if k == "badge":
            return format_html('<span class="cell-badge">{}</span>', v) if v else "—"
        if k == "color":
            return format_html('<span class="cell-color" style="background:{}"></span>{}', v, v)
        if k == "icon":
            return format_html('<span class="cell-icon"><i class="bi {}"></i></span>', v)
        if k == "title":
            return format_html('<strong class="cell-title">{}</strong>', Truncator(str(v)).chars(60))
        if v is None or v == "":
            return "—"
        if hasattr(v, "all"):
            return ", ".join(str(x) for x in v.all()) or "—"
        return Truncator(str(v)).chars(70)


def C(name, label=None, kind="text", sortable=False):
    if label is None:
        label = name.split(".")[0].replace("_", " ").capitalize()
    return Column(name, label, kind, sortable)


# ---------------------------------------------------------------- resources
@dataclass
class Resource:
    key: str
    model: type
    label: str
    singular: str
    icon: str
    group: str
    columns: list = field(default_factory=list)
    search: list = field(default_factory=list)
    filters: list = field(default_factory=list)   # field names (choices / FK / bool)
    toggles: list = field(default_factory=list)   # bool fields switchable from the list
    fieldsets: list = None                        # [(title, [fields], help)]
    exclude: list = field(default_factory=list)
    ordering: list = None
    singleton: bool = False
    can_add: bool = True
    can_edit: bool = True
    description: str = ""
    per_page: int = 20

    @property
    def opts(self):
        return self.model._meta

    def perm(self, user, action):
        if self.singleton and action in ("add", "delete"):
            return False
        if action == "add" and not self.can_add:
            return False
        return user.has_perm(f"{self.opts.app_label}.{action}_{self.opts.model_name}")

    def queryset(self):
        qs = self.model._default_manager.all()
        if self.ordering:
            return qs.order_by(*self.ordering)
        return qs if self.opts.ordering else qs.order_by("-pk")


RESOURCES = [
    # ------------------------------------------------ Listings
    Resource(
        "properties", Property, "Properties", "Property", "bi-house-door", "Listings",
        description="All listings shown on the website.",
        columns=[C("img", "", "image"), C("title", "Property", "title", True), C("city", "City"), C("property_type", "Type"),
                 C("get_status_display", "Status", "badge"), C("price", "Price", "money", True), C("bedrooms", "Beds"),
                 C("is_featured", "Featured", "bool"), C("is_published", "Published", "bool")],
        search=["title", "address", "zip_code", "description"],
        filters=["status", "property_type", "city", "label", "agent", "is_featured", "is_published"],
        toggles=["is_featured", "is_published"],
        fieldsets=[
            ("Listing", ["title", "slug", "status", "label", "property_type", "city", "agent", "is_featured", "is_published"], "Leave the slug empty to generate it from the title."),
            ("Price & location", ["price", "price_suffix", "address", "zip_code"], "Use a price suffix such as “/mo” for rentals."),
            ("Details", ["bedrooms", "bathrooms", "garages", "area", "lot_size", "year_built"], ""),
            ("Description", ["excerpt", "description"], ""),
            ("Amenities", ["amenities"], ""),
            ("Main photo & video", ["image", "video_url"], "Upload a photo or paste an image link. More photos go in the gallery below."),
        ],
    ),
    Resource(
        "agents", Agent, "Agents", "Agent", "bi-person-badge", "Listings",
        columns=[C("img", "", "avatar"), C("name", "Name", "title", True), C("title", "Role"), C("phone"), C("email"),
                 C("order", "Order", sortable=True), C("is_active", "Active", "bool")],
        search=["name", "email", "phone"], filters=["is_active"], toggles=["is_active"],
        fieldsets=[
            ("Profile", ["name", "slug", "title", "languages", "bio", "order", "is_active"], ""),
            ("Contact", ["phone", "email"], ""),
            ("Photo", ["photo"], ""),
            ("Social links", ["facebook", "instagram", "linkedin"], ""),
        ],
    ),
    Resource("cities", City, "Cities", "City", "bi-geo-alt", "Listings",
             columns=[C("img", "", "image"), C("name", "City", "title"), C("state"), C("properties.count", "Listings"), C("order", sortable=True)],
             search=["name"]),
    Resource("types", PropertyType, "Property Types", "Property Type", "bi-grid-1x2", "Listings",
             columns=[C("img", "", "image"), C("icon", "", "icon"), C("name", "Type", "title"), C("properties.count", "Listings"), C("order", sortable=True)],
             search=["name"]),
    Resource("labels", Label, "Labels", "Label", "bi-tag", "Listings",
             columns=[C("name", "Label", "title"), C("color", "Color", "color"), C("properties.count", "Listings")], search=["name"]),
    Resource("amenities", Amenity, "Amenities", "Amenity", "bi-stars", "Listings",
             columns=[C("icon", "", "icon"), C("name", "Amenity", "title"), C("properties.count", "Listings")], search=["name"], per_page=50),

    # ------------------------------------------------ Website content
    Resource("site-settings", SiteSettings, "Site Settings", "Site Settings", "bi-sliders", "Website", singleton=True,
             description="Brand, contact details, colors, header, hero and every home-page section.",
             fieldsets=[
                 ("Brand", ["site_name", "tagline", "logo", "favicon", "primary_color", "accent_color", "meta_description"], "Leave the logo empty to show the site name as a text logo."),
                 ("Contact details", ["phone", "email", "address", "office_hours", "map_embed_url"], ""),
                 ("Social links", ["facebook", "instagram", "twitter", "linkedin", "youtube"], "Leave a field empty to hide that icon."),
                 ("Header", ["topbar_text", "header_button_text", "header_button_link"], ""),
                 ("Hero", ["hero_badge", "hero_title", "hero_subtitle"], "Background images are managed under Hero Slides."),
                 ("Featured properties section", ["show_featured", "featured_title", "featured_subtitle"], ""),
                 ("Why-us section", ["show_features", "features_title", "features_subtitle"], ""),
                 ("Recently listed section", ["show_latest", "latest_title", "latest_subtitle"], ""),
                 ("Lifestyles section", ["show_types", "types_title", "types_subtitle"], ""),
                 ("Cities section", ["show_cities", "cities_title", "cities_subtitle"], ""),
                 ("Call-to-action band", ["show_cta", "cta_title", "cta_text", "cta_button_text", "cta_button_link", "cta_image"], ""),
                 ("Pricing section", ["show_pricing", "pricing_title", "pricing_subtitle"], ""),
                 ("Testimonials section", ["show_testimonials", "testimonials_title", "testimonials_subtitle"], ""),
                 ("Agents section", ["show_agents", "agents_title", "agents_subtitle"], ""),
                 ("Blog section", ["show_blog", "blog_title", "blog_subtitle"], ""),
                 ("Contact section", ["show_contact", "contact_title", "contact_subtitle", "contact_image"], ""),
                 ("Footer", ["footer_about", "copyright_text"], ""),
             ]),
    Resource("hero-slides", HeroSlide, "Hero Slides", "Hero Slide", "bi-images", "Website",
             description="Background images that cross-fade behind the home-page search.",
             columns=[C("img", "", "image"), C("caption", "Caption", "title"), C("order", sortable=True), C("is_active", "Active", "bool")],
             toggles=["is_active"]),
    Resource("page-banners", PageHeader, "Page Banners", "Page Banner", "bi-window", "Website",
             columns=[C("img", "", "image"), C("get_page_display", "Page", "badge"), C("title", "Title", "title"), C("subtitle")]),
    Resource("about", AboutPage, "About Page", "About Page", "bi-info-circle", "Website", singleton=True,
             fieldsets=[
                 ("Introduction", ["intro_eyebrow", "intro_title", "intro_text", "years_experience"], ""),
                 ("Images", ["intro_image", "second_image"], ""),
                 ("Mission, vision & promise", ["mission_title", "mission_text", "vision_title", "vision_text", "values_title", "values_text"], ""),
                 ("Sections", ["show_team", "show_testimonials"], ""),
             ]),
    Resource("features", Feature, "Why-Us Features", "Feature", "bi-award", "Website",
             columns=[C("icon", "", "icon"), C("title", "Title", "title"), C("description"), C("order", sortable=True)]),
    Resource("stats", Stat, "Stats", "Stat", "bi-123", "Website",
             columns=[C("__str__", "Stat", "title"), C("label"), C("order", sortable=True)]),
    Resource("pricing", PricingPlan, "Pricing Plans", "Pricing Plan", "bi-credit-card", "Website",
             columns=[C("name", "Plan", "title"), C("price", "Price", "money"), C("period"), C("is_popular", "Popular", "bool"), C("order", sortable=True)],
             toggles=["is_popular"]),
    Resource("testimonials", Testimonial, "Testimonials", "Testimonial", "bi-chat-quote", "Website",
             columns=[C("img", "", "avatar"), C("name", "Name", "title"), C("role"), C("rating", "Stars"), C("order", sortable=True), C("is_active", "Active", "bool")],
             toggles=["is_active"], search=["name", "quote"]),
    Resource("popups", Popup, "Popups", "Popup", "bi-window-stack", "Website",
             description="Only the most recently updated active popup is shown to visitors.",
             columns=[C("img", "", "image"), C("name", "Name", "title"), C("title"), C("get_frequency_display", "Shows", "badge"),
                      C("delay_seconds", "Delay (s)"), C("is_active", "Active", "bool")],
             toggles=["is_active"],
             fieldsets=[
                 ("General", ["name", "is_active"], ""),
                 ("Content", ["eyebrow", "title", "text", "image"], ""),
                 ("Form or button", ["show_form", "form_button_text", "note", "button_text", "button_link"], "When the form is off, the button is shown instead."),
                 ("Display rules", ["delay_seconds", "frequency", "pages"], ""),
             ]),

    # ------------------------------------------------ Blog
    Resource("posts", Post, "Blog Posts", "Post", "bi-journal-richtext", "Blog",
             columns=[C("img", "", "image"), C("title", "Title", "title", True), C("category"), C("author"),
                      C("published_at", "Published", "date", True), C("is_published", "Live", "bool")],
             search=["title", "excerpt", "body"], filters=["category", "author", "is_published"], toggles=["is_published"],
             fieldsets=[
                 ("Post", ["title", "slug", "category", "author", "published_at", "read_minutes", "is_published"], ""),
                 ("Cover image", ["image"], ""),
                 ("Content", ["excerpt", "body"], "Separate paragraphs with a blank line. Start a line with “## ” to make it a heading."),
             ]),
    Resource("categories", Category, "Categories", "Category", "bi-folder", "Blog",
             columns=[C("name", "Category", "title"), C("slug"), C("posts.count", "Posts")], search=["name"]),

    # ------------------------------------------------ Inbox
    Resource("messages", ContactMessage, "Messages & Leads", "Message", "bi-inbox", "Inbox", can_add=False,
             columns=[C("name", "From", "title"), C("email"), C("phone"), C("get_source_display", "Source", "badge"),
                      C("property", "Property"), C("created", "Received", "date", True)],
             search=["name", "email", "phone", "subject", "message"], filters=["source", "is_read"], toggles=[]),
    Resource("subscribers", Subscriber, "Subscribers", "Subscriber", "bi-envelope-paper", "Inbox", can_edit=False,
             columns=[C("email", "Email", "title"), C("created", "Subscribed", "date", True)], search=["email"], per_page=50),
]

REGISTRY = {r.key: r for r in RESOURCES}


GROUP_ORDER = ["Inbox", "Listings", "Blog", "Website"]


def grouped():
    groups = {g: [] for g in GROUP_ORDER}
    for r in RESOURCES:
        groups.setdefault(r.group, []).append(r)
    return {g: items for g, items in groups.items() if items}
