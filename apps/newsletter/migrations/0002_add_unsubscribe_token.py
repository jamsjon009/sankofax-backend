import uuid
from django.db import migrations, models


def populate_tokens(apps, schema_editor):
    Subscriber = apps.get_model('newsletter', 'Subscriber')
    for sub in Subscriber.objects.all():
        sub.unsubscribe_token = uuid.uuid4()
        sub.save(update_fields=['unsubscribe_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='unsubscribe_token',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.RunPython(populate_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='subscriber',
            name='unsubscribe_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
