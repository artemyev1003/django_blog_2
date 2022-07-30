from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from blog.models import Post


class Command(BaseCommand):
    help = "Populates database with data"

    def handle(self, *args, **kwargs):
        fake = Faker()
        for _ in range(10):
            d = fake.unique
            Post.objects.create(
                title=d.sentence(nb_words=5),
                author=User.objects.get(id=1),
                body=d.paragraph(nb_sentences=10),
                status='published',
            )
