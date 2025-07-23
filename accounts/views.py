from django.shortcuts import render, redirect

def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'about.html')

def contact_us_view(request):
    return render(request, 'contact-us.html')

from .forms import SignUpForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import CourseOption, Session, Topic, Video, Exam

User = get_user_model()

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(CourseOption, id=course_id)
    # Fetch sessions, topics, videos, exams for this course
    sessions = Session.objects.filter(course=course).order_by('order')
    topics = Topic.objects.filter(session__course=course).order_by('session__order', 'order')
    videos = Video.objects.filter(topic__session__course=course)
    exams = Exam.objects.filter(topic__session__course=course)
    return render(request, 'accounts/course_detail.html', {
        'course': course,
        'sessions': sessions,
        'topics': topics,
        'videos': videos,
        'exams': exams,
    })

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.age = form.cleaned_data.get('age')
            user.help_text = form.cleaned_data.get('help_text')
            user.is_active = True  # Auto-approve all accounts
            user.save()
            messages.success(request, 'Account created successfully! An email will be sent to you for a while .')
            return render(request, 'accounts/signup_done.html')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # First check if user exists
        try:
            user = User.objects.get(username=username)
            
            # If user exists, verify password
            if user.check_password(password):
                if user.is_active:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    # Case: Account exists but not active
                    messages.error(request, 'Your account is registered but not yet activated. Please wait for admin approval.')
                    return redirect('login')
            else:
                # Incorrect password
                messages.error(request, 'Incorrect password')
        except User.DoesNotExist:
            # Username doesn't exist
            messages.error(request, 'Username is not registered')
    
    return render(request, 'accounts/login.html')


import django.db.models as models
from django.http import HttpResponse
import csv
from django.contrib.admin.views.decorators import staff_member_required

@login_required
def dashboard_view(request):
    # All course and study tracking logic removed
    return render(request, 'accounts/dashboard.html', {
        'user': request.user,
        'courses': request.user.courses.all(),
    })

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test

from django.http import JsonResponse
from django.views.decorators.http import require_GET
import re

# --- AJAX Endpoints (formerly in views_ajax.py) ---
User = get_user_model()

@require_GET
def check_username(request):
    username = request.GET.get('username', '').lower()
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})

@require_GET
def check_email(request):
    email = request.GET.get('email', '').lower()
    # Basic email format check
    if not re.match(r'^.+@.+\..+$', email):
        return JsonResponse({'exists': False, 'invalid': True})
    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists, 'invalid': False})

@require_GET
def check_student_number(request):
    student_mobile = request.GET.get('student_mobile', '').strip()
    # Normalize phone (digits only for matching)
    normalized = ''.join(filter(str.isdigit, student_mobile))
    exists = User.objects.filter(student_mobile__regex=r'\d*' + normalized + r'\d*').exists()
    return JsonResponse({'exists': exists})

@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_user_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} has been {status}.")
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required('accounts.upload_content')
@require_GET
def api_list_sessions(request):
    sessions = Session.objects.all().order_by('order')
    data = [model_to_dict(s, fields=['id','title','order','course_id']) for s in sessions]
    return JsonResponse({'sessions': data})

@login_required
@permission_required('accounts.upload_content')
@require_POST
@csrf_exempt
def api_create_session(request):
    import json
    data = json.loads(request.body)
    s = Session.objects.create(
        title=data.get('title', ''),
        course_id=data.get('course_id'),
        order=Session.objects.filter(course_id=data.get('course_id')).count()
    )
    return JsonResponse({'session': model_to_dict(s)})

@login_required
@permission_required('accounts.upload_content')
@require_POST
@csrf_exempt
def api_update_session(request, session_id):
    import json
    data = json.loads(request.body)
    s = Session.objects.get(id=session_id)
    s.title = data.get('title', s.title)
    s.order = data.get('order', s.order)
    s.save()
    return JsonResponse({'session': model_to_dict(s)})

@login_required
@permission_required('accounts.upload_content')
@require_POST
@csrf_exempt
def api_delete_session(request, session_id):
    s = Session.objects.get(id=session_id)
    s.delete()
    return JsonResponse({'deleted': True})

@login_required
@permission_required('accounts.upload_content')
@require_POST
@csrf_exempt
def api_reorder_sessions(request):
    import json
    data = json.loads(request.body)
    order = data.get('order', [])
    for idx, session_id in enumerate(order):
        Session.objects.filter(id=session_id).update(order=idx)
    return JsonResponse({'success': True})

# --- TOPIC API ENDPOINTS ---
from django.views.decorators.csrf import csrf_exempt

@login_required
@permission_required('accounts.upload_content')
@require_GET
@csrf_exempt
def api_list_topics(request):
    topics = Topic.objects.all().order_by('order')
    data = [model_to_dict(t, fields=['id','title','order','session_id','is_quiz']) for t in topics]
    return JsonResponse({'topics': data})

@login_required
@permission_required('accounts.upload_content')
@require_POST
@csrf_exempt
def api_create_topic(request):
    import json
    data = json.loads(request.body)
    title = data.get('title', '')
    is_quiz = data.get('is_quiz', False)
    # Create topic for all sessions in all courses
    topics = []
    for session in Session.objects.all():
        t = Topic.objects.create(title=title, session=session, order=Topic.objects.filter(session=session).count(), is_quiz=is_quiz)
        topics.append(model_to_dict(t, fields=['id','title','order','session_id','is_quiz']))
    return JsonResponse({'topics': topics})

@login_required
@permission_required('accounts.upload_content')
@require_http_methods(["PUT"])
@csrf_exempt
def api_update_topic(request, topic_id):
    import json
    data = json.loads(request.body)
    t = Topic.objects.get(id=topic_id)
    t.title = data.get('title', t.title)
    t.is_quiz = data.get('is_quiz', t.is_quiz)
    t.order = data.get('order', t.order)
    t.save()
    return JsonResponse({'topic': model_to_dict(t, fields=['id','title','order','session_id','is_quiz'])})

@login_required
@permission_required('accounts.upload_content')
@require_http_methods(["DELETE"])
@csrf_exempt
def api_delete_topic(request, topic_id):
    t = Topic.objects.get(id=topic_id)
    t.delete()
    return JsonResponse({'deleted': True})

@login_required
@permission_required('accounts.upload_content')
@require_POST
@csrf_exempt
def api_reorder_topics(request):
    import json
    data = json.loads(request.body)
    order = data.get('order', [])
    for idx, item in enumerate(order):
        Topic.objects.filter(id=item['id']).update(order=idx)
    return JsonResponse({'success': True})