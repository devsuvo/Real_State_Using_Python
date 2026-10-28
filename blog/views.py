from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from core.views import page_header

from .models import Category, Post


def _sidebar():
    return {
        "categories": Category.objects.annotate(n=Count("posts", filter=Q(posts__is_published=True))).filter(n__gt=0).order_by("name"),
        "recent_posts": Post.objects.published()[:4],
    }


def post_list(request):
    posts = Post.objects.published().select_related("category", "author")
    active_category = None
    if slug := request.GET.get("category"):
        active_category = Category.objects.filter(slug=slug).first()
        posts = posts.filter(category__slug=slug)
    if q := request.GET.get("q", "").strip():
        posts = posts.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(body__icontains=q))
    page = Paginator(posts, 6).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    context = {
        "header": page_header("blog"),
        "page_obj": page,
        "posts": page.object_list,
        "active_category": active_category,
        "query_string": params.urlencode(),
        **_sidebar(),
    }
    return render(request, "blog/post_list.html", context)


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.published().select_related("category", "author"), slug=slug)
    related = Post.objects.published().exclude(pk=post.pk)
    if post.category:
        related = related.filter(category=post.category)
    return render(request, "blog/post_detail.html", {"post": post, "related": related[:2], **_sidebar()})
