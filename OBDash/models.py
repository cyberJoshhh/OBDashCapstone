from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Student(models.Model):
    child_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=10)
    dob = models.DateField()
    address = models.CharField(max_length=255)
    barangay = models.CharField(max_length=255)
    municipality = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    handedness = models.CharField(max_length=50)
    studying = models.CharField(max_length=10)
    father_name = models.CharField(max_length=255)
    father_password = models.CharField(max_length=128, default='123')
    father_age = models.IntegerField()
    father_occupation = models.CharField(max_length=255)
    father_education = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    mother_password = models.CharField(max_length=128, default='123')
    mother_age = models.IntegerField()
    mother_occupation = models.CharField(max_length=255)
    mother_education = models.CharField(max_length=255)
    num_siblings = models.IntegerField()
    birth_order = models.CharField(max_length=50)
    
    

    def __str__(self):
        return self.child_name

class StudentScore(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='scores')
    gross_motor = models.FloatField(null=True, blank=True)
    fine_motor = models.FloatField(null=True, blank=True)
    self_help = models.FloatField(null=True, blank=True)
    receptive_language = models.FloatField(null=True, blank=True)
    expressive_language = models.FloatField(null=True, blank=True)
    cognitive = models.FloatField(null=True, blank=True)
    social_emotional = models.FloatField(null=True, blank=True)
    date_assessed = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.student.child_name}'s Scores"

@receiver(post_save, sender=Student)
def create_user_for_student(sender, instance, created, **kwargs):
    if created:
        # Create father's username
        father_username = instance.father_name.replace(' ', '_').lower()
        # Only create if user doesn't exist
        if not User.objects.filter(username=father_username).exists():
            User.objects.create_user(
                username=father_username,
                password=instance.father_password
            )
        
        # Create mother's username
        mother_username = instance.mother_name.replace(' ', '_').lower()
        # Only create if user doesn't exist
        if not User.objects.filter(username=mother_username).exists():
            User.objects.create_user(
                username=mother_username,
                password=instance.mother_password
            )

class EvaluationRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    evaluation_date = models.DateField(auto_now_add=True)
    evaluation_number = models.IntegerField()  # 1, 2, or 3
    
    # Scores for each domain
    cognitive_score = models.IntegerField()
    fine_motor_score = models.IntegerField()
    gross_motor_score = models.IntegerField()
    self_help_score = models.IntegerField()
    social_emotional_score = models.IntegerField()
    expressive_language_score = models.IntegerField()
    receptive_language_score = models.IntegerField()

    class Meta:
        unique_together = ['student', 'evaluation_number']

class CognitiveEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"
    
class ExpressiveEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"
    
class FineEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"

class GrossEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"
    
class ReceptiveEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"
    
class SelfHelpEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"

class SocialEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"


#parent's evaluation
class ParentSocialEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"

class ParentSelfHelpEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"

class ParentGrossEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"

class ParentCognitiveEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"

class ParentExpressiveEvaluation(models.Model):
    student_name = models.CharField(max_length=255)
    eval1_score = models.IntegerField()
    eval2_score = models.IntegerField()
    eval3_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.created_at}"