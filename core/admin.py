from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    AboutPage,
    ContactMessage,
    Feature,
    HeroSlide,
    PageHeader,
    Popup,
    PricingPlan,
    SiteSettings,
    Stat,
    Subscriber,
    Testimonial,
)


def thumb(url, size=64, round_=False):
    if not url:
        return "—"
    radius = "50%" if round_ else "8px"
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:{};box-shadow:0 1px 3px rgba(0,0,0,.2)">',
        url, size, size if round_ else int(size * 0.7), radius,
    )


def preview_field(attr="img", round_=False, label="Preview"):
    def _preview(self, obj):
        return thumb(getattr(obj, attr, ""), 64, round_)
    _preview.short_description = label
    return _preview


def large_preview(attr="img"):
    def _preview(self, obj):
        url = getattr(obj, attr, "")
        if not url:
            return "No image yet — upload one or paste a link, then save."
        return format_html('<img src="{}" style="max-width:420px;max-height:260px;border-radius:10px;object-fit:cover">', url)
    _preview.short_description = "Current image"
    return _preview


class SingletonAdmin(admin.ModelAdmin):
    """Edit-only admin for single-row models: the list view jumps straight into the form."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        return redirect(reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk]))


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    readonly_fields = ["cta_preview", "contact_preview"]
    fieldsets = [
        ("Brand", {"fields": ["site_name", "tagline", "logo", "favicon", ("primary_color", "accent_color"), "meta_description"]}),
        ("Contact details", {"fields": [("phone", "email"), "address", "office_hours", "map_embed_url"]}),
        ("Social links", {"fields": [("facebook", "instagram"), ("twitter", "linkedin"), "youtube"]}),
        ("Header", {"fields": ["topbar_text", ("header_button_text", "header_button_link")]}),
        ("Hero (top of home page)", {"fields": ["hero_badge", "hero_title", "hero_subtitle"],
                                      "description": "Background images are managed under “Hero Slides”."}),
        ("Home · Featured properties", {"classes": ["collapse"], "fields": ["show_featured", "featured_title", "featured_subtitle"]}),
        ("Home · Why choose us", {"classes": ["collapse"], "fields": ["show_features", "features_title", "features_subtitle"]}),
        ("Home · Recently listed", {"classes": ["collapse"], "fields": ["show_latest", "latest_title", "latest_subtitle"]}),
        ("Home · Lifestyles (property types)", {"classes": ["collapse"], "fields": ["show_types", "types_title", "types_subtitle"]}),
        ("Home · Cities", {"classes": ["collapse"], "fields": ["show_cities", "cities_title", "cities_subtitle"]}),
        ("Home · Call to action band", {"classes": ["collapse"], "fields": ["show_cta", "cta_title", "cta_text", ("cta_button_text", "cta_button_link"), "cta_image", "cta_image_url", "cta_preview"]}),
        ("Home · Pricing plans", {"classes": ["collapse"], "fields": ["show_pricing", "pricing_title", "pricing_subtitle"]}),
        ("Home · Testimonials", {"classes": ["collapse"], "fields": ["show_testimonials", "testimonials_title", "testimonials_subtitle"]}),
        ("Home · Agents", {"classes": ["collapse"], "fields": ["show_agents", "agents_title", "agents_subtitle"]}),
        ("Home · Blog", {"classes": ["collapse"], "fields": ["show_blog", "blog_title", "blog_subtitle"]}),
        ("Home · Contact section", {"classes": ["collapse"], "fields": ["show_contact", "contact_title", "contact_subtitle", "contact_image", "contact_image_url", "contact_preview"]}),
        ("Footer", {"fields": ["footer_about", "copyright_text"]}),
    ]
    cta_preview = large_preview("cta_img")
    contact_preview = large_preview("contact_img")


@admin.register(AboutPage)
class AboutPageAdmin(SingletonAdmin):
    readonly_fields = ["intro_preview", "second_preview"]
    fieldsets = [
        ("Introduction", {"fields": ["intro_eyebrow", "intro_title", "intro_text", "years_experience"]}),
        ("Images", {"fields": ["intro_image", "intro_image_url", "intro_preview", "second_image", "second_image_url", "second_preview"]}),
        ("Mission · Vision · Promise", {"fields": ["mission_title", "mission_text", "vision_title", "vision_text", "values_title", "values_text"]}),
        ("Sections", {"fields": ["show_team", "show_testimonials"]}),
    ]
    intro_preview = large_preview("intro_img")
    second_preview = large_preview("second_img")


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ["preview", "__str__", "order", "is_active"]
    list_editable = ["order", "is_active"]
    readonly_fields = ["big_preview"]
    preview = preview_field()
    big_preview = large_preview()


@admin.register(PageHeader)
class PageHeaderAdmin(admin.ModelAdmin):
    list_display = ["preview", "page", "title"]
    list_display_links = ["page", "title"]
    readonly_fields = ["big_preview"]
    preview = preview_field()
    big_preview = large_preview()


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["icon_preview", "title", "order"]
    list_display_links = ["title"]
    list_editable = ["order"]

    @admin.display(description="Icon")
    def icon_preview(self, obj):
        return format_html('<i class="bi {}" style="font-size:22px;color:#12A4B0"></i>', obj.icon)


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ["label", "prefix", "value", "suffix", "order"]
    list_editable = ["prefix", "value", "suffix", "order"]


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "period", "is_popular", "order"]
    list_editable = ["price", "period", "is_popular", "order"]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["preview", "name", "role", "rating", "order", "is_active"]
    list_display_links = ["name"]
    list_editable = ["order", "is_active"]
    preview = preview_field(round_=True)


@admin.register(Popup)
class PopupAdmin(admin.ModelAdmin):
    list_display = ["name", "title", "is_active", "frequency", "pages", "delay_seconds", "updated"]
    list_editable = ["is_active"]
    readonly_fields = ["big_preview"]
    fieldsets = [
        (None, {"fields": ["name", "is_active"]}),
        ("Content", {"fields": ["eyebrow", "title", "text", "image", "image_url", "big_preview"]}),
        ("Form / button", {"fields": ["show_form", "form_button_text", "note", ("button_text", "button_link")]}),
        ("Display rules", {"fields": [("delay_seconds", "frequency", "pages")]}),
    ]
    big_preview = large_preview()


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "source", "property", "agent", "created", "is_read"]
    list_filter = ["source", "is_read", "created"]
    list_editable = ["is_read"]
    search_fields = ["name", "email", "phone", "subject", "message"]
    readonly_fields = ["created"]
    date_hierarchy = "created"
    actions = ["mark_read"]

    @admin.action(description="Mark selected as read")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "created"]
    search_fields = ["email"]
