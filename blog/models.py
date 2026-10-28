from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import IMAGE_URL_HELP, pick_image
from properties.models import SlugMixin


class Category(SlugMixin):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:list") + f"?category={self.slug}"


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())


class Post(SlugMixin):
    slug_source = "title"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    author = models.ForeignKey("properties.Agent", on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    image = models.ImageField(upload_to="blog/", blank=True, verbose_name="Cover image")
    image_url = models.URLField(max_length=500, blank=True, verbose_name="Cover image link", help_text=IMAGE_URL_HELP)
    excerpt = models.CharField(max_length=300)
    body = models.TextField(help_text="Separate paragraphs with a blank line. Lines starting with '## ' become headings.")
    read_minutes = models.PositiveSmallIntegerField(default=4)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", args=[self.slug])

    @property
    def img(self):
        return pick_image(self.image, self.image_url)

    @property
    def blocks(self):
        """Split the body into simple heading / paragraph blocks for rendering."""
        out = []
        for chunk in self.body.replace("\r\n", "\n").split("\n\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            if chunk.startswith("## "):
                out.append(("h", chunk[3:].strip()))
            else:
                out.append(("p", chunk))
        return out
