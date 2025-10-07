# --- START OF FILE practice/management/commands/seed_problems.py ---

import os
from pathlib import Path

from django.core.management.base import BaseCommand
from practice.models import Problem, Schema, Solution

class Command(BaseCommand):
    help = 'Seeds initial SQL problems, schemas, and solutions from structured files.'

    def handle(self, *args, **options):
        # Adjusting the path for Docker context or local runs if needed
        # Assuming 'problems' directory is sibling to 'practice' app directory
        # If running from app root, it should be 'practice/problems'
        # If running from project root, it should be 'practice/problems'
        # Let's try to make this robust:
        
        # This resolves to your 'practice' app directory, then navigates to 'problems'
        # If your 'problems' directory is directly under your Django project root, adjust this.
        # Assuming structure: your_project_root/practice/problems/
        problems_dir = Path(__file__).resolve().parent.parent.parent / 'problems'

        # --- DEBUG: Print the resolved path to problems_dir ---
        self.stdout.write(self.style.NOTICE(f"Resolved problems directory: {problems_dir}"))

        if not problems_dir.is_dir():
            self.stdout.write(self.style.ERROR(f"Problem definitions directory NOT FOUND at: {problems_dir}"))
            self.stdout.write(self.style.ERROR("Please ensure 'problems' directory is correctly placed relative to the 'practice' app."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("Starting problem data seeding..."))

        for problem_folder in sorted(problems_dir.iterdir()):
            if problem_folder.is_dir():
                problem_title = problem_folder.name.replace('_', ' ').title()
                self.stdout.write(self.style.MIGRATE_HEADING(f"\nProcessing problem: {problem_title}"))

                # --- 1. Read Problem Description ---
                description_file = problem_folder / 'description.md'
                description_content = ""
                if description_file.is_file():
                    description_content = description_file.read_text(encoding='utf-8')
                    self.stdout.write(self.style.NOTICE(f"  Found description.md for '{problem_title}'. Length: {len(description_content)} chars."))
                else:
                    self.stdout.write(self.style.ERROR(f"  ERROR: description.md NOT FOUND for '{problem_title}'. Description will be empty."))
                    continue

                # --- 2. Read Solution Explanation ---
                explanation_file = problem_folder / 'solution_explanation.md'
                explanation_content = ""
                if explanation_file.is_file():
                    explanation_content = explanation_file.read_text(encoding='utf-8')
                    self.stdout.write(self.style.NOTICE(f"  Found solution_explanation.md for '{problem_title}'. Length: {len(explanation_content)} chars."))
                else:
                    self.stdout.write(self.style.WARNING(f"  solution_explanation.md not found for '{problem_title}'. Solution explanation will be empty."))

                # --- 3. Read Solution Query ---
                solution_file = problem_folder / 'solution.sql'
                solution_content = ""
                if solution_file.is_file():
                    solution_content = solution_file.read_text(encoding='utf-8')
                    self.stdout.write(self.style.NOTICE(f"  Found solution.sql for '{problem_title}'. Length: {len(solution_content)} chars."))
                else:
                    self.stdout.write(self.style.ERROR(f"  ERROR: solution.sql NOT FOUND for '{problem_title}'. Skipping problem."))
                    continue

                # --- 4. Create/Update Problem and Solution Instances ---
                problem, created_problem = Problem.objects.update_or_create(
                    title=problem_title,
                    defaults={
                        'description': description_content,
                        'solution_explanation': explanation_content,
                    }
                )
                if created_problem:
                    self.stdout.write(self.style.SUCCESS(f"  Created new Problem: '{problem.title}'"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  Updated existing Problem: '{problem.title}'"))

                Solution.objects.update_or_create(
                    problem=problem,
                    defaults={
                        'query': solution_content
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"  Solution for '{problem.title}' seeded/updated."))

                # --- 5. Handle Schema Scripts ---
                problem.schemas.all().delete()
                self.stdout.write(self.style.WARNING(f"  Cleared existing schemas for '{problem.title}'."))

                schema_files = sorted(problem_folder.glob('schema*.sql'))

                if not schema_files:
                    self.stdout.write(self.style.WARNING(f"  No 'schema*.sql' files found for '{problem_title}'."))

                for idx, schema_file in enumerate(schema_files):
                    # --- DEBUG: Print schema file path and content before saving ---
                    self.stdout.write(self.style.NOTICE(f"  Processing schema file: {schema_file.name} at path: {schema_file}"))
                    
                    schema_script_content = schema_file.read_text(encoding='utf-8')
                    
                    self.stdout.write(self.style.NOTICE(f"  Read schema content (length: {len(schema_script_content)}):"))
                    self.stdout.write(self.style.NOTICE(f"  --- START RAW SCHEMA CONTENT ---"))
                    self.stdout.write(self.style.NOTICE(schema_script_content.strip())) # Print stripped content for readability
                    self.stdout.write(self.style.NOTICE(f"  --- END RAW SCHEMA CONTENT ---"))
                    
                    if not schema_script_content.strip(): # Check if content is truly empty
                        self.stdout.write(self.style.ERROR(f"  ERROR: Schema file '{schema_file.name}' is empty or only whitespace!"))
                        continue # Skip this schema if it's empty

                    Schema.objects.create(
                        problem=problem,
                        script=schema_script_content,
                        order=idx
                    )
                    self.stdout.write(self.style.SUCCESS(f"  Added schema script: '{schema_file.name}' for '{problem.title}' (Order: {idx})."))

        self.stdout.write(self.style.SUCCESS('\nFinished seeding all problems!'))