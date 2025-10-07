# practice/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection, transaction, Error
from django.contrib import messages
from .models import Problem # Make sure Problem, Schema, Solution are imported

def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)

    context = {
        'problem': problem,
        'user_query': request.session.pop('user_query', ''),
        'query_results': None,
        'column_headers': [],
        'query_error': None,
    }

    if request.method != 'POST':
        return render(request, 'practice/problem_detail.html', context)

    # --- DEBUGGING ADDITIONS START ---
    print(f"\n--- DEBUGGING POST REQUEST for problem_id={problem_id} ---")
    print(f"Full request.POST data: {request.POST}")
    print(f"request.POST.get('user_query'): {request.POST.get('user_query')}")
    # --- DEBUGGING ADDITIONS END ---

    user_query = request.POST.get('user_query', '').strip()

    # --- MORE DEBUGGING ADDITIONS ---
    print(f"user_query (after .strip()): '{user_query}'")
    if not user_query:
        print("WARNING: user_query is empty after stripping whitespace!")
    # --- END MORE DEBUGGING ADDITIONS ---

    action = request.POST.get('action')

    # --- BRANCH 1: User clicked "Run Query" ---
    if action == 'run':
        context.update({'user_query': user_query})
        
        # Initial check for empty query
        if not user_query:
            context['query_error'] = "Cannot execute an empty query."
            print("Returning from 'run' action due to empty query (initial check).")
            return render(request, 'practice/problem_detail.html', context)

        try:
            with transaction.atomic():
                # Use a separate cursor for schema setup
                with connection.cursor() as schema_cursor:
                    print("Executing schema scripts...")
                    if not problem.schemas.exists():
                        print("WARNING: No schema scripts found for this problem.")
                    for schema_sql in problem.schemas.all():
                        print(f"  Attempting to execute schema script (Order {schema_sql.order}):")
                        print(f"  --- START SCHEMA SCRIPT ---")
                        print(schema_sql.script) # PRINT THE FULL SCRIPT HERE
                        print(f"  --- END SCHEMA SCRIPT ---")
                        
                        # Strip and check length before execution for more robust debugging
                        stripped_script = schema_sql.script.strip()
                        print(f"  Script length (stripped): {len(stripped_script)}") 
                        
                        if not stripped_script:
                            # Instead of raising Error, which might be too abrupt, let's make it a more specific message
                            # and ensure it's caught by the outer try-except for display.
                            raise ValueError(f"Schema script (Order {schema_sql.order}) is empty or whitespace only!")
                            
                        schema_cursor.execute(stripped_script) # Execute the stripped script
                        print(f"  SUCCESSFULLY Executed schema script (Order {schema_sql.order}).")
                
                # Use a fresh cursor for the user's query
                with connection.cursor() as user_query_cursor:
                    print(f"Executing user_query: '{user_query}'")
                    user_query_cursor.execute(user_query) 
                    
                    context['query_results'] = user_query_cursor.fetchall()
                    context['column_headers'] = [col[0] for col in user_query_cursor.description] if user_query_cursor.description else []
                
                print("User query executed successfully, rendering results.")
                return render(request, 'practice/problem_detail.html', context)
        
        except (Error, ValueError) as e: # Catch ValueError too now
            context['query_error'] = str(e)
            print(f"Database Error during 'run' action: {e}")
            return render(request, 'practice/problem_detail.html', context)
        except Exception as e: # Catch any other unexpected errors
            context['query_error'] = f"An unexpected application error occurred during 'run': {e}"
            print(f"An unexpected application error occurred during 'run' action: {e}")
            return render(request, 'practice/problem_detail.html', context)

    # --- BRANCH 2: User clicked "Submit Solution" ---
    elif action == 'submit':
        request.session['user_query'] = user_query
        
        if not user_query:
            messages.error(request, "Cannot submit an empty query.")
            print("Redirecting from 'submit' action due to empty query (initial check).")
            return redirect('practice:problem_detail', problem_id=problem.id)

        try:
            with transaction.atomic():
                # Separate cursor for schema setup
                with connection.cursor() as schema_cursor:
                    print("Executing schema scripts for submission...")
                    if not problem.schemas.exists():
                        print("WARNING: No schema scripts found for this problem for submission.")
                    for schema_sql in problem.schemas.all():
                        stripped_script = schema_sql.script.strip()
                        if not stripped_script:
                            raise ValueError(f"Schema script (Order {schema_sql.order}) is empty or whitespace only for submission!")
                        schema_cursor.execute(stripped_script)
                        print(f"  Executed schema script for submission (Order {schema_sql.order}).")

                # Fresh cursor for user's query
                with connection.cursor() as user_query_cursor:
                    print(f"Executing user's submission query: '{user_query}'")
                    user_query_cursor.execute(user_query)
                    user_results = user_query_cursor.fetchall()

                # Fresh cursor for solution query
                if not hasattr(problem, 'solution') or not problem.solution.query:
                    messages.error(request, "This problem does not have a solution configured yet.")
                    print("Solution not configured, redirecting.")
                    return redirect('practice:problem_detail', problem_id=problem.id)

                with connection.cursor() as solution_cursor:
                    print(f"Executing solution query: '{problem.solution.query}'")
                    solution_cursor.execute(problem.solution.query)
                    solution_results = solution_cursor.fetchall()
                
                if user_results == solution_results:
                    messages.success(request, 'Correct! Your solution is accurate.')
                    print("Solution is correct!")
                else:
                    messages.error(request, 'Incorrect. The results did not match the expected solution.')
                    print("Solution is incorrect.")
        
        except (Error, ValueError) as e: # Catch ValueError here too
            messages.error(request, f"Database Error: {e}")
            print(f"Database Error during 'submit' action: {e}")
        
        except Exception as e:
            messages.error(request, f"An unexpected application error occurred: {e}")
            print(f"An unexpected application error occurred during 'submit' action: {e}")
        
        return redirect('practice:problem_detail', problem_id=problem.id)

    print("Reached end of view, redirecting.")
    return redirect('practice:problem_detail', problem_id=problem.id)