from django.db import migrations, models

from news.models import archive_id


def fill(apps, schema_editor):
    FeedItem = apps.get_model('news', 'FeedItem')
    for item in FeedItem.objects.all().iterator():
        item.archive_id = archive_id(item.url)
        item.save(update_fields=['archive_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feeditem',
            name='archive_id',
            field=models.CharField(max_length=12, null=True),
        ),
        migrations.RunPython(fill, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='feeditem',
            name='archive_id',
            field=models.CharField(max_length=12, unique=True),
        ),
    ]
