import csv
import json
from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from blog.models import Post
from core.models import ContactMessage, Popup, Subscriber
from properties.models import City, Property, PropertyType

from .forms import GalleryFormSet, build_form_class, layout, style_formset
from .registry import REGISTRY, RESOURCES, grouped


# ---------------------------------------------------------------- helpers
def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("dashboard:login"))
        if not (user.is_active and user.is_staff):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def get_resource(key, user, action="view"):
    resource = REGISTRY.get(key)
    if not resource:
        raise Http404
    if not resource.perm(user, action):
        raise PermissionDenied
    return resource


def ctx(request, **extra):
    """Context shared by every dashboard page (sidebar, badges)."""
    unread = ContactMessage.objects.filter(is_read=False).count()
    nav = []
    for group, items in grouped().items():
        visible = [r for r in items if r.perm(request.user, "view")]
        if visible:
            nav.append((group, visible))
    return {"nav": nav, "unread_count": unread, **extra}


def _url(resource, obj=None):
    if resource.singleton:
        return reverse("dashboard:singleton", args=[resource.key])
    if obj is None:
        return reverse("dashboard:list", args=[resource.key])
    return reverse("dashboard:edit", args=[resource.key, obj.pk])


def nice_label(text):
    text = str(text)
    return (text[3:] if text.lower().startswith("is ") else text).capitalize()


def _filter_options(resource):
    out = []
    for name in resource.filters:
        f = resource.model._meta.get_field(name)
        if f.choices:
            choices = [(str(k), v) for k, v in f.choices]
        elif isinstance(f, models.BooleanField):
            choices = [("1", "Yes"), ("0", "No")]
        elif f.is_relation:
            choices = [(str(o.pk), str(o)) for o in f.related_model._default_manager.all()]
        else:
            continue
        out.append({"name": name, "label": nice_label(f.verbose_name), "choices": choices})
    return out


# ---------------------------------------------------------------- overview
@staff_required
def overview(request):
    now = timezone.now()
    props = Property.objects.all()
    published = props.filter(is_published=True)
    days = 30
    start = (now - timedelta(days=days - 1)).date()

    leads_by_day = dict(
        ContactMessage.objects.filter(created__date__gte=start)
        .annotate(day=TruncDate("created")).values("day").annotate(n=Count("id")).values_list("day", "n")
    )
    labels, series = [], []
    for i in range(days):
        d = start + timedelta(days=i)
        labels.append(d.strftime("%b %d"))
        series.append(leads_by_day.get(d, 0))

    by_city = list(City.objects.annotate(n=Count("properties", filter=Q(properties__is_published=True))).order_by("-n", "name").values_list("name", "n"))
    by_type = list(PropertyType.objects.annotate(n=Count("properties", filter=Q(properties__is_published=True))).order_by("-n", "name").values_list("name", "n"))
    max_type = max([n for _, n in by_type] or [1]) or 1

    week_ago = now - timedelta(days=7)
    context = ctx(
        request,
        page_title="Overview",
        kpis=[
            {"label": "Published listings", "value": published.count(), "icon": "bi-house-door", "sub": f"{props.count() - published.count()} hidden · {published.filter(is_featured=True).count()} featured", "url": reverse("dashboard:list", args=["properties"])},
            {"label": "New leads (7 days)", "value": ContactMessage.objects.filter(created__gte=week_ago).count(), "icon": "bi-inbox", "sub": f"{ContactMessage.objects.filter(is_read=False).count()} unread", "url": reverse("dashboard:list", args=["messages"])},
            {"label": "Subscribers", "value": Subscriber.objects.count(), "icon": "bi-envelope-paper", "sub": f"+{Subscriber.objects.filter(created__gte=week_ago).count()} this week", "url": reverse("dashboard:list", args=["subscribers"])},
            {"label": "Blog posts", "value": Post.objects.filter(is_published=True).count(), "icon": "bi-journal-richtext", "sub": f"{Post.objects.filter(is_published=False).count()} drafts", "url": reverse("dashboard:list", args=["posts"])},
        ],
        sale_value=published.filter(status=Property.STATUS_SALE).aggregate(v=Sum("price"))["v"] or 0,
        sale_count=published.filter(status=Property.STATUS_SALE).count(),
        rent_count=published.filter(status=Property.STATUS_RENT).count(),
        chart=json.dumps({"labels": labels, "leads": series, "cities": [c for c, _ in by_city], "cityCounts": [n for _, n in by_city]}),
        leads_total=sum(series),
        by_type=[(name, n, round(n * 100 / max_type)) for name, n in by_type],
        recent_leads=ContactMessage.objects.select_related("property")[:6],
        recent_props=props.select_related("city")[:5],
        active_popup=Popup.objects.filter(is_active=True).first(),
    )
    return render(request, "dashboard/overview.html", context)


