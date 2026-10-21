from django.core.management.base import BaseCommand

from blog.models import Post, Tag

TAGS = {"django": "Django", "python": "Python", "portfolio": "Portfolio"}

POSTS = [
    {
        "title": "Pourquoi j'ai choisi Django REST pour mon blog",
        "excerpt": "Retour d'expérience sur l'architecture API + frontend séparé de mon portfolio.",
        "tags": ["django", "python"],
        "content": (
            "# Un backend léger, un frontend libre\n\n"
            "Pour mon portfolio, je voulais **séparer** le contenu de l'interface. "
            "Django REST Framework expose une API JSON propre, et l'admin Django me donne "
            "gratuitement un espace de rédaction.\n\n"
            "## Ce que j'y gagne\n\n"
            "- Un modèle de données clair (articles, tags)\n"
            "- Une pagination et des filtres prêts à l'emploi\n"
            "- Un déploiement simple avec Docker\n\n"
            "```python\nclass PostViewSet(ReadOnlyModelViewSet):\n    lookup_field = 'slug'\n```\n\n"
            "Le frontend n'a plus qu'à consommer l'API."
        ),
    },
    {
        "title": "5 astuces Python que j'utilise tous les jours",
        "excerpt": "Petites habitudes qui rendent le code plus lisible et plus robuste.",
        "tags": ["python"],
        "content": (
            "# 5 astuces Python\n\n"
            "1. **f-strings** partout pour formater.\n"
            "2. `enumerate` plutôt qu'un compteur manuel.\n"
            "3. `pathlib` pour manipuler les chemins.\n"
            "4. Les *list comprehensions*, sans en abuser.\n"
            "5. `dataclasses` pour les structures simples.\n\n"
            "```python\nfrom pathlib import Path\n\nfor f in Path('.').glob('*.md'):\n    print(f.name)\n```\n"
        ),
    },
    {
        "title": "Construire un portfolio qui se démarque",
        "excerpt": "Ce que je mets en avant dans mon portfolio et pourquoi j'y tiens un blog.",
        "tags": ["portfolio"],
        "content": (
            "# Un portfolio vivant\n\n"
            "Un portfolio ne se limite pas à une liste de projets. Un **blog** montre "
            "votre façon de réfléchir, vos erreurs et ce que vous apprenez.\n\n"
            "## Mes critères\n\n"
            "- Des projets expliqués, pas seulement listés\n"
            "- Des articles courts et utiles\n"
            "- Un site rapide et accessible\n\n"
            "> Écrire, c'est apprendre deux fois."
        ),
    },
]


class Command(BaseCommand):
    help = "Crée 3 articles de démonstration (idempotent)."

    def handle(self, *args, **options):
        tags = {}
        for slug, name in TAGS.items():
            tags[slug], _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})

        created = 0
        for data in POSTS:
            post, was_created = Post.objects.get_or_create(
                title=data["title"],
                defaults={
                    "excerpt": data["excerpt"],
                    "content": data["content"],
                    "published": True,
                },
            )
            post.tags.set([tags[t] for t in data["tags"]])
            created += was_created

        self.stdout.write(self.style.SUCCESS(f"{created} article(s) créé(s), {len(POSTS) - created} déjà présent(s)."))
