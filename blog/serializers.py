from rest_framework import serializers

from .models import Post, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name", "slug")


class PostListSerializer(serializers.ModelSerializer):
    """Version allégée (sans `content`) pour la liste."""

    tags = TagSerializer(many=True, read_only=True)
    # ImageField renvoie une URL absolue grâce au `request` du contexte.
    cover = serializers.ImageField(read_only=True)

    class Meta:
        model = Post
        fields = ("title", "slug", "excerpt", "cover", "tags", "created_at", "reading_time")


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ("content", "updated_at")
