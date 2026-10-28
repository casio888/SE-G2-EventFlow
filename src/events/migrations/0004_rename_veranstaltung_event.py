from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_remove_event_timeslots_timeslot'),
    ]

    operations = [
        migrations.RenameModel(old_name='Veranstaltung', new_name='Event'),
        migrations.RenameField(model_name='event', old_name='titel', new_name='title'),
        migrations.RenameField(model_name='event', old_name='beschreibung', new_name='description'),
        migrations.RenameField(model_name='event', old_name='start_datum', new_name='start_date'),
        migrations.RenameField(model_name='event', old_name='end_datum', new_name='end_date'),
        migrations.RenameField(model_name='event', old_name='ort', new_name='location'),
        migrations.RenameField(model_name='event', old_name='erstellt_am', new_name='created_at'),
        migrations.RenameField(model_name='timeslot', old_name='veranstaltung', new_name='event'),
        migrations.RenameField(model_name='timeslot', old_name='ende', new_name='end'),
        migrations.RenameField(model_name='timeslot', old_name='dauer', new_name='duration'),
        migrations.RenameField(model_name='timeslot', old_name='kategorie', new_name='category'),
    ]
