from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from django_q.models import Task, OrmQ  # Temporarily disabled
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q as QFilter
import logging

logger = logging.getLogger(__name__)


@login_required
def email_task_dashboard(request):
    """Dashboard showing queued email tasks and monitoring"""
    
    # Get email-related tasks from django_q
    all_tasks = Task.objects.all().order_by('-created')
    
    # Filter email tasks (tasks that send emails)
    email_tasks = all_tasks.filter(
        func__in=[
            'payments.tasks.send_payment_confirmation_email',
            'payments.tasks.send_payment_cancelled_email'
        ]
    )
    
    # Calculate statistics
    today = timezone.now()
    week_ago = today - timedelta(days=7)
    
    total_email_tasks = email_tasks.count()
    completed_tasks = email_tasks.filter(stopped__isnull=False).count()
    failed_tasks = email_tasks.filter(failed=True).count()
    pending_tasks = email_tasks.filter(stopped__isnull=True, failed=False).count()
    
    # Tasks sent today
    tasks_today = email_tasks.filter(created__gte=today.replace(hour=0, minute=0, second=0))
    
    # Tasks sent this week
    tasks_this_week = email_tasks.filter(created__gte=week_ago)
    
    # Recent tasks
    recent_tasks = email_tasks.order_by('-created')[:20]
    
    # Task execution stats
    avg_execution_time = 0
    if completed_tasks > 0:
        successful_tasks = email_tasks.filter(stopped__isnull=False, failed=False)
        total_time = sum([
            (task.stopped - task.created).total_seconds() 
            for task in successful_tasks if task.stopped
        ])
        avg_execution_time = total_time / completed_tasks if completed_tasks > 0 else 0
    
    # Hourly distribution (last 24 hours)
    hourly_data = {}
    for i in range(24):
        hour_start = today.replace(hour=i, minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        count = email_tasks.filter(
            created__gte=hour_start,
            created__lt=hour_end
        ).count()
        hourly_data[f"{i:02d}:00"] = count
    
    context = {
        'total_email_tasks': total_email_tasks,
        'completed_tasks': completed_tasks,
        'failed_tasks': failed_tasks,
        'pending_tasks': pending_tasks,
        'tasks_today': tasks_today.count(),
        'tasks_this_week': tasks_this_week.count(),
        'recent_tasks': recent_tasks,
        'avg_execution_time': round(avg_execution_time, 2),
        'hourly_data': hourly_data,
    }
    
    return render(request, 'payments/email_dashboard.html', context)


@login_required
def retry_failed_email_task(request, task_id):
    """Retry a failed email task"""
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST
    
    if request.method != 'POST':
        return JsonResponse({'status': False, 'message': 'POST required'}, status=400)
    
    try:
        task = Task.objects.get(id=task_id)
        
        if not task.failed:
            return JsonResponse({'status': False, 'message': 'Task did not fail'}, status=400)
        
        # Re-enqueue the task
        from django_q.tasks import async_task
        
        # Parse original task data
        func_name = task.func
        args = eval(task.args) if task.args else ()
        kwargs = eval(task.kwargs) if task.kwargs else {}
        
        new_task_id = async_task(func_name, *args, **kwargs)
        
        logger.info(f"Retried email task {task_id} -> new task {new_task_id}")
        
        return JsonResponse({
            'status': True,
            'message': 'Task re-queued successfully',
            'new_task_id': new_task_id
        })
    
    except Task.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Task not found'}, status=404)
    except Exception as e:
        logger.error(f"Error retrying task {task_id}: {str(e)}")
        return JsonResponse({'status': False, 'message': str(e)}, status=500)
