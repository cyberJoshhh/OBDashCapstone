from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, StudentScore, EvaluationRecord, CognitiveEvaluation, ExpressiveEvaluation, FineEvaluation, GrossEvaluation, ReceptiveEvaluation, SelfHelpEvaluation, ParentSelfHelpEvaluation, ParentGrossEvaluation, ParentSocialEvaluation, ParentExpressiveEvaluation, ParentCognitiveEvaluation
from .forms import StudentForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
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
        context['debug'] = True
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

@login_required
def ParentEvaluationSelf(request, student_id=None):
    """
    Display and handle the parent self-help evaluation form.
    If method is GET, displays the form.
    If method is POST, processes the submission.
    """
    # GET request - display the evaluation form
    if request.method == 'GET':
        student = None
        if student_id:
            student = get_object_or_404(Student, id=student_id)
        
        context = {
            'student': student,
        }
        
        return render(request, 'pevalself.html', context)
    
    # POST request - process the evaluation data
    elif request.method == 'POST':
        try:
            # Extract form data
            student_name = request.POST.get('student_name', '')
            
            # If we have student_id but not student_name, try to get the name
            if student_id and not student_name:
                try:
                    student = Student.objects.get(id=student_id)
                    student_name = student.child_name
                except Student.DoesNotExist:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Student not found'
                    }, status=404)
            
            # Get evaluation scores
            eval1_score = int(request.POST.get('eval1_score', 0))
            eval2_score = int(request.POST.get('eval2_score', 0))
            eval3_score = int(request.POST.get('eval3_score', 0))
            
            # Get comments if any
            comments_json = request.POST.get('comments', '[]')
            
            # Create a new evaluation record
            evaluation = ParentSelfHelpEvaluation(
                student_name=student_name,
                eval1_score=eval1_score,
                eval2_score=eval2_score,
                eval3_score=eval3_score
            )
            evaluation.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Self-Help evaluation saved successfully',
                'evaluation_id': evaluation.id
            })
            
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid data format: {str(e)}'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error saving evaluation: {str(e)}'
            }, status=500)
    
    # Other request methods
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method. GET or POST required.'
    }, status=405)

@login_required
def ParentEvaluationGross(request, student_id=None):
    """
    Display and handle the parent gross motor evaluation form.
    If method is GET, displays the form.
    If method is POST, processes the submission.
    """
    # GET request - display the evaluation form
    if request.method == 'GET':
        student = None
        if student_id:
            student = get_object_or_404(Student, id=student_id)
        
        context = {
            'student': student,
        }
        
        return render(request, 'pevalgross.html', context)
    
    # POST request - process the evaluation data
    elif request.method == 'POST':
        try:
            # Extract form data
            student_name = request.POST.get('student_name', '')
            
            # If we have student_id but not student_name, try to get the name
            if student_id and not student_name:
                try:
                    student = Student.objects.get(id=student_id)
                    student_name = student.child_name
                except Student.DoesNotExist:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Student not found'
                    }, status=404)
            
            # Get evaluation scores
            eval1_score = int(request.POST.get('eval1_score', 0))
            eval2_score = int(request.POST.get('eval2_score', 0))
            eval3_score = int(request.POST.get('eval3_score', 0))
            
            # Get comments if any
            comments_json = request.POST.get('comments', '[]')
            
            # Create a new evaluation record
            evaluation = ParentGrossEvaluation(
                student_name=student_name,
                eval1_score=eval1_score,
                eval2_score=eval2_score,
                eval3_score=eval3_score
            )
            evaluation.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Gross Motor evaluation saved successfully',
                'evaluation_id': evaluation.id
            })
            
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid data format: {str(e)}'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error saving evaluation: {str(e)}'
            }, status=500)
    
    # Other request methods
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method. GET or POST required.'
    }, status=405)

@login_required
def ParentEvaluationSocial(request, student_id=None):
    """
    Display and handle the parent social-emotional evaluation form.
    If method is GET, displays the form.
    If method is POST, processes the submission.
    """
    # GET request - display the evaluation form
    if request.method == 'GET':
        student = None
        if student_id:
            student = get_object_or_404(Student, id=student_id)
        
        context = {
            'student': student,
        }
        
        return render(request, 'pevalsocial.html', context)
    
    # POST request - process the evaluation data
    elif request.method == 'POST':
        try:
            # Extract form data
            student_name = request.POST.get('student_name', '')
            
            # If we have student_id but not student_name, try to get the name
            if student_id and not student_name:
                try:
                    student = Student.objects.get(id=student_id)
                    student_name = student.child_name
                except Student.DoesNotExist:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Student not found'
                    }, status=404)
            
            # Get evaluation scores
            eval1_score = int(request.POST.get('eval1_score', 0))
            eval2_score = int(request.POST.get('eval2_score', 0))
            eval3_score = int(request.POST.get('eval3_score', 0))
            
            # Get comments if any
            comments_json = request.POST.get('comments', '[]')
            
            # Create a new evaluation record
            evaluation = ParentSocialEvaluation(
                student_name=student_name,
                eval1_score=eval1_score,
                eval2_score=eval2_score,
                eval3_score=eval3_score
            )
            evaluation.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Social-Emotional evaluation saved successfully',
                'evaluation_id': evaluation.id
            })
            
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid data format: {str(e)}'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error saving evaluation: {str(e)}'
            }, status=500)
    
    # Other request methods
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method. GET or POST required.'
    }, status=405)

@login_required
def ParentEvaluationExpressive(request, student_id=None):
    """
    Display and handle the parent expressive language evaluation form.
    If method is GET, displays the form.
    If method is POST, processes the submission.
    """
    # GET request - display the evaluation form
    if request.method == 'GET':
        student = None
        if student_id:
            student = get_object_or_404(Student, id=student_id)
        
        context = {
            'student': student,
        }
        
        return render(request, 'pevalexpressive.html', context)
    
    # POST request - process the evaluation data
    elif request.method == 'POST':
        try:
            # Extract form data
            student_name = request.POST.get('student_name', '')
            
            # If we have student_id but not student_name, try to get the name
            if student_id and not student_name:
                try:
                    student = Student.objects.get(id=student_id)
                    student_name = student.child_name
                except Student.DoesNotExist:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Student not found'
                    }, status=404)
            
            # Get evaluation scores
            eval1_score = int(request.POST.get('eval1_score', 0))
            eval2_score = int(request.POST.get('eval2_score', 0))
            eval3_score = int(request.POST.get('eval3_score', 0))
            
            # Get comments if any
            comments_json = request.POST.get('comments', '[]')
            
            # Create a new evaluation record
            evaluation = ParentExpressiveEvaluation(
                student_name=student_name,
                eval1_score=eval1_score,
                eval2_score=eval2_score,
                eval3_score=eval3_score
            )
            evaluation.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Expressive Language evaluation saved successfully',
                'evaluation_id': evaluation.id
            })
            
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid data format: {str(e)}'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error saving evaluation: {str(e)}'
            }, status=500)
    
    # Other request methods
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method. GET or POST required.'
    }, status=405)

@login_required
def ParentEvaluationCognitive(request, student_id=None):
    """
    Display and handle the parent cognitive evaluation form.
    If method is GET, displays the form.
    If method is POST, processes the submission.
    """
    # GET request - display the evaluation form
    if request.method == 'GET':
        student = None
        if student_id:
            student = get_object_or_404(Student, id=student_id)
        
        context = {
            'student': student,
        }
        
        return render(request, 'pevalcognitive.html', context)
    
    # POST request - process the evaluation data
    elif request.method == 'POST':
        try:
            # Extract form data
            student_name = request.POST.get('student_name', '')
            
            # If we have student_id but not student_name, try to get the name
            if student_id and not student_name:
                try:
                    student = Student.objects.get(id=student_id)
                    student_name = student.child_name
                except Student.DoesNotExist:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Student not found'
                    }, status=404)
            
            # Get evaluation scores
            eval1_score = int(request.POST.get('eval1_score', 0))
            eval2_score = int(request.POST.get('eval2_score', 0))
            eval3_score = int(request.POST.get('eval3_score', 0))
            
            # Get comments if any
            comments_json = request.POST.get('comments', '[]')
            
            # Create a new evaluation record
            evaluation = ParentCognitiveEvaluation(
                student_name=student_name,
                eval1_score=eval1_score,
                eval2_score=eval2_score,
                eval3_score=eval3_score
            )
            evaluation.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cognitive evaluation saved successfully',
                'evaluation_id': evaluation.id
            })
            
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid data format: {str(e)}'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error saving evaluation: {str(e)}'
            }, status=500)
    
    # Other request methods
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method. GET or POST required.'
    }, status=405)

