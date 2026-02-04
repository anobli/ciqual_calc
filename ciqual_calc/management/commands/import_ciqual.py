import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from ciqual_calc.models import Food

class Command(BaseCommand):
    help = 'Cleans the DB and imports CIQUAL data from Excel'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CIQUAL Excel file')

    def handle(self, *args, **options):
        # 1. Load the Excel file
        self.stdout.write("Loading Excel file...")
        try:
            df = pd.read_excel(options['file_path'], sheet_name=0) 
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to read file: {e}"))
            return

        # 2. Filter out unwanted categories
        # Assuming 'alim_grp_nom_fr' is the category column
        excluded_categories = [
            'entrées et plats composés',
            'aliments infantiles',
            'eaux et autres boissons',
        ]
        if 'alim_grp_nom_fr' in df.columns:
            initial_count = len(df)

            # Filter out rows where the category is in our excluded list
            df = df[~df['alim_grp_nom_fr'].isin(excluded_categories)]

            removed_count = initial_count - len(df)
            self.stdout.write(f"Filtered out {removed_count} items (Categories: {', '.join(excluded_categories)}).")

        # 3. Dynamic Column Identification
        def find_col(keywords):
            for col in df.columns:
                if all(k.lower() in col.lower() for k in keywords):
                    return col
            return None

        col_name = 'alim_nom_fr'
        col_kcal = find_col(['Energie', 'kcal'])
        col_prot = find_col(['Protéines'])
        col_carb = find_col(['Glucides'])
        col_fat = find_col(['Lipides'])

        # 4. Atomically Clear and Rebuild
        self.stdout.write("Cleaning database and importing new data...")

        try:
            with transaction.atomic():
                # Delete all existing records
                deleted_count = Food.objects.all().delete()[0]
                self.stdout.write(f"Deleted {deleted_count} existing food items.")

                foods_to_create = []
                for _, row in df.iterrows():
                    def clean_val(val):
                        if pd.isna(val) or str(val).strip() in ['-', 'tr', '']:
                            return 0.0
                        try:
                            # Handle French comma (1,5) and "less than" signs (< 0.5)
                            s_val = str(val).replace(',', '.').replace('<', '').strip()
                            return float(s_val)
                        except ValueError:
                            return 0.0

                    food = Food(
                        name=row[col_name],
                        kcal_100g=clean_val(row.get(col_kcal, 0)),
                        protein_100g=clean_val(row.get(col_prot, 0)),
                        carbs_100g=clean_val(row.get(col_carb, 0)),
                        fat_100g=clean_val(row.get(col_fat, 0)),
                    )
                    foods_to_create.append(food)

                # Batch insert for performance
                Food.objects.bulk_create(foods_to_create)

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(foods_to_create)} items!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during import: {e}"))
