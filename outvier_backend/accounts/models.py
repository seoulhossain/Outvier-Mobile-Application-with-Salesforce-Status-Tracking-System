from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    STUDENT = 'student'
    ADMINISTRATOR = 'administrator'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (ADMINISTRATOR, 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    student_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    push_token = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'students'

    def is_student(self):
        return self.role == self.STUDENT

    def is_admin(self):
        return self.role == self.ADMINISTRATOR
