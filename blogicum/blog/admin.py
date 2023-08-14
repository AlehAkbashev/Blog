from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "title",
        "text",
        "pub_date",
        "is_published",
        "author",
        "category",
        "location",
    )

    list_editable = ("is_published", "category")
    search_fields = ("category__title", "title")
    list_filter = ("category",)
    list_display_links = ("title",)
    empty_value_display = "Не задано"


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryList(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ("title",)


admin.site.register(Location)
