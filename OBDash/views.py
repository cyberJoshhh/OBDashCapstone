from django.shortcuts import render, redirect
from .models import Student, StudentScore, EvaluationRecord, CognitiveEvaluation, ExpressiveEvaluation, FineEvaluation, GrossEvaluation, ReceptiveEvaluation, SelfHelpEvaluation, SocialEvaluation
from .forms import StudentForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import json
from django.db.models import Q

@login_required
def dashboard(request):
    # Get the logged-in user's username
    username = request.user.username
    
    # Check if the user is a parent
    student = None
    scores = None
    
    # Try to find student by father's name
    father_student = Student.objects.filter(father_name__iexact=username.replace('_', ' ')).first()
    # Try to find student by mother's name
    mother_student = Student.objects.filter(mother_name__iexact=username.replace('_', ' ')).first()
    
    if father_student or mother_student:
        # This is a parent
        student = father_student if father_student else mother_student
        try:
            scores = student.scores
        except StudentScore.DoesNotExist:
            scores = None
        context = {
            'student': student,
            'scores': scores,
            'gross_evaluations': GrossEvaluation.objects.all(),
            'fine_evaluations': FineEvaluation.objects.all(),
            'self_help_evaluations': SelfHelpEvaluation.objects.all(),
            'social_evaluations': SocialEvaluation.objects.all(),
            'expressive_evaluations': ExpressiveEvaluation.objects.all(),
            'receptive_evaluations': ReceptiveEvaluation.objects.all(),
            'cognitive_evaluations': CognitiveEvaluation.objects.all()
        }
        return render(request, "PDash.html", context)
    else:
        # This is a teacher/admin
        students = Student.objects.all()
        # Get the total number of users
        users_count = User.objects.count()
        # Count evaluations (you can adjust this based on your needs)
        evaluations_count = (GrossEvaluation.objects.count() + 
                            FineEvaluation.objects.count() + 
                            SelfHelpEvaluation.objects.count() + 
                            SocialEvaluation.objects.count() + 
                            ExpressiveEvaluation.objects.count() + 
                            ReceptiveEvaluation.objects.count() + 
                            CognitiveEvaluation.objects.count())
        
        return render(request, "TDash.html", {
            "students": students,
            "users_count": users_count,
            "evaluations_count": evaluations_count,
            "messages_count": 0  # You can replace this with actual message count if you have a message model
        })


def add_student(request):
    if request.method == 'POST':
        try:
            # Create student record with the correct field names
            student = Student(
                child_name=request.POST.get('child_name'),
                sex=request.POST.get('sex'),
                dob=request.POST.get('dob'),
                handedness=request.POST.get('handedness'),
                studying=request.POST.get('studying'),
                birth_order=request.POST.get('birth_order'),
                num_siblings=int(request.POST.get('num_siblings')),
                
                # Address information
                address=request.POST.get('address'),
                barangay=request.POST.get('barangay'),
                municipality=request.POST.get('municipality'),
                province=request.POST.get('province'),
                region=request.POST.get('region'),
                
                # Father's information
                father_name=request.POST.get('father_name'),
                father_age=int(request.POST.get('father_age')),
                father_occupation=request.POST.get('father_occupation'),
                father_education=request.POST.get('father_education'),
                father_password=request.POST.get('father_password'),
                
                # Mother's information
                mother_name=request.POST.get('mother_name'),
                mother_age=int(request.POST.get('mother_age')),
                mother_occupation=request.POST.get('mother_occupation'),
                mother_education=request.POST.get('mother_education'),
                mother_password=request.POST.get('mother_password')
            )
            student.save()
            
            messages.success(request, f'Student {request.POST.get("child_name")} has been successfully registered!')
            return redirect('performance')
            
        except Exception as e:
            messages.error(request, f'Error registering student: {str(e)}')
            return render(request, 'add_student.html')
    
    return render(request, 'add_student.html')

