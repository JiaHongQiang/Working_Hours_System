# Generated migration for SystemConfig model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),  # 根据实际情况调整
    ]

    operations = [
        migrations.CreateModel(
            name='SystemConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config_key', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='配置键')),
                ('config_value', models.TextField(verbose_name='配置值')),
                ('description', models.CharField(blank=True, default='', max_length=200, verbose_name='描述')),
                ('group', models.CharField(default='general', max_length=50, verbose_name='分组')),
                ('is_active', models.BooleanField(default=True, verbose_name='启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '系统配置',
                'verbose_name_plural': '系统配置',
                'db_table': 'system_config',
                'ordering': ['group', 'config_key'],
            },
        ),
        # 插入初始数据
        migrations.RunPython(
            code=lambda apps, schema_editor: [
                apps.get_model('core', 'SystemConfig').objects.create(
                    config_key='system_name',
                    config_value='考勤系统',
                    description='系统中文名称',
                    group='public',
                    is_active=True
                ),
                apps.get_model('core', 'SystemConfig').objects.create(
                    config_key='system_name_en',
                    config_value='Attendance System',
                    description='系统英文名称',
                    group='public',
                    is_active=True
                ),
            ],
            reverse_code=migrations.RunPython.noop,
        ),
    ]