# ---------------------------------------------------------------- list
@staff_required
def resource_list(request, key):
    resource = get_resource(key, request.user)
    if resource.singleton:
        return redirect(_url(resource))
    qs = resource.queryset()
    g = request.GET

    q = g.get("q", "").strip()
    if q and resource.search:
        cond = Q()
        for f in resource.search:
            cond |= Q(**{f"{f}__icontains": q})
        qs = qs.filter(cond)

    filters = _filter_options(resource)
    active_filters = 0
    for flt in filters:
        val = g.get(flt["name"], "")
        flt["value"] = val
        if val != "":
            active_filters += 1
            field = resource.model._meta.get_field(flt["name"])
            if isinstance(field, models.BooleanField):
                qs = qs.filter(**{flt["name"]: val == "1"})
            else:
                qs = qs.filter(**{flt["name"]: val})

    sortable = {c.name for c in resource.columns if c.sortable}
    sort = g.get("sort", "")
    if sort.lstrip("-") in sortable:
        qs = qs.order_by(sort)

    page = Paginator(qs, resource.per_page).get_page(g.get("page"))
    params = g.copy()
    params.pop("page", None)

    def cell(c, o):
        if c.name in resource.toggles:
            return {"toggle": c.name, "value": getattr(o, c.name), "label": f"{c.label}: {o}"}
        return {"html": c.render(o)}

    rows = [{"obj": o, "cells": [cell(c, o) for c in resource.columns]} for o in page.object_list]

    context = ctx(
        request,
        resource=resource,
        page_title=resource.label,
        page_obj=page,
        rows=rows,
        total=page.paginator.count,
        q=q,
        filters=filters,
        active_filters=active_filters,
        sort=sort,
        query_string=params.urlencode(),
        can_add=resource.perm(request.user, "add"),
        can_delete=resource.perm(request.user, "delete"),
        can_change=resource.perm(request.user, "change"),
        toggle_labels={t: nice_label(resource.model._meta.get_field(t).verbose_name) for t in resource.toggles},
    )
    return render(request, "dashboard/list.html", context)


@staff_required
@require_POST
def bulk_action(request, key):
    resource = get_resource(key, request.user)
    ids = request.POST.getlist("ids")
    action = request.POST.get("action")
    qs = resource.model._default_manager.filter(pk__in=ids)
    if not ids:
        messages.warning(request, "Select at least one item first.")
    elif action == "delete":
        if not resource.perm(request.user, "delete"):
            raise PermissionDenied
        n = qs.count()
        qs.delete()
        messages.success(request, f"Deleted {n} {resource.label.lower()}.")
    elif action in ("mark_read", "mark_unread") and resource.key == "messages":
        qs.update(is_read=action == "mark_read")
        messages.success(request, "Messages updated.")
    elif action.startswith("set:") or action.startswith("unset:"):
        mode, fname = action.split(":", 1)
        if fname not in resource.toggles or not resource.perm(request.user, "change"):
            raise PermissionDenied
        qs.update(**{fname: mode == "set"})
        messages.success(request, f"Updated {qs.count()} item(s).")
    return redirect(request.POST.get("next") or _url(resource))


@staff_required
@require_POST
def toggle(request, key, pk, field):
    resource = get_resource(key, request.user, "change")
    if field not in resource.toggles:
        raise PermissionDenied
    obj = get_object_or_404(resource.model, pk=pk)
    setattr(obj, field, not getattr(obj, field))
    obj.save()
    return JsonResponse({"value": getattr(obj, field)})


# ---------------------------------------------------------------- forms
def _save_form(request, resource, instance=None):
    is_new = instance is None or instance.pk is None
    FormClass = build_form_class(resource)
    form = FormClass(request.POST or None, request.FILES or None, instance=instance)
    gallery = None
    if resource.model is Property:
        gallery = style_formset(GalleryFormSet(request.POST or None, request.FILES or None, instance=form.instance, prefix="gallery"))

    if request.method == "POST":
        valid = form.is_valid() and (gallery is None or gallery.is_valid())
        if valid:
            obj = form.save()
            if gallery is not None:
                gallery.instance = obj
                gallery.save()
            name = resource.singular if resource.singleton else f"{resource.singular} “{obj}”"
            messages.success(request, f"{name} {'created' if is_new else 'saved'}.")
            if "_addanother" in request.POST:
                return redirect(reverse("dashboard:add", args=[resource.key]))
            if "_continue" in request.POST or resource.singleton:
                return redirect(_url(resource, obj))
            return redirect(_url(resource))
        messages.error(request, "Please fix the highlighted fields below.")

    obj = form.instance
    context = ctx(
        request,
        resource=resource,
        page_title=resource.label if resource.singleton else (f"Add {resource.singular.lower()}" if is_new else str(obj)),
        form=form,
        sections=layout(resource, form),
        gallery=gallery,
        is_new=is_new,
        obj=obj,
        view_url=obj.get_absolute_url() if not is_new and hasattr(obj, "get_absolute_url") else ("/" if resource.singleton else ""),
        can_delete=not is_new and resource.perm(request.user, "delete"),
        can_change=resource.perm(request.user, "change"),
    )
    return render(request, "dashboard/form.html", context)


@staff_required
def add(request, key):
    resource = get_resource(key, request.user, "add")
    return _save_form(request, resource)


@staff_required
def edit(request, key, pk):
    resource = get_resource(key, request.user)
    if resource.key == "messages":
        return message_detail(request, pk)
    if not resource.can_edit:
        raise PermissionDenied
    if request.method == "POST" and not resource.perm(request.user, "change"):
        raise PermissionDenied
    obj = get_object_or_404(resource.model, pk=pk)
    return _save_form(request, resource, obj)


@staff_required
def singleton(request, key):
    resource = get_resource(key, request.user)
    if not resource.singleton:
        raise Http404
    if request.method == "POST" and not resource.perm(request.user, "change"):
        raise PermissionDenied
    return _save_form(request, resource, resource.model.load())


@staff_required
def delete(request, key, pk):
    resource = get_resource(key, request.user, "delete")
    obj = get_object_or_404(resource.model, pk=pk)
    if request.method == "POST":
        label = str(obj)
        obj.delete()
        messages.success(request, f"{resource.singular} “{label}” deleted.")
        return redirect(_url(resource))
    return render(request, "dashboard/confirm_delete.html", ctx(request, resource=resource, obj=obj, page_title=f"Delete {resource.singular.lower()}"))


# ---------------------------------------------------------------- inbox
def message_detail(request, pk):
    resource = REGISTRY["messages"]
    msg = get_object_or_404(ContactMessage.objects.select_related("property", "agent"), pk=pk)
    if request.method == "POST":
        if not resource.perm(request.user, "change"):
            raise PermissionDenied
        msg.is_read = request.POST.get("is_read") == "1"
        msg.save(update_fields=["is_read"])
        messages.success(request, "Marked as read." if msg.is_read else "Marked as unread.")
        return redirect(_url(resource))
    if not msg.is_read and resource.perm(request.user, "change"):
        msg.is_read = True
        msg.save(update_fields=["is_read"])
    others = ContactMessage.objects.filter(email__iexact=msg.email).exclude(pk=msg.pk)[:5]
    return render(request, "dashboard/message.html", ctx(
        request, resource=resource, msg=msg, others=others, page_title=f"Message from {msg.name}",
        can_delete=resource.perm(request.user, "delete"),
    ))


@staff_required
def export_csv(request, key):
    resource = get_resource(key, request.user)
    if key not in ("messages", "subscribers"):
        raise Http404
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="crystalbay-{key}-{timezone.now():%Y%m%d}.csv"'
    writer = csv.writer(response)
    if key == "subscribers":
        writer.writerow(["Email", "Subscribed"])
        for s in Subscriber.objects.all():
            writer.writerow([s.email, s.created.strftime("%Y-%m-%d %H:%M")])
    else:
        writer.writerow(["Received", "Name", "Email", "Phone", "Source", "Subject", "Message", "Property", "Agent", "Read"])
        for m in ContactMessage.objects.select_related("property", "agent"):
            writer.writerow([m.created.strftime("%Y-%m-%d %H:%M"), m.name, m.email, m.phone, m.get_source_display(),
                             m.subject, m.message, m.property or "", m.agent or "", "yes" if m.is_read else "no"])
    return response


# ---------------------------------------------------------------- search & account
@staff_required
def search(request):
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        for r in RESOURCES:
            if r.singleton or not r.search or not r.perm(request.user, "view"):
                continue
            cond = Q()
            for f in r.search:
                cond |= Q(**{f"{f}__icontains": q})
            hits = list(r.queryset().filter(cond)[:6])
            if hits:
                results.append({"resource": r, "hits": [(h, _url(r, h)) for h in hits]})
    return render(request, "dashboard/search.html", ctx(request, q=q, results=results, page_title=f"Search: {q}" if q else "Search"))


@staff_required
def password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    for f in form.fields.values():
        f.widget.attrs["class"] = "form-control"
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Your password has been changed.")
        return redirect("dashboard:overview")
    return render(request, "dashboard/password.html", ctx(request, form=form, page_title="Change password"))
