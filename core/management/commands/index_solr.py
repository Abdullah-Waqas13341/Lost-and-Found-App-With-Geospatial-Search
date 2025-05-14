
import requests
from django.core.management.base import BaseCommand
from core.models import LostItem

# Define the mapping for locations and their corresponding Solr cores
LOCATION_CORE_MAP = {
    'server1': ['seeecs', 'c2', 'nbs'],
    'server2': ['nice', 'ric'],
    'server3': ['smme', 'sports_complex', 'swimming_pool', 'c4'],
    'server4': ['scme', 'c1', 'igs', 'sada', 'nbs_ground', 'helipad_ground'],
    'server5': ['library', 'masjid', 'rims', 'iaec'],
    'server6': ['south_edge_cafe', 'main_office', 'library_lawn', 'convocation_ground'],
    'server7': ['gate1', 'gate2', 'gate10'],
    'male_hostels': [
        'rumi_hostel', 'johar_hostel', 'ghazali_hostel', 'beruni_hostel',
        'razi_hostel', 'rahmat_hostel', 'attar_hostel', 'liaquat_hostel',
        'hajveri_hostel', 'zakariya_hostel'
    ],
    'female_hostels': [
        'fatima_block1_pg', 'fatima_block2_pg', 'fatima_block1_ug',
        'zainab_hostel', 'ayesha_hostel', 'khadija_hostel', 'amna_hostel'
    ]
}

class Command(BaseCommand):
    help = 'Index lost items to Solr based on their location.'

    def handle(self, *args, **options):
        items = LostItem.objects.all()
        indexed_count = 0
        skipped_count = 0

        for item in items:
            # Use lowercased location text for matching to avoid case sensitivity issues
            location_text = item.location_text.lower()
            core_found = False

            # Check each server/core mapping
            for core, locations in LOCATION_CORE_MAP.items():
                if any(location in location_text for location in locations):
                    solr_url = f'http://localhost:8983/solr/{core}/update/json/docs?commit=true'
                    doc = {
                        'id': item.id,
                        'title': item.title,
                        'description': item.description,
                        'category': item.category,
                        'location': item.location_text,
                        'status': item.status,
                        'reported_at': item.reported_at.isoformat(),
                    }
                    # Send the data to Solr for indexing
                    try:
                        response = requests.post(solr_url, json=[doc])
                        if response.status_code == 200:
                            indexed_count += 1
                        else:
                            skipped_count += 1
                            self.stdout.write(self.style.WARNING(f"Failed to index item '{item.title}' to Solr at {solr_url}"))
                    except Exception as e:
                        skipped_count += 1
                        self.stdout.write(self.style.WARNING(f"Error indexing item '{item.title}': {str(e)}"))
                    core_found = True
                    break  # Stop checking other cores once a match is found

            if not core_found:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Skipping: {item.title} - Unknown location '{item.location_text}'"))

        # Provide a summary of the results
        self.stdout.write(self.style.SUCCESS(f"Successfully indexed {indexed_count} items to Solr."))
        self.stdout.write(self.style.SUCCESS(f"Skipped {skipped_count} items due to location mismatches or errors."))
