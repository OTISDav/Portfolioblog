import math
import re

from django.db import models
from django.utils.text import slugify

WORDS_PER_MINUTE = 200


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="Généré automatiquement depuis le titre si laissé vide.",
    )
    excerpt = models.CharField(max_length=300)
    content = models.TextField(help_text="Contenu au format Markdown.")
    cover = models.ImageField(upload_to="covers/%Y/%m/", blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reading_time = models.PositiveIntegerField(
        default=1, editable=False, help_text="Minutes (calculé automatiquement)."
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def _generate_unique_slug(self):
        base = slugify(self.title)[:200] or "article"
        slug, n = base, 2
        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    def _compute_reading_time(self):
        words = len(re.findall(r"\w+", self.content or ""))
        return max(1, math.ceil(words / WORDS_PER_MINUTE))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        self.reading_time = self._compute_reading_time()
        super().save(*args, **kwargs)
