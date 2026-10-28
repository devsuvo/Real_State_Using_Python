from django.contrib import admin

from core.admin import large_preview, preview_field

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["preview", "title", "category", "author", "published_at", "is_published"]
    list_display_links = ["preview", "title"]
    list_editable = ["is_published"]
    list_filter = ["category", "is_published", "author"]
    search_fields = ["title", "excerpt", "body"]
    prepopulated_fields = {"slug": ["title"]}
    date_hierarchy = "published_at"
    readonly_fields = ["big_preview"]
    fieldsets = [
        (None, {"fields": ["title", "slug", ("category", "author"), ("published_at", "read_minutes", "is_published")]}),
        ("Cover image", {"fields": ["image", "image_url", "big_preview"]}),
        ("Content", {"fields": ["excerpt", "body"]}),
    ]
    preview = preview_field()
    big_preview = large_preview()
