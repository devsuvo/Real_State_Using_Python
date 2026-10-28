from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from blog.models import Post
from properties.models import Agent, City, Property, PropertyType

from .context_processors import get_favorites
from .forms import ContactForm, LeadForm, SubscribeForm
from .models import AboutPage, Feature, HeroSlide, PageHeader, PricingPlan, Stat, Testimonial


def _back(request, fallback="/"):
    target = request.POST.get("next") or request.META.get("HTTP_REFERER") or fallback
    if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return redirect(target)
    return redirect(fallback)


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def page_header(page):
    return PageHeader.objects.filter(page=page).first()


def home(request):
    published = Property.objects.published().select_related("city", "property_type", "label", "agent")
    form = ContactForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            msg = form.save(commit=False)
            msg.source = "home"
            msg.save()
            messages.success(request, "Thank you! One of our advisors will contact you shortly.")
            return redirect("/#contact")
        messages.error(request, "Please correct the highlighted fields.")

    context = {
        "slides": HeroSlide.objects.filter(is_active=True),
        "featured": published.filter(is_featured=True)[:9],
        "latest": published[:6],
        "features": Feature.objects.all(),
        "stats": Stat.objects.all(),
        "types": PropertyType.objects.annotate(n=Count("properties", filter=Q(properties__is_published=True))).order_by("order", "name"),
        "cities": City.objects.annotate(n=Count("properties", filter=Q(properties__is_published=True))).order_by("order", "name"),
        "plans": PricingPlan.objects.all(),
        "testimonials": Testimonial.objects.filter(is_active=True),
        "agents": Agent.objects.filter(is_active=True)[:4],
        "posts": Post.objects.published().select_related("category", "author")[:3],
        "form": form,
    }
    return render(request, "core/home.html", context)


def about(request):
    context = {
        "header": page_header("about"),
        "about": AboutPage.load(),
        "stats": Stat.objects.all(),
        "features": Feature.objects.all(),
        "agents": Agent.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_active=True),
    }
    return render(request, "core/about.html", context)


def contact(request):
    form = ContactForm(request.POST or None, initial={"subject": request.GET.get("subject", "")})
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent. We'll get back to you within one business day.")
            return redirect("core:contact")
        messages.error(request, "Please correct the highlighted fields.")
    return render(request, "core/contact.html", {"form": form, "header": page_header("contact")})


@require_POST
def subscribe(request):
    form = SubscribeForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "You're subscribed! Watch your inbox for new listings.")
    else:
        messages.error(request, "Please enter a valid email address.")
    return _back(request)


@require_POST
def lead(request):
    form = LeadForm(request.POST)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.source = "popup"
        msg.subject = request.POST.get("popup_title", "")[:200]
        msg.save()
        if _is_ajax(request):
            return JsonResponse({"ok": True})
        messages.success(request, "Thank you! We'll be in touch soon.")
    elif _is_ajax(request):
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    else:
        messages.error(request, "Please enter your name and a valid email.")
    return _back(request)


def favorites(request):
    ids = get_favorites(request)
    items = Property.objects.published().filter(pk__in=ids).select_related("city", "property_type", "label")
    return render(request, "core/favorites.html", {"properties": items, "header": page_header("favorites")})


@require_POST
def toggle_favorite(request, pk):
    prop = get_object_or_404(Property, pk=pk, is_published=True)
    ids = get_favorites(request)
    if prop.pk in ids:
        ids.remove(prop.pk)
        active = False
    else:
        ids.append(prop.pk)
        active = True
    request.session["favorites"] = ids
    if _is_ajax(request):
        return JsonResponse({"active": active, "count": len(ids)})
    return _back(request)


def page_not_found(request, exception):
    return render(request, "404.html", status=404)
