from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.promotions.models import StorySubmission


class Command(BaseCommand):
    help = 'Un-feature published stories whose promotion period has ended.'

    def handle(self, *args, **options):
        now = timezone.now()
        expired = StorySubmission.objects.filter(
            status=StorySubmission.Status.PUBLISHED,
            featured_until__lt=now,
            published_post__isnull=False,
            published_post__is_featured=True,
        ).select_related('published_post')

        n = 0
        for sub in expired:
            post = sub.published_post
            post.is_featured = False
            post.save(update_fields=['is_featured'])
            n += 1

        self.stdout.write(self.style.SUCCESS(f'Un-featured {n} expired story(ies).'))
