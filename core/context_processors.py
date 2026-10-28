from properties.models import City, Label, PropertyType

from .models import Popup, SiteSettings

PRICE_OPTIONS = [
    (2000, "$2,000"),
    (5000, "$5,000"),
    (10000, "$10,000"),
    (250000, "$250K"),
    (500000, "$500K"),
    (750000, "$750K"),
    (1000000, "$1M"),
    (2000000, "$2M"),
    (3000000, "$3M"),
    (5000000, "$5M"),
    (10000000, "$10M"),
]


def get_favorites(request):
    return [int(pk) for pk in request.session.get("favorites", [])]


def site_context(request):
    if request.path.startswith("/admin/"):
        return {}

    popup = Popup.objects.filter(is_active=True).first()
    if popup and popup.pages == "home":
        match = getattr(request, "resolver_match", None)
        if not match or match.url_name != "home":
            popup = None

    favorites = get_favorites(request)
    return {
        "site": SiteSettings.load(),
        "popup": popup,
        "nav_cities": City.objects.all(),
        "nav_types": PropertyType.objects.all(),
        "nav_labels": Label.objects.all(),
        "favorite_ids": favorites,
        "favorite_count": len(favorites),
        "price_options": PRICE_OPTIONS,
        "number_options": range(1, 7),
    }
