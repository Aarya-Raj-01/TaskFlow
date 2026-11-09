from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Task
from .forms import CustomUserCreationForm
from .forms import TaskForm, CustomUserCreationForm



@login_required
def dashboard(request):
    tasks = Task.objects.filter(
        user=request.user
    ).order_by('-created_at')

    total = tasks.count()
    completed = tasks.filter(status='Completed').count()
    pending = tasks.filter(status='Pending').count()

    high = tasks.filter(priority='High').count()
    medium = tasks.filter(priority='Medium').count()
    low = tasks.filter(priority='Low').count()

    percentage = (
        round((completed / total) * 100) if total > 0 else 0
    )

    return render(request, 'tasks/dashboard.html', {
        'tasks': tasks,
        'total': total,
        'completed': completed,
        'pending': pending,
        'high': high,
        'medium': medium,
        'low': low,
        'percentage': percentage,
    })

@login_required
def add_task(request):
    form = TaskForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
        return redirect('dashboard')

    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def toggle_task(request, task_id):
    task = get_object_or_404(
        Task, id=task_id, user=request.user
    )

    if request.method == 'POST':
        task.status = (
            'Completed' if task.status == 'Pending' else 'Pending'
        )
        task.save()

    return redirect('dashboard')


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(
        Task, id=task_id, user=request.user
    )

    if request.method == 'POST':
        task.delete()

    return redirect('dashboard')
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(
        Task, id=task_id, user=request.user
    )

    form = TaskForm(request.POST or None, instance=task)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('dashboard')

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'editing': True
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'tasks/register.html', {
        'form': form
    })

@login_required
def delete_account(request):

    if request.method == 'POST':

        password = request.POST.get('password','')

        if request.user.check_password(password):

            user = request.user

            logout(request)
            user.delete()

            return redirect('login')

        else:
            return render(request, 'tasks/delete_account.html', {
                'error': 'Incorrect password. Please try again.'
            })

    return render(request, 'tasks/delete_account.html')