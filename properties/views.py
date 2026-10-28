from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from core.forms import InquiryForm
from core.views import page_header

from .models import Agent, Amenity, City, Label, Property, PropertyType

SORT_OPTIONS = {
    "newest": ("Newest first", "-created"),
    "price_asc": ("Price: low to high", "price"),
    "price_desc": ("Price: high to low", "-price"),
    "area_desc": ("Largest first", "-area"),
}


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _decimal(value):
    try:
        return Decimal(value)
    except (TypeError, ValueError, InvalidOperation):
        return None


def property_list(request):
    qs = Property.objects.published().select_related("city", "property_type", "label", "agent")
    g = request.GET

    if q := g.get("q", "").strip():
        qs = qs.filter(Q(title__icontains=q) | Q(address__icontains=q) | Q(description__icontains=q) | Q(zip_code__icontains=q) | Q(city__name__icontains=q))
    if g.get("city"):
        qs = qs.filter(city__slug=g["city"])
    if g.get("type"):
        qs = qs.filter(property_type__slug=g["type"])
    if g.get("status") in dict(Property.STATUS_CHOICES):
        qs = qs.filter(status=g["status"])
    if g.get("label"):
        qs = qs.filter(label__slug=g["label"])
    if beds := _int(g.get("beds")):
        qs = qs.filter(bedrooms__gte=beds)
    if baths := _int(g.get("baths")):
        qs = qs.filter(bathrooms__gte=baths)
    if (min_price := _decimal(g.get("min_price"))) is not None:
        qs = qs.filter(price__gte=min_price)
    if (max_price := _decimal(g.get("max_price"))) is not None:
        qs = qs.filter(price__lte=max_price)
    selected_amenities = [a for a in g.getlist("amenities") if a.isdigit()]
    for amenity_id in selected_amenities:
        qs = qs.filter(amenities__id=amenity_id)

    sort = g.get("sort") if g.get("sort") in SORT_OPTIONS else "newest"
    qs = qs.order_by(SORT_OPTIONS[sort][1]).distinct()

    page = Paginator(qs, 9).get_page(g.get("page"))
    params = g.copy()
    params.pop("page", None)
    view_params = params.copy()
    view_params.pop("view", None)

    context = {
        "header": page_header("properties"),
        "page_obj": page,
        "properties": page.object_list,
        "total": page.paginator.count,
        "amenities": Amenity.objects.all(),
        "selected_amenities": selected_amenities,
        "sort_options": [(k, v[0]) for k, v in SORT_OPTIONS.items()],
        "sort": sort,
        "query_string": params.urlencode(),
        "view_qs": view_params.urlencode(),
        "view_mode": "list" if g.get("view") == "list" else "grid",
        "active_city": City.objects.filter(slug=g.get("city")).first() if g.get("city") else None,
        "active_type": PropertyType.objects.filter(slug=g.get("type")).first() if g.get("type") else None,
        "active_label": Label.objects.filter(slug=g.get("label")).first() if g.get("label") else None,
        "types_with_counts": PropertyType.objects.annotate(n=Count("properties", filter=Q(properties__is_published=True))).order_by("order", "name"),
    }
    return render(request, "properties/property_list.html", context)


def property_detail(request, slug):
    prop = get_object_or_404(
        Property.objects.published().select_related("city", "property_type", "label", "agent").prefetch_related("amenities", "images"),
        slug=slug,
    )
    form = InquiryForm(
        request.POST or None,
        initial={"message": f"Hello, I'm interested in \"{prop.title}\". Please send me more information."},
    )
    if request.method == "POST":
        if form.is_valid():
            msg = form.save(commit=False)
            msg.source = "property"
            msg.property = prop
            msg.agent = prop.agent
            msg.subject = f"Inquiry: {prop.title}"[:200]
            msg.save()
            messages.success(request, "Your inquiry was sent. The listing agent will contact you shortly.")
            return redirect(prop.get_absolute_url() + "#inquiry")
        messages.error(request, "Please correct the highlighted fields.")

    similar = (
        Property.objects.published()
        .exclude(pk=prop.pk)
        .filter(Q(property_type=prop.property_type) | Q(city=prop.city))
        .select_related("city", "property_type", "label")[:3]
    )
    return render(request, "properties/property_detail.html", {"property": prop, "form": form, "similar": similar})


def agent_list(request):
    agents = Agent.objects.filter(is_active=True).annotate(listing_count=Count("properties", filter=Q(properties__is_published=True))).order_by("order", "name")
    return render(request, "properties/agent_list.html", {"agents": agents, "header": page_header("agents")})


def agent_detail(request, slug):
    agent = get_object_or_404(Agent, slug=slug, is_active=True)
    form = InquiryForm(request.POST or None, initial={"message": f"Hi {agent.name.split()[0]}, I'd like to talk about buying or selling a property."})
    if request.method == "POST":
        if form.is_valid():
            msg = form.save(commit=False)
            msg.source = "agent"
            msg.agent = agent
            msg.subject = f"Message for {agent.name}"
            msg.save()
            messages.success(request, f"Your message was sent to {agent.name}.")
            return redirect(agent.get_absolute_url() + "#contact-agent")
        messages.error(request, "Please correct the highlighted fields.")
    listings = agent.properties.published().select_related("city", "property_type", "label")
    return render(request, "properties/agent_detail.html", {"agent": agent, "listings": listings, "form": form})
