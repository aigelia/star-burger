from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('geolocations', '0003_remove_location_foodcartapp_lat_cc2ff7_idx_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE geolocations_location (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lng NUMERIC(9,6) NOT NULL,
                lat NUMERIC(9,6) NOT NULL,
                address VARCHAR(255) UNIQUE NULL
            );
            """
        ),
    ]
