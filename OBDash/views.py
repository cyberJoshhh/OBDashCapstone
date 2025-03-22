from django.shortcuts import render, redirect
from .models import Student, StudentScore, EvaluationRecord, CognitiveEvaluation, ExpressiveEvaluation, FineEvaluation, GrossEvaluation, ReceptiveEvaluation, SelfHelpEvaluation
from .forms import StudentForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import json
from django.db.models import Q
from django.utils import timezone

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
        student_id = request.POST.get('student_id')
        student_name = request.POST.get('student_name')
        eval1_score = int(request.POST.get('eval1_score', 0) or 0)
        eval2_score = int(request.POST.get('eval2_score', 0) or 0)
        eval3_score = int(request.POST.get('eval3_score', 0) or 0)
        evaluator_type = request.POST.get('evaluator_type', 'teacher')  # Default to teacher if not specified
        
        try:
            # Find the student - either by ID or by name
            student = None
            if student_id and student_id.isdigit():
                try:
                    student = Student.objects.get(id=int(student_id))
                except Student.DoesNotExist:
                    pass
            
            if not student and student_name:
                # Try to find by name if ID didn't work
                student = Student.objects.filter(child_name__iexact=student_name).first()
            
            # If we found a student, update their StudentScore record
            if student:
                # Get existing score for this student
                student_score, created = StudentScore.objects.get_or_create(
                    student=student,
                    defaults={
                        'self_help': 0,
                        'date_assessed': timezone.now().date()
                    }
                )
                
                # Get existing evaluations for this student
                teacher_eval = SelfHelpEvaluation.objects.filter(
                    student_name=student.child_name,
                    evaluator_type='teacher'
                ).order_by('-created_at').first()
                
                parent_eval = SelfHelpEvaluation.objects.filter(
                    student_name=student.child_name,
                    evaluator_type='parent'
                ).order_by('-created_at').first()
                
                # Save new evaluation
                SelfHelpEvaluation.objects.create(
                    student_name=student.child_name,
                    eval1_score=eval1_score,
                    eval2_score=eval2_score,
                    eval3_score=eval3_score,
                    evaluator_type=evaluator_type
                )
                
                # Calculate combined score based on both teacher and parent evaluations
                teacher_score = max(
                    teacher_eval.eval1_score, 
                    teacher_eval.eval2_score, 
                    teacher_eval.eval3_score
                ) if teacher_eval else 0
                
                parent_score = max(
                    parent_eval.eval1_score, 
                    parent_eval.eval2_score, 
                    parent_eval.eval3_score
                ) if parent_eval else 0
                
                # If this is a new evaluation, use its scores
                if evaluator_type == 'teacher':
                    teacher_score = max(eval1_score, eval2_score, eval3_score)
                else:
                    parent_score = max(eval1_score, eval2_score, eval3_score)
                
                # Calculate combined score (average of teacher and parent scores)
                # You can adjust this formula according to your requirements
                combined_score = (teacher_score + parent_score) / 2 if teacher_score and parent_score else (teacher_score or parent_score)
                
                # Update the StudentScore
                student_score.self_help = combined_score
                student_score.date_assessed = timezone.now().date()
                student_score.save()
            
            else:
                # If student not found, just save the evaluation
                SelfHelpEvaluation.objects.create(
                    student_name=student_name if student_name else "Unknown",
                    eval1_score=eval1_score,
                    eval2_score=eval2_score,
                    eval3_score=eval3_score,
                    evaluator_type=evaluator_type
                )
            
            messages.success(request, 'Evaluation submitted successfully!')
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            messages.error(request, f'Error saving evaluation: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

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
    
    # Add users_count for consistency with other views
    users_count = User.objects.count()
    evaluations_count = (GrossEvaluation.objects.count() + 
                        FineEvaluation.objects.count() + 
                        SelfHelpEvaluation.objects.count() + 
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

def evaluation_gross(request):
    # Get username and convert to proper format for comparison
    username = request.user.username.replace('_', ' ')
    
    # Find student by parent's name
    student = Student.objects.filter(
        Q(father_name__iexact=username) | 
        Q(mother_name__iexact=username)
    ).first()
    
    context = {
        'student': student,
        'active_domain': 'gross'
    }
    
    return render(request, 'pevalgross.html', context)


def evaluation_self(request):
    # Get username and convert to proper format for comparison
    username = request.user.username.replace('_', ' ')
    
    # Find student by parent's name
    student = Student.objects.filter(
        Q(father_name__iexact=username) | 
        Q(mother_name__iexact=username)
    ).first()
    
    context = {
        'student': student,
        'active_domain': 'self'
    }
    
    return render(request, 'pevalself.html', context)

def evaluation_expressive(request):
    # Get username and convert to proper format for comparison
    username = request.user.username.replace('_', ' ')
    
    # Find student by parent's name
    student = Student.objects.filter(
        Q(father_name__iexact=username) | 
        Q(mother_name__iexact=username)
    ).first()
    
    context = {
        'student': student,
        'active_domain': 'expressive'
    }
    
    return render(request, 'pevalexpressive.html', context)

def evaluation_cognitive(request):
    # Get username and convert to proper format for comparison
    username = request.user.username.replace('_', ' ')
    
    # Find student by parent's name
    student = Student.objects.filter(
        Q(father_name__iexact=username) | 
        Q(mother_name__iexact=username)
    ).first()
    
    context = {
        'student': student,
        'active_domain': 'cognitive'
    }
    
    return render(request, 'pevalcognitive.html', context)

def evaluation_social(request):
    # Get username and convert to proper format for comparison
    username = request.user.username.replace('_', ' ')
    
    # Find student by parent's name
    student = Student.objects.filter(
        Q(father_name__iexact=username) | 
        Q(mother_name__iexact=username)
    ).first()
    
    context = {
        'student': student,
        'active_domain': 'social'
    }
    
    return render(request, 'pevalsocial.html', context)


