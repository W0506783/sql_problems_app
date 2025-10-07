`docker-compose up -d`

Safe for data. This will start your services. If your db container already exists and is configured with a volume, it will simply restart or attach to the existing data. If it's a new db container, it will create/attach to the pg_data volume and your data will persist.

`docker-compose exec web python manage.py migrate`

Safe for data. This runs Django migrations. It modifies your database schema but doesn't delete the entire database or volume.

`docker-compose down`

Generally safe for data, as long as you have named volumes configured. docker-compose down stops and removes the containers and networks. By default, it does not remove named volumes.

`docker-compose down -v (or --volumes)`

**DANGER! This WILL delete your named volumes and all your database data! Only use this if you explicitly want to wipe your database and start fresh.**

You've hit on another excellent point that touches on a crucial aspect of application development: **managing initial or "seed" data**. Manually copying and pasting into the Django admin is definitely *not* the scalable or sustainable way to manage your problem data, especially when working across different environments or with a team.

You're absolutely right that there's a file stored with this information – your `.md` problem descriptions. The goal is to get that information **into the database reliably and automatically**, especially for new deployments or environments.

### The Problem: Initial Data / Seed Data

When you set up a new environment (like at school), you need:

1.  **Database Schema:** Handled by `manage.py migrate` (creates tables).
2.  **Basic Users:** Handled by `manage.py createsuperuser` (creates a superuser).
3.  **Core Application Data:** This is your "problem data" – the actual `Problem` instances, their associated `Schema` scripts, and `Solution` queries. This is the content that makes your application functional.

This third point is where "data seeding" comes in.

### Solutions for Data Seeding in Django


#### Django Fixtures (`manage.py loaddata`) - Good for Static Data

*   **How it works:** You export existing database data (e.g., your problems and schemas) into a file (usually JSON or YAML). This file is called a "fixture." You then load this fixture into a new database.
*   **Process:**
    1.  **Dump data (on your home machine, once data is entered):**
        ```bash
        docker-compose exec web python manage.py dumpdata practice --indent 2 > practice/fixtures/initial_problems.json
        ```
        (Replace `practice` with your app name if different. `--indent 2` makes it human-readable.)
    2.  **Add to Git:** Commit `practice/fixtures/initial_problems.json` to your repository.
    3.  **Load data (on a new machine/environment):**
        ```bash
        docker-compose exec web python manage.py loaddata initial_problems.json
        ```
*   **Pros:**
    *   Simple for static, unchanging data.
    *   Easy to manage with Git.
    *   Official Django feature.
*   **Cons:**
    *   Can become unwieldy if data changes frequently or is very large.
    *   Requires `dumpdata` and `loaddata` steps.
    *   If you change model fields, existing fixtures might become invalid and need re-dumping.
    *   Doesn't handle `OneToOneField` or complex relationships as elegantly sometimes.
    *   Doesn't integrate with Markdown files directly; you'd still copy from MD to the DB, then dump.

#### 2. Custom Management Command / Seeding Script - Recommended for Dynamic/Complex Data

*   **How it works:** You write a Python script (as a Django custom management command) that programmatically creates your `Problem`, `Schema`, and `Solution` objects. This script can read directly from your Markdown files!
*   **Process:**
    1.  **Structure your problem files:** Keep your Markdown (`.md`) files, SQL schema scripts (`.sql`), and solution queries (`.sql`) in a well-defined directory structure within your Django app. For example:
        ```
        practice/
        ├── management/
        │   └── commands/
        │       └── seed_problems.py # <--- Your custom command
        ├── problems/ # <--- New directory for problem content
        │   ├── problem_1/
        │   │   ├── description.md
        │   │   ├── schema.sql
        │   │   └── solution.sql
        │   ├── problem_2/
        │   │   ├── description.md
        │   │   ├── schema_part_1.sql
        │   │   └── schema_part_2.sql
        │   │   └── solution.sql
        │   └── problem_3/
        │       └── ...
        ```
    2.  **Write `seed_problems.py`:** This script will:
        *   Iterate through your `practice/problems/` directory.
        *   Read the contents of `description.md`, `schema.sql`, `solution.sql` for each problem.
        *   Create (or update if they already exist) `Problem`, `Schema`, and `Solution` model instances.
        *   You'll need `pathlib` for file system navigation and simple file reading.
    3.  **Run the command:**
        ```bash
        docker-compose exec web python manage.py seed_problems
        ```
*   **Pros:**
    *   Highly flexible and programmatic.
    *   **Directly reads from your source `.md` and `.sql` files**, ensuring data in the DB matches your files.
    *   Can handle updates: the script can check if a problem already exists and update it, rather than creating duplicates.
    *   Excellent for data that originates from external files or needs complex logic.
    *   Keeps your problem data (the actual content) in version control directly as files, not as a dumped database state.
