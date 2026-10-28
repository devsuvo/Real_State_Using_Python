from django import forms
from django.db import models
from django.forms import inlineformset_factory

from properties.models import Property, PropertyImage

WIDE_WIDGETS = (forms.Textarea, forms.CheckboxSelectMultiple, forms.ClearableFileInput)


def image_partner(model, name):
    """Return the name of the URL field paired with an image field (image -> image_url)."""
    partner = f"{name}_url"
    try:
        model._meta.get_field(partner)
        return partner
    except Exception:
        return None


def style_field(name, field):
    w = field.widget
    if isinstance(w, forms.CheckboxInput):
        w.attrs["class"] = "form-check-input"
        w.attrs["role"] = "switch"
    elif isinstance(w, forms.CheckboxSelectMultiple):
        pass
    elif isinstance(w, (forms.Select, forms.SelectMultiple)):
        w.attrs["class"] = "form-select"
    elif isinstance(w, forms.ClearableFileInput):
        w.attrs["class"] = "form-control"
        w.attrs["accept"] = "image/*"
    else:
        w.attrs["class"] = "form-control"
    if isinstance(w, forms.Textarea):
        w.attrs.setdefault("rows", 6 if name in ("description", "body", "intro_text", "bio") else 3)
    if name.endswith("color"):
        w.input_type = "color"
        w.attrs["class"] = "form-control form-control-color"
    if name == "icon":
        w.attrs["data-icon-input"] = "1"
        w.attrs["placeholder"] = "bi-house"
    if name.endswith("_url") or name in ("button_link", "cta_button_link", "header_button_link"):
        w.attrs.setdefault("placeholder", "https://…" if name.endswith("_url") else "/contact/")


def formfield_callback(model_field, **kwargs):
    if isinstance(model_field, models.ManyToManyField):
        return model_field.formfield(widget=forms.CheckboxSelectMultiple, **kwargs)
    if isinstance(model_field, models.DateTimeField):
        return model_field.formfield(
            widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            input_formats=["%Y-%m-%dT%H:%M"],
            **kwargs,
        )
    return model_field.formfield(**kwargs)


def build_form_class(resource):
    form_class = forms.modelform_factory(
        resource.model, fields="__all__", exclude=resource.exclude or None, formfield_callback=formfield_callback,
    )

    class DashboardForm(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for name, f in self.fields.items():
                style_field(name, f)
                if f.label and f.label.lower().startswith("is "):
                    f.label = f.label[3:].capitalize()

    return DashboardForm


def layout(resource, form):
    """
    Turn the resource's fieldsets into render-ready sections:
    [{title, help, fields: [{bf, kind, wide, partner, preview}]}]
    """
    model = resource.model
    partners = {image_partner(model, n) for n in form.fields if isinstance(form.fields[n].widget, forms.ClearableFileInput)}
    partners.discard(None)

    sets = resource.fieldsets or [("Details", list(form.fields), "")]
    used = set()
    sections = []
    for title, names, help_text in sets:
        items = []
        for name in names:
            if name not in form.fields or name in partners:
                continue
            used.add(name)
            items.append(_item(form, model, name))
            partner = items[-1]["partner"]
            if partner:
                used.add(partner.name)
        if items:
            sections.append({"title": title, "help": help_text, "fields": items})

    leftovers = [n for n in form.fields if n not in used and n not in partners]
    if leftovers:
        sections.append({"title": "Other", "help": "", "fields": [_item(form, model, n) for n in leftovers]})
    return sections


def _item(form, model, name):
    bf = form[name]
    widget = form.fields[name].widget
    kind = "text"
    if isinstance(widget, forms.CheckboxInput):
        kind = "switch"
    elif isinstance(widget, forms.CheckboxSelectMultiple):
        kind = "checks"
    elif isinstance(widget, forms.ClearableFileInput):
        kind = "image"
    elif isinstance(widget, forms.Textarea):
        kind = "textarea"

    partner = None
    preview = ""
    if kind == "image":
        pname = image_partner(model, name)
        partner = form[pname] if pname and pname in form.fields else None
        inst = form.instance
        file = getattr(inst, name, None)
        if file:
            try:
                preview = file.url
            except ValueError:
                preview = ""
        if not preview and pname:
            preview = getattr(inst, pname, "") or ""
    return {
        "bf": bf,
        "kind": kind,
        "wide": kind in ("textarea", "checks", "image"),
        "partner": partner,
        "preview": preview,
    }


GalleryFormSet = inlineformset_factory(
    Property, PropertyImage, fields=["image", "image_url", "order"], extra=2, can_delete=True,
)


def style_formset(formset):
    for f in formset.forms:
        for name, field in f.fields.items():
            if name == "DELETE":
                field.widget.attrs["class"] = "form-check-input"
            else:
                style_field(name, field)
    return formset
