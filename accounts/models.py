from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver




def normalize_phone(phone):
    return ''.join(filter(str.isdigit, phone))

def validate_image(image):
    max_size_mb = 3
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image must be smaller than {max_size_mb}MB.")
    if not image.content_type in ['image/jpeg', 'image/png', 'image/webp']:
        raise ValidationError("Only JPEG, PNG, or WebP images are allowed.")

class CourseOption(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Session(models.Model):
    course = models.ForeignKey(CourseOption, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.name} - {self.title}"

class Topic(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    is_quiz = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.session.title} - {self.title}"

class Video(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class Exam(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=100)
    timer_minutes = models.PositiveIntegerField(blank=True, null=True)
    retake_limit = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    image = models.ImageField(upload_to='exam_questions/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Q{self.order+1}: {self.text[:30]}..."

class ExamChoice(models.Model):
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class ExamAttempt(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='exam_attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    score = models.FloatField(default=0)
    retake_number = models.PositiveIntegerField(default=1)
    is_finished = models.BooleanField(default=False)
    saved_answers = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} (Retake {self.retake_number})"

class UserAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(ExamChoice, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.text[:20]}..."



class CustomUser(AbstractUser):
    GRADE_CHOICES = [
        ('G10', _('Grade 10')),
        ('G11', _('Grade 11')),
        ('G12', _('Grade 12')),
    ]
    # ... other fields and methods ...

    # Place Meta at the end
    class Meta(AbstractUser.Meta):
        permissions = [
            ("can_upload_content", "Can upload and manage course content"),
        ]


    COURSE_CHOICES = [
        ('Basics EST', _('Basics EST')),
        ('Basics DSAT', _('Basics DSAT')),
        ('Basics SAT', _('Basics SAT')),
        ('Basics L2 EST', _('Basics L2 EST')),
        ('Basics L2 DSAT', _('Basics L2 DSAT')),
        ('Basics L2 ACT', _('Basics L2 ACT')),
        ('Real Exams + Explain Basics EST', _('Real Exams + Explain Basics EST')),
        ('Real Exams + Explain Basics DSAT', _('Real Exams + Explain Basics DSAT')),
        ('Real Exams + Explain Basics ACT', _('Real Exams + Explain Basics ACT')),
        ('Advanced L1 EST', _('Advanced L1 EST')),
        ('Advanced L1 DSAT', _('Advanced L1 DSAT')),
        ('Advanced L1 ACT', _('Advanced L1 ACT')),
        ('Advanced L2 EST', _('Advanced L2 EST')),
        ('Advanced L2 DSAT', _('Advanced L2 DSAT')),
        ('Advanced L2 ACT', _('Advanced L2 ACT')),
        ('EST2 Full Course', _('EST2 Full Course')),
    ]



    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name=_('Profile picture'),
        help_text=_('Upload a profile picture (optional)'),
        validators=[validate_image]
    )

    age = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        default=18,
        verbose_name=_('Age'),
        help_text=_('Your age (optional)')
    )

    help_text = models.TextField(
        blank=False,
        null=False,
        default='-',
        verbose_name=_('How can you help us?'),
        help_text=_('Tell us how you can help us (optional)')
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')



    def __str__(self):
        full_name = self.get_full_name()
        return f"{self.username} ({full_name})" if full_name else self.username

    def clean(self):
        super().clean()
        self._validate_username()

    def _validate_username(self):
        if self.username:
            self.username = self.username.lower()
            existing = CustomUser.objects.filter(username__iexact=self.username).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({'username': _("This username is already taken.")})





    def normalize_phone(phone):
        return ''.join(filter(str.isdigit, phone))

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)

    def get_full_name_with_grade(self):
        return f"{self.get_full_name()} ({self.get_grade_level_display()})"
