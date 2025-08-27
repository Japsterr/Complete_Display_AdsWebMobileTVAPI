from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_schedule_preempt'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('menu_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='menus', to='api.business')),
                ('personal_user', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='menus', to='api.user')),
            ],
            options={
                'db_table': 'Menus',
            },
        ),
        migrations.CreateModel(
            name='MenuCategory',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('order', models.PositiveIntegerField(default=0)),
                ('menu', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='categories', to='api.menu')),
            ],
            options={
                'db_table': 'MenuCategories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2, default=0)),
                ('currency', models.CharField(max_length=10, default='ZAR')),
                ('available', models.BooleanField(default=True)),
                ('image', models.FileField(upload_to='menus/', null=True, blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='items', to='api.menucategory')),
                ('menu', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='items', to='api.menu')),
            ],
            options={
                'db_table': 'MenuItems',
                'ordering': ['order', 'name'],
            },
        ),
    ]