def comparison_view(request):
    search_query = request.GET.get('search', '')
    student_name = request.GET.get('student_name', '')
    
    # Get list of students for the search dropdown
    students = set()
    
    # Collect student names from various evaluation tables
    if search_query:
        # Search across multiple evaluation tables with case-insensitive search
        gross_students = GrossEvaluation.objects.filter(student_name__icontains=search_query).values_list('student_name', flat=True)
        fine_students = FineEvaluation.objects.filter(student_name__icontains=search_query).values_list('student_name', flat=True)
        self_help_students = SelfHelpEvaluation.objects.filter(student_name__icontains=search_query).values_list('student_name', flat=True)
        cognitive_students = CognitiveEvaluation.objects.filter(student_name__icontains=search_query).values_list('student_name', flat=True)
        
        # Add to set to remove duplicates
        students.update(gross_students)
        students.update(fine_students)
        students.update(self_help_students)
        students.update(cognitive_students)
        
        # Sort the students alphabetically
        students = sorted(students)
    
    # Only fetch evaluation data if a specific student is selected
    if student_name:
        # Fetch teacher evaluations
        teacher_gross = GrossEvaluation.objects.filter(student_name=student_name).first()
        teacher_fine = FineEvaluation.objects.filter(student_name=student_name).first()
        teacher_self_help = SelfHelpEvaluation.objects.filter(student_name=student_name).first()
        teacher_receptive = ReceptiveEvaluation.objects.filter(student_name=student_name).first()
        teacher_expressive = ExpressiveEvaluation.objects.filter(student_name=student_name).first()
        teacher_cognitive = CognitiveEvaluation.objects.filter(student_name=student_name).first()
        
        # Fetch parent evaluations
        parent_gross = ParentGrossEvaluation.objects.filter(student_name=student_name).first()
        parent_self_help = ParentSelfHelpEvaluation.objects.filter(student_name=student_name).first()
        parent_social = ParentSocialEvaluation.objects.filter(student_name=student_name).first()
        parent_expressive = ParentExpressiveEvaluation.objects.filter(student_name=student_name).first()
        parent_cognitive = ParentCognitiveEvaluation.objects.filter(student_name=student_name).first()
        
        # Create data for JSON
        teacher_data = {
            'gross_motor': [
                teacher_gross.eval1_score if teacher_gross else 0,
                teacher_gross.eval2_score if teacher_gross else 0,
                teacher_gross.eval3_score if teacher_gross else 0
            ],
            'fine_motor': [
                teacher_fine.eval1_score if teacher_fine else 0,
                teacher_fine.eval2_score if teacher_fine else 0,
                teacher_fine.eval3_score if teacher_fine else 0
            ],
            'self_help': [
                teacher_self_help.eval1_score if teacher_self_help else 0,
                teacher_self_help.eval2_score if teacher_self_help else 0,
                teacher_self_help.eval3_score if teacher_self_help else 0
            ],
            'receptive': [
                teacher_receptive.eval1_score if teacher_receptive else 0,
                teacher_receptive.eval2_score if teacher_receptive else 0,
                teacher_receptive.eval3_score if teacher_receptive else 0
            ],
            'expressive': [
                teacher_expressive.eval1_score if teacher_expressive else 0,
                teacher_expressive.eval2_score if teacher_expressive else 0,
                teacher_expressive.eval3_score if teacher_expressive else 0
            ],
            'cognitive': [
                teacher_cognitive.eval1_score if teacher_cognitive else 0,
                teacher_cognitive.eval2_score if teacher_cognitive else 0,
                teacher_cognitive.eval3_score if teacher_cognitive else 0
            ]
        }
        
        parent_data = {
            'gross_motor': [
                parent_gross.eval1_score if parent_gross else 0,
                parent_gross.eval2_score if parent_gross else 0,
                parent_gross.eval3_score if parent_gross else 0
            ],
            'self_help': [
                parent_self_help.eval1_score if parent_self_help else 0,
                parent_self_help.eval2_score if parent_self_help else 0,
                parent_self_help.eval3_score if parent_self_help else 0
            ],
            'social': [
                parent_social.eval1_score if parent_social else 0,
                parent_social.eval2_score if parent_social else 0,
                parent_social.eval3_score if parent_social else 0
            ],
            'expressive': [
                parent_expressive.eval1_score if parent_expressive else 0,
                parent_expressive.eval2_score if parent_expressive else 0,
                parent_expressive.eval3_score if parent_expressive else 0
            ],
            'cognitive': [
                parent_cognitive.eval1_score if parent_cognitive else 0,
                parent_cognitive.eval2_score if parent_cognitive else 0,
                parent_cognitive.eval3_score if parent_cognitive else 0
            ]
        }
        
        context = {
            'student_name': student_name,
            'teacher_data_json': json.dumps(teacher_data),
            'parent_data_json': json.dumps(parent_data),
            'teacher_evaluations': {
                'gross': teacher_gross,
                'fine': teacher_fine,
                'self_help': teacher_self_help,
                'receptive': teacher_receptive,
                'expressive': teacher_expressive,
                'cognitive': teacher_cognitive
            },
            'parent_evaluations': {
                'gross': parent_gross,
                'self_help': parent_self_help,
                'social': parent_social,
                'expressive': parent_expressive,
                'cognitive': parent_cognitive
            },
            'has_data': True
        }
    else:
        context = {
            'has_data': False
        }
    
    # Always include these in the context
    context['search_query'] = search_query
    context['students'] = students
    
    return render(request, 'comparison.html', context)