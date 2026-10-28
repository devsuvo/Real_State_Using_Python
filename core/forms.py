from django import forms

from .models import ContactMessage, Subscriber


class HoneypotMixin(forms.Form):
    """Hidden field bots tend to fill in; humans never see it."""

    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""


def _style(form):
    for name, field in form.fields.items():
        if name == "website":
            continue
        css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
        field.widget.attrs.setdefault("class", css)
        if field.label and not isinstance(field.widget, forms.Select):
            field.widget.attrs.setdefault("placeholder", field.label)


class ContactForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        labels = {"name": "Full name", "email": "Email address", "phone": "Phone number"}
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].required = True
        _style(self)


class InquiryForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        labels = {"name": "Your name", "email": "Your email", "phone": "Your phone"}
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].required = True
        _style(self)


class LeadForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone"]
        labels = {"name": "Your name", "email": "Email address", "phone": "Phone (optional)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)


class SubscribeForm(forms.Form):
    email = forms.EmailField()

    def save(self):
        return Subscriber.objects.get_or_create(email=self.cleaned_data["email"].lower())
