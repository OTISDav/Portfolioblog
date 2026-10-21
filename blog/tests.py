import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APITestCase

from .models import Post, Tag


class BlogAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.django_tag = Tag.objects.create(name="Django", slug="django")
        cls.react_tag = Tag.objects.create(name="React", slug="react")

        cls.post1 = Post.objects.create(
            title="Mon premier article", excerpt="Intro Django", content="Du **Markdown** " * 10,
            published=True,
        )
        cls.post1.tags.add(cls.django_tag)

        cls.post2 = Post.objects.create(
            title="Article React", excerpt="Intro React", content="Hooks et composants",
            published=True,
        )
        cls.post2.tags.add(cls.react_tag)

        cls.draft = Post.objects.create(
            title="Brouillon secret", excerpt="Pas public", content="Brouillon", published=False
        )

    def test_list_only_published_without_content(self):
        res = self.client.get(reverse("post-list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 2)
        slugs = [p["slug"] for p in res.data["results"]]
        self.assertNotIn(self.draft.slug, slugs)
        first = res.data["results"][0]
        self.assertNotIn("content", first)
        self.assertEqual(
            set(first), {"title", "slug", "excerpt", "cover", "tags", "created_at", "reading_time"}
        )

    def test_list_ordered_newest_first(self):
        res = self.client.get(reverse("post-list"))
        self.assertEqual(res.data["results"][0]["slug"], self.post2.slug)

    def test_detail_has_content(self):
        res = self.client.get(reverse("post-detail", kwargs={"slug": self.post1.slug}))
        self.assertEqual(res.status_code, 200)
        self.assertIn("content", res.data)
        self.assertEqual(res.data["tags"][0]["slug"], "django")

    def test_unpublished_post_is_404(self):
        res = self.client.get(reverse("post-detail", kwargs={"slug": self.draft.slug}))
        self.assertEqual(res.status_code, 404)

    def test_filter_by_tag(self):
        res = self.client.get(reverse("post-list"), {"tag": "django"})
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["slug"], self.post1.slug)

    def test_search(self):
        res = self.client.get(reverse("post-list"), {"search": "Hooks"})
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["slug"], self.post2.slug)

    def test_tags_list(self):
        res = self.client.get(reverse("tag-list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)

    def test_sitemap(self):
        res = self.client.get(reverse("sitemap"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(set(res.data[0]), {"slug", "updated_at"})

    def test_write_methods_not_allowed(self):
        res = self.client.post(reverse("post-list"), {"title": "x"})
        self.assertEqual(res.status_code, 405)


class PostModelTests(APITestCase):
    def test_slug_is_unique_and_auto(self):
        a = Post.objects.create(title="Même titre", excerpt="a", content="a")
        b = Post.objects.create(title="Même titre", excerpt="b", content="b")
        self.assertEqual(a.slug, "meme-titre")
        self.assertEqual(b.slug, "meme-titre-2")

    def test_reading_time(self):
        short = Post.objects.create(title="Court", excerpt="a", content="un deux trois")
        long = Post.objects.create(title="Long", excerpt="a", content="mot " * 450)
        self.assertEqual(short.reading_time, 1)
        self.assertEqual(long.reading_time, 3)


class CoverAbsoluteURLTests(APITestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)

    def test_cover_is_absolute_url(self):
        with override_settings(MEDIA_ROOT=self.media):
            buf = BytesIO()
            Image.new("RGB", (4, 4), "red").save(buf, format="PNG")
            post = Post.objects.create(
                title="Avec cover", excerpt="a", content="a", published=True,
                cover=SimpleUploadedFile("c.png", buf.getvalue(), content_type="image/png"),
            )
            res = self.client.get(reverse("post-detail", kwargs={"slug": post.slug}))
            self.assertTrue(res.data["cover"].startswith("http://testserver/media/covers/"))
