# Generated manually for Department model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_alter_brand_options_alter_category_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('image', models.CharField(blank=True, max_length=255)),
                ('order_position', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order_position', 'name'],
            },
        ),
        migrations.AddField(
            model_name='category',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='catalog.department'),
        ),
        migrations.AddField(
            model_name='category',
            name='order_position',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order_position', 'name'], 'verbose_name_plural': 'Categories'},
        ),
    ]
