# Generated by Django 3.2 on 2021-05-18 21:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0004_auto_20210518_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesection',
            name='ref_category',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='my_app.sectioncategory'),
        ),
        migrations.AlterField(
            model_name='filesection',
            name='ref_status',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='my_app.sectionstatus'),
        ),
        migrations.AlterField(
            model_name='filesection',
            name='ref_status_data',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='my_app.statusdata'),
        ),
    ]
