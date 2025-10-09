# practice/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection, transaction, Error
from django.contrib import messages
from .models import Problem # Make sure Problem, Schema, Solution are imported

def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)

    # Initialize context that will be used for rendering the template
    context = {
        'problem': problem,
        'user_query': request.session.pop('user_query', ''), # Get query from session if it exists
        'query_results': None,
        'column_headers': [],
        'query_error': None,
    }

    # If it's a GET request, just render the page
    if request.method != 'POST':
        return render(request, 'practice/problem_detail.html', context)

    # --- POST REQUEST LOGIC ---

    user_query = request.POST.get('user_query', '').strip()
    context['user_query'] = user_query # Add user query to context to re-populate editor

    # Validate that the query is a SELECT or WITH statement
    user_query_lower = user_query.lower()
    if not (user_query_lower.startswith('select') or user_query_lower.startswith('with')):
        messages.error(request, "Only SELECT queries (including those starting with WITH) are allowed.")
        # On validation error, we redirect to clear the POST
        return redirect('practice:problem_detail', problem_id=problem.id)

    action = request.POST.get('action')

    # --- BRANCH 1: User clicked "Run Query" ---
    if action == 'run':
        if not user_query:
            context['query_error'] = "Cannot execute an empty query."
            return render(request, 'practice/problem_detail.html', context)

        try:
            # Use a transaction to ensure schema setup and query run are atomic
            with transaction.atomic():
                # Execute all schema scripts for this problem
                with connection.cursor() as schema_cursor:
                    for schema_sql in problem.schemas.all():
                        schema_cursor.execute(schema_sql.script.strip())
                
                # Execute the user's query
                with connection.cursor() as user_query_cursor:
                    user_query_cursor.execute(user_query)
                    context['query_results'] = user_query_cursor.fetchall()
                    context['column_headers'] = [col[0] for col in user_query_cursor.description] if user_query_cursor.description else []
                
                # Re-render the page with the results
                return render(request, 'practice/problem_detail.html', context)
        
        except Error as e:
            context['query_error'] = str(e)
            return render(request, 'practice/problem_detail.html', context)
        except Exception as e:
            context['query_error'] = f"An unexpected application error occurred: {e}"
            return render(request, 'practice/problem_detail.html', context)

    # --- BRANCH 2: User clicked "Submit Solution" ---
    elif action == 'submit':
        if not user_query:
            # For submit, a simple message and redirect is fine for an empty query
            messages.error(request, "Cannot submit an empty query.")
            return redirect('practice:problem_detail', problem_id=problem.id)

        try:
            with transaction.atomic():
                # Set up the schema in the database
                with connection.cursor() as schema_cursor:
                    for schema_sql in problem.schemas.all():
                        schema_cursor.execute(schema_sql.script.strip())

                # Execute the user's query and fetch their results
                with connection.cursor() as user_query_cursor:
                    user_query_cursor.execute(user_query)
                    user_results = user_query_cursor.fetchall()
                    # *** IMPORTANT: Capture user's headers to display results ***
                    user_column_headers = [col[0] for col in user_query_cursor.description] if user_query_cursor.description else []

                # Check if a solution is configured for this problem
                if not hasattr(problem, 'solution') or not problem.solution.query:
                    messages.error(request, "This problem does not have a solution configured yet.")
                    return redirect('practice:problem_detail', problem_id=problem.id)

                # Execute the official solution query and fetch its results
                with connection.cursor() as solution_cursor:
                    solution_cursor.execute(problem.solution.query)
                    solution_results = solution_cursor.fetchall()
                
                # Compare the results (sorting them ensures order doesn't matter)
                if sorted(user_results) == sorted(solution_results):
                    messages.success(request, 'Correct! Your solution is accurate.')
                    # *** On success, add the user's results to the context to be displayed ***
                    context['query_results'] = user_results
                    context['column_headers'] = user_column_headers
                else:
                    messages.error(request, 'Incorrect. The results did not match the expected solution.')
                    # *** On incorrect, ALSO show their results so they can debug ***
                    context['query_results'] = user_results
                    context['column_headers'] = user_column_headers
            
            # *** RENDER THE TEMPLATE with the messages and results context ***
            return render(request, 'practice/problem_detail.html', context)

        except Error as e: 
            # If a database error happens during submission, display it in the results area
            context['query_error'] = str(e)
            return render(request, 'practice/problem_detail.html', context)
        
        except Exception as e:
            # Handle any other unexpected application errors
            context['query_error'] = f"An unexpected application error occurred: {e}"
            return render(request, 'practice/problem_detail.html', context)

    # Fallback redirect if no action is specified
    return redirect('practice:problem_detail', problem_id=problem.id)