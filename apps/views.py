from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.core.management import call_command
from django.db import transaction
from io import StringIO

from .models import App
from .forms import AddAppForm, EditAppForm, CustomUserCreationForm


def login(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('app_list')  # Redirect to a logged-in user view
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created!')
            return redirect('login')
        else:
            messages.error(request, 'An error has been occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'register.html', context)


def logout(request):
    auth_logout(request)
    return redirect('login')


@login_required
def app_list(request):
    apps = App.objects.filter(uploaded_by=request.user)
    return render(request, 'app_list.html', {'apps': apps})


@login_required
def app_detail(request, pk):
    app = get_object_or_404(App, pk=pk, uploaded_by=request.user)
    return render(request, 'app_detail.html', {'app': app})


@login_required
def app_add(request):
    if request.method == "POST":
        form = AddAppForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    app = form.save(commit=False)
                    app.uploaded_by = request.user
                    app.save()
                    return redirect('app_detail', pk=app.pk)
            except Exception as e:
                # Handle the exception as needed, e.g., log it
                form.add_error(None, str(e))
    else:
        form = AddAppForm()
    return render(request, 'app_form.html', {'form': form})


def run_appium_test(request, app_id):
    try:
        # Capture the command output
        out = StringIO()
        err = StringIO()

        call_command('run_appium_test', app_id, stdout=out, stderr=err)

        error = err.getvalue().strip()

        if error:
            messages.error(request, f'Test Failed: {str(error)}')
        else:
            messages.success(request, f'Test Finished Successfully')

        return redirect('app_detail', pk=app_id)
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")
        return redirect('app_detail', pk=app_id)


@login_required
def app_edit(request, pk):
    app = get_object_or_404(App, pk=pk, uploaded_by=request.user)
    if request.method == "POST":
        form = EditAppForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            try:
                with transaction.atomic():
                    app = form.save(commit=False)
                    # Only update file fields if new files are provided
                    if 'apk_file_path' in request.FILES:
                        app.apk_file_path = request.FILES['apk_file_path']
                    if 'first_screen_screenshot_path' in request.FILES:
                        app.first_screen_screenshot_path = request.FILES['first_screen_screenshot_path']
                    if 'second_screen_screenshot_path' in request.FILES:
                        app.second_screen_screenshot_path = request.FILES['second_screen_screenshot_path']
                    app.save()
                    return redirect('app_detail', pk=app.pk)
            except Exception as e:
                # Handle the exception as needed, e.g., log it
                form.add_error(None, str(e))
    else:
        form = EditAppForm(instance=app)
    return render(request, 'app_form.html', {'form': form})


@login_required
def app_delete(request, pk):
    app = get_object_or_404(App, pk=pk, uploaded_by=request.user)
    if request.method == "POST":
        # Delete associated files
        if app.apk_file_path:
            default_storage.delete(app.apk_file_path.name)
        if app.first_screen_screenshot_path:
            default_storage.delete(app.first_screen_screenshot_path.name)
        if app.second_screen_screenshot_path:
            default_storage.delete(app.second_screen_screenshot_path.name)
        if app.video_recording_path:
            default_storage.delete(app.video_recording_path.name)

        # Delete the App instance
        app.delete()
        return redirect('app_list')

    return render(request, 'app_confirm_delete.html', {'app': app})
