from django.contrib import admin
from django.utils.html import format_html

from core.admin import large_preview, preview_field

from .models import Agent, Amenity, City, Label, Property, PropertyImage, PropertyType


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ["preview", "image", "image_url", "order"]
    readonly_fields = ["preview"]
    preview = preview_field()


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ["preview", "title", "status", "property_type", "city", "price_display", "bedrooms", "is_featured", "is_published"]
    list_display_links = ["preview", "title"]
    list_editable = ["is_featured", "is_published"]
    list_filter = ["status", "property_type", "city", "label", "is_featured", "is_published", "agent"]
    search_fields = ["title", "address", "zip_code", "description"]
    prepopulated_fields = {"slug": ["title"]}
    filter_horizontal = ["amenities"]
    readonly_fields = ["big_preview", "created", "updated"]
    autocomplete_fields = ["agent"]
    inlines = [PropertyImageInline]
    list_per_page = 25
    fieldsets = [
        ("Listing", {"fields": ["title", "slug", ("status", "label"), ("property_type", "city"), "agent", ("is_featured", "is_published")]}),
        ("Price & location", {"fields": [("price", "price_suffix"), "address", "zip_code"]}),
        ("Details", {"fields": [("bedrooms", "bathrooms", "garages"), ("area", "lot_size", "year_built")]}),
        ("Description", {"fields": ["excerpt", "description", "amenities"]}),
        ("Media", {"fields": ["image", "image_url", "big_preview", "video_url"],
                   "description": "Add more photos in the “Gallery images” section below."}),
        ("Info", {"classes": ["collapse"], "fields": ["created", "updated"]}),
    ]
    preview = preview_field()
    big_preview = large_preview()

    @admin.display(description="Price", ordering="price")
    def price_display(self, obj):
        return f"${obj.price:,.0f}{obj.price_suffix}"


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["preview", "name", "title", "phone", "email", "order", "is_active"]
    list_display_links = ["preview", "name"]
    list_editable = ["order", "is_active"]
    search_fields = ["name", "email"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["big_preview"]
    fieldsets = [
        (None, {"fields": ["name", "slug", "title", ("phone", "email"), "languages", "bio", ("order", "is_active")]}),
        ("Photo", {"fields": ["photo", "photo_url", "big_preview"]}),
        ("Social", {"fields": ["facebook", "instagram", "linkedin"]}),
    ]
    preview = preview_field("img", round_=True)
    big_preview = large_preview()


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["preview", "name", "state", "order"]
    list_display_links = ["preview", "name"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["big_preview"]
    preview = preview_field()
    big_preview = large_preview()


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ["preview", "name", "icon", "order"]
    list_display_links = ["preview", "name"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["big_preview"]
    preview = preview_field()
    big_preview = large_preview()


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ["name", "badge"]
    prepopulated_fields = {"slug": ["name"]}

    @admin.display(description="Badge")
    def badge(self, obj):
        return format_html('<span style="background:{};color:#fff;padding:3px 10px;border-radius:20px;font-size:11px">{}</span>', obj.color, obj.name)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ["name", "icon"]
    search_fields = ["name"]