*   **Cons:**
    *   More initial setup work to write the script.
    *   Requires a bit of Python code.

#### 3. Django Data Migrations (migrations that create data) - Less Common for Bulk Data

*   **How it works:** You can create "data migrations" that run Python code directly within your Django migration files.
*   **Pros:** Data is created as part of the `migrate` process itself.
*   **Cons:**
    *   Mixing data with schema migrations can get messy.
    *   Harder to update or re-run if data changes often.
    *   Not ideal for large amounts of initial data.
    *   Better for crucial, tiny pieces of initial data (e.g., initial user groups, default settings).

### My Recommendation: Custom Management Command (Solution #2)

Given your use case (problems defined in separate `.md` and `.sql` files), a **custom management command is the cleanest and most robust solution.** It ensures:

*   Your "source of truth" for problem content remains the actual files in your repository.
*   You can easily populate a fresh database on any machine by just running `python manage.py seed_problems`.
*   You can easily update existing problems by changing the files and re-running the command.

Let's quickly sketch out what that `seed_problems.py` might look like:

```python
# practice/management/commands/seed_problems.py
import os
from pathlib import Path

from django.core.management.base import BaseCommand
from practice.models import Problem, Schema, Solution # Adjust import if your models are elsewhere

class Command(BaseCommand):
    help = 'Seeds initial SQL problems, schemas, and solutions from files.'

    def handle(self, *args, **options):
        # Path to your problem definition files relative to your app directory
        problems_dir = Path(__file__).resolve().parent.parent.parent / 'problems'

        if not problems_dir.is_dir():
            self.stdout.write(self.style.ERROR(f"Problem directory not found: {problems_dir}"))
            return

        for problem_folder in problems_dir.iterdir():
            if problem_folder.is_dir():
                problem_name = problem_folder.name.replace('_', ' ').title() # E.g., 'problem_1' -> 'Problem 1'
                self.stdout.write(self.style.MIGRATE_HEADING(f"Processing problem: {problem_name}"))

                # Read description
                description_file = problem_folder / 'description.md'
                if not description_file.is_file():
                    self.stdout.write(self.style.WARNING(f"  Skipping {problem_name}: description.md not found."))
                    continue
                description_content = description_file.read_text()

                # Read solution
                solution_file = problem_folder / 'solution.sql'
                if not solution_file.is_file():
                    self.stdout.write(self.style.WARNING(f"  Skipping {problem_name}: solution.sql not found."))
                    continue
                solution_content = solution_file.read_text()

                # Create/Update Problem and Solution
                problem, created_problem = Problem.objects.update_or_create(
                    title=problem_name, # Assuming title can be derived from folder name or put in description.md
                    defaults={'prompt': description_content}
                )
                if created_problem:
                    self.stdout.write(self.style.SUCCESS(f"  Created new Problem: {problem.title}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  Updated existing Problem: {problem.title}"))

                Solution.objects.update_or_create(
                    problem=problem,
                    defaults={'query': solution_content}
                )
                self.stdout.write(self.style.SUCCESS(f"  Solution for {problem.title} seeded."))

                # Read and Create/Update Schemas
                # Assuming schema files are named schema_1.sql, schema_2.sql, etc., or just schema.sql
                # You might need more sophisticated logic here if a problem can have multiple schemas
                # and you want to distinguish them. For now, let's assume one or more schema.sql files.
                # A better approach might be to name them by their intent, e.g., 'create_users.sql', 'insert_data.sql'

                # Clear existing schemas for the problem before adding new ones, to handle updates cleanly
                problem.schema_set.all().delete()
                self.stdout.write(self.style.WARNING(f"  Cleared existing schemas for {problem.title}."))


                schema_files = sorted(problem_folder.glob('schema*.sql')) # Finds schema.sql, schema_1.sql, etc.
                if not schema_files:
                    self.stdout.write(self.style.WARNING(f"  No schema.sql files found for {problem.title}."))
                
                for schema_file in schema_files:
                    schema_content = schema_file.read_text()
                    Schema.objects.create(
                        problem=problem,
                        script=schema_content,
                        # You might want to add an order or name field to Schema model
                        # to manage multiple scripts for one problem
                        # name=schema_file.stem
                    )
                    self.stdout.write(self.style.SUCCESS(f"  Schema '{schema_file.name}' for {problem.title} seeded."))


        self.stdout.write(self.style.SUCCESS('Successfully seeded all problems!'))

```

This approach gives you a repeatable, reliable way to populate your application's core data, making new environment setups (like at school) much smoother.
Here's a visual representation of how that file structure and command would work.

