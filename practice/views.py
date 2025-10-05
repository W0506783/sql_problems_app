# practice/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection, transaction, Error
from django.contrib import messages
from .models import Problem

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

    user_query = request.POST.get('user_query', '')
    action = request.POST.get('action')

    # --- BRANCH 1: User clicked "Run Query" ---
    if action == 'run':
        context.update({'user_query': user_query})
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    for schema_sql in problem.schemas.all():
                        cursor.execute(schema_sql.script)
                    
                    cursor.execute(user_query)
                    
                    context['query_results'] = cursor.fetchall()
                    context['column_headers'] = [col[0] for col in cursor.description] if cursor.description else []
                
                return render(request, 'practice/problem_detail.html', context)
        
        except Error as e:
            context['query_error'] = str(e)
            return render(request, 'practice/problem_detail.html', context)

    # --- BRANCH 2: User clicked "Submit Solution" ---
    elif action == 'submit':
        request.session['user_query'] = user_query
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    for schema_sql in problem.schemas.all():
                        cursor.execute(schema_sql.script)
                    cursor.execute(user_query)
                    user_results = cursor.fetchall()

                if not hasattr(problem, 'solution') or not problem.solution.query:
                    messages.error(request, "This problem does not have a solution configured yet.")
                    # FIX: Added 'practice:' namespace
                    return redirect('practice:problem_detail', problem_id=problem.id)

                with connection.cursor() as cursor:
                    cursor.execute(problem.solution.query)
                    solution_results = cursor.fetchall()
                
                if user_results == solution_results:
                    messages.success(request, 'Correct! Your solution is accurate.')
                else:
                    messages.error(request, 'Incorrect. The results did not match the expected solution.')
        
        except Error as e:
            messages.error(request, f"Database Error: {e}")
        
        except Exception as e:
            messages.error(request, f"An unexpected application error occurred: {e}")
        
        # FIX: Added 'practice:' namespace
        return redirect('practice:problem_detail', problem_id=problem.id)

    # FIX: Added 'practice:' namespace
    return redirect('practice:problem_detail', problem_id=problem.id)