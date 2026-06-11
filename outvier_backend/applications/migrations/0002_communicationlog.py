from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunicationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salesforce_task_id', models.CharField(max_length=100, unique=True)),
                ('log_type', models.CharField(
                    choices=[('call', 'Call'), ('email', 'Email'), ('note', 'Note'), ('other', 'Other')],
                    default='other',
                    max_length=10,
                )),
                ('subject', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('activity_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('application', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='communication_logs',
                    to='applications.application',
                )),
            ],
            options={
                'db_table': 'communication_logs',
                'ordering': ['-activity_date', '-created_at'],
            },
        ),
    ]
