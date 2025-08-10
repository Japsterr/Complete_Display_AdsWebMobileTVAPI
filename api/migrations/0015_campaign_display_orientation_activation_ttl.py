from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_tag_displaygroup_mediaapproval'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='normalize_to_orientation',
            field=models.CharField(choices=[('none', 'None'), ('portrait', 'Portrait'), ('landscape', 'Landscape')], default='none', help_text='Playback hint: normalize media to this orientation at display time', max_length=10),
        ),
        migrations.AddField(
            model_name='display',
            name='activation_code_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