def login_view(request):
    if request.method == 'POST':
        parent_name = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate
        user = authenticate(request, username=parent_name, password=password)
        if user is not None:
            login(request, user)
            # Check if user is superuser (teacher/admin)
            if user.is_superuser:
                return redirect('dashboard')  # This will go to TDash for superusers
            
            # Convert parent name to username format for regular users
            username = parent_name.replace(' ', '_').lower()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)    
                return redirect('dashboard')
        else:
            # Check if this is a parent's name
            student_father = Student.objects.filter(father_name__iexact=parent_name).first()
            student_mother = Student.objects.filter(mother_name__iexact=parent_name).first()
            
            if student_father and student_father.father_password == password:
                # Create user if it doesn't exist
                username = parent_name.replace(' ', '_').lower()
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                return redirect('dashboard')
            elif student_mother and student_mother.mother_password == password:
                # Create user if it doesn't exist
                username = parent_name.replace(' ', '_').lower()
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid parent name or password')
                return render(request, 'Login.html', {'error': 'Invalid parent name or password'})
    
    return render(request, 'Login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def evaluation_checklist(request):
    domain = request.GET.get('domain', 'gross_motor')  # Default to gross motor if no domain specified
    template_name = f"evaluation_checklists/{domain}.html"
    return render(request, template_name)

@csrf_protect
def social_emotional_checklist(request, student_id):
    student = Student.objects.get(id=student_id)
    context = {
        'student': student
    }
    return render(request, 'evaluation_checklists/social_emotional.html', context)

def cognitive_checklist(request, student_id):
    student = Student.objects.get(id=student_id)
    context = {
        'student': student
    }
    return render(request, 'evaluation_checklists/cognitive.html', context)

def get_checklist_context(student_id):
    try:
        student = Student.objects.get(id=student_id)
        latest_eval = EvaluationRecord.objects.filter(student=student).order_by('-evaluation_number').first()
        evaluation_number = (latest_eval.evaluation_number + 1 if latest_eval else 1) if latest_eval and latest_eval.evaluation_number < 3 else 3
        
        return {
            'student': student,
            'evaluation_number': evaluation_number
        }
    except Student.DoesNotExist:
        return None

def checklist_view(request, student_id, domain):
    context = get_checklist_context(student_id)
    if context is None:
        return redirect('dashboard')
    
    # Add domain-specific context
    domain_titles = {
        'cognitive': 'Cognitive Domain',
        'social_emotional': 'Social-Emotional Domain',
        'fine_motor': 'Fine Motor Domain',
        'gross_motor': 'Gross Motor Domain',
        'self_help': 'Self-Help Domain',
        'expressive_language': 'Expressive Language Domain',
        'receptive_language': 'Receptive Language Domain'
    }
    
    context.update({
        'current_domain': domain,
        'domain_title': domain_titles[domain]
    })
    
    return render(request, f'evaluation_checklists/{domain}.html', context)

def submit_cognitive_evaluation(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        eval1_score = int(request.POST.get('eval1_score', 0) or 0)
        eval2_score = int(request.POST.get('eval2_score', 0) or 0)
        eval3_score = int(request.POST.get('eval3_score', 0) or 0)

        CognitiveEvaluation.objects.create(
            student_name=student_name,
            eval1_score=eval1_score,
            eval2_score=eval2_score,
            eval3_score=eval3_score
        )

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect('dashboard')  # or wherever you want to redirect after submission

    return redirect('dashboard')


def submit_expressive_evaluation(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        eval1_score = int(request.POST.get('eval1_score', 0) or 0)
        eval2_score = int(request.POST.get('eval2_score', 0) or 0)
        eval3_score = int(request.POST.get('eval3_score', 0) or 0)

        ExpressiveEvaluation.objects.create(
            student_name=student_name,
            eval1_score=eval1_score,
            eval2_score=eval2_score,
            eval3_score=eval3_score
        )

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect('dashboard')

    return redirect('dashboard')

def submit_fine_evaluation(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        # Convert scores to integers, default to 0 if empty
        eval1_score = int(request.POST.get('eval1_score', 0) or 0)
        eval2_score = int(request.POST.get('eval2_score', 0) or 0)
        eval3_score = int(request.POST.get('eval3_score', 0) or 0)

        FineEvaluation.objects.create(
            student_name=student_name,
            eval1_score=eval1_score,
            eval2_score=eval2_score,
            eval3_score=eval3_score
        )

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect('dashboard')

    return redirect('dashboard')

def submit_gross_evaluation(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        eval1_score = int(request.POST.get('eval1_score', 0) or 0)
        eval2_score = int(request.POST.get('eval2_score', 0) or 0)
        eval3_score = int(request.POST.get('eval3_score', 0) or 0)

        GrossEvaluation.objects.create(
            student_name=student_name,
            eval1_score=eval1_score,
            eval2_score=eval2_score,
            eval3_score=eval3_score
        )

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect('dashboard')  # or wherever you want to redirect after submission

    return redirect('dashboard')

def submit_receptive_evaluation(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        eval1_score = int(request.POST.get('eval1_score', 0) or 0)
        eval2_score = int(request.POST.get('eval2_score', 0) or 0)
        eval3_score = int(request.POST.get('eval3_score', 0) or 0)

        ReceptiveEvaluation.objects.create(
            student_name=student_name,
            eval1_score=eval1_score,
            eval2_score=eval2_score,
            eval3_score=eval3_score
        )

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect('dashboard')  # or wherever you want to redirect after submission

    return redirect('dashboard')

def submit_selfhelp_evaluation(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        eval1_score = int(request.POST.get('eval1_score', 0) or 0)
        eval2_score = int(request.POST.get('eval2_score', 0) or 0)
        eval3_score = int(request.POST.get('eval3_score', 0) or 0)

        SelfHelpEvaluation.objects.create(
            student_name=student_name,
            eval1_score=eval1_score,
            eval2_score=eval2_score,
            eval3_score=eval3_score
        )

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect('dashboard')  # or wherever you want to redirect after submission

    return redirect('dashboard')

def submit_social_evaluation(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        eval1_score = int(request.POST.get('eval1_score', 0) or 0)
        eval2_score = int(request.POST.get('eval2_score', 0) or 0)
        eval3_score = int(request.POST.get('eval3_score', 0) or 0)

        SocialEvaluation.objects.create(
            student_name=student_name,
            eval1_score=eval1_score,
            eval2_score=eval2_score,
            eval3_score=eval3_score
        )

        messages.success(request, 'Evaluation submitted successfully!')
        return redirect('dashboard')  # or wherever you want to redirect after submission

    return redirect('dashboard')

@login_required
def performance_view(request):
    # Get all students
    students = Student.objects.all()
    
    # Get all evaluation data
    gross_evaluations = GrossEvaluation.objects.all()
    fine_evaluations = FineEvaluation.objects.all()
    self_help_evaluations = SelfHelpEvaluation.objects.all()
    receptive_evaluations = ReceptiveEvaluation.objects.all()
    expressive_evaluations = ExpressiveEvaluation.objects.all()
    cognitive_evaluations = CognitiveEvaluation.objects.all()
    social_evaluations = SocialEvaluation.objects.all()
    
    # Add users_count for consistency with other views
    users_count = User.objects.count()
    evaluations_count = (GrossEvaluation.objects.count() + 
                        FineEvaluation.objects.count() + 
                        SelfHelpEvaluation.objects.count() + 
                        SocialEvaluation.objects.count() + 
                        ExpressiveEvaluation.objects.count() + 
                        ReceptiveEvaluation.objects.count() + 
                        CognitiveEvaluation.objects.count())
    
    context = {
        'students': students,
        'gross_evaluations': gross_evaluations,
        'fine_evaluations': fine_evaluations,
        'self_help_evaluations': self_help_evaluations,
        'receptive_evaluations': receptive_evaluations,
        'expressive_evaluations': expressive_evaluations,
        'cognitive_evaluations': cognitive_evaluations,
        'social_evaluations': social_evaluations,
        'users_count': users_count,
        'evaluations_count': evaluations_count,
        'messages_count': 0
    }
    return render(request, "performance.html", context)


def settings_view(request):
    """
    View function for the settings page.
    """
    return render(request, 'settings.html')

def parent_view_social_emotional(request):
    # Get student name associated with parent (adjust based on your models)
    student_name = "Your Child"  # Default fallback
    
    try:
        # Adjust this query based on your model relationships
        parent = request.user
        student = Student.objects.filter(parent=parent).first()
        if student:
            student_name = student.child_name
    except:
        pass
    
    # Pass the student name to the template
    context = {
        'student_name': student_name
    }
    
    return render(request, 'evaluation_checklists/social_emotional.html', context)

