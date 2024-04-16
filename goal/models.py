from django.contrib.auth.models import AbstractUser,Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserDetails(AbstractUser):
    firstName = models.CharField(max_length=30, blank=True)
    lastName = models.CharField(max_length=30, blank=True)
    phoneNo = models.CharField(max_length=20, blank=True)
    linkedIn = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        # Add a unique identifier for this model in the database
        db_table = 'user_details'

    # Specify related_name for groups and user_permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_set',  
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_set',  
        related_query_name='user',
    )

class Goal(models.Model):
    userId = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    goalId = models.AutoField(primary_key=True)
    mentor = models.ForeignKey('Mentor', on_delete=models.SET_NULL, null=True, blank=True)
    goalName = models.TextField(null=False)
    beginDate = models.DateTimeField(null=False)
    endDate = models.DateTimeField(null=False)
    url = models.URLField()
    imageUrl = models.URLField(default=None)
    description = models.TextField(null=False)
    price = models.TextField()
    status = models.TextField()

    def __str__(self):
        return self.goalName

class Mentor(models.Model):
    userId = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    mentorId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    url = models.URLField(null=True, blank=False)
    imageUrl = models.URLField(null=True, blank=False)
    price = models.CharField(max_length=10)
    amount = models.IntegerField()
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    currencyType = models.CharField(max_length=10)
    ratings = models.FloatField()
    availability = models.BooleanField(default=True)
    

    def __str__(self):
        return self.title


class Todo(models.Model):
    goalId = models.ForeignKey(Goal, on_delete=models.CASCADE)
    todoId = models.AutoField(primary_key=True)
    todoName = models.TextField()
    beginDate = models.DateTimeField()
    endDate = models.DateTimeField()
    url = models.URLField()
    imageUrl = models.URLField(default=None)
    description = models.TextField()
    status = models.TextField()

    def __str__(self):
        return self.todoName

class MentorTodo(models.Model):
    mentorId = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    todoId = models.AutoField(primary_key=True)
    todoName = models.TextField()  # Replace with an existing field name
    url = models.URLField()
    imageUrl = models.URLField(default=None,null=True)
    description = models.TextField()

    def __str__(self):
        return str(self.mentorId)
    
class Book(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='books', null=True, blank=True)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='books', null=True, blank=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255,null=True)
    ratings = models.FloatField(null=True)
    isbn = models.CharField(max_length=13, unique=True,null=True)
    description = models.TextField()
    url = models.URLField(null=True)

    def __str__(self):
        return self.title

class Website(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='websites', null=True, blank=True)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='websites', null=True, blank=True)
    name = models.CharField(max_length=255)
    url = models.URLField(null=False)
    description = models.TextField(null=False)

    def __str__(self):
        return self.name

class Event(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    title = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255,null=True)
    description = models.TextField()
    mode = models.TextField()
    url = models.URLField(null=True)

    def __str__(self):
        return self.title

class Meeting(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='meetings', null=True, blank=True)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='meetings', null=True, blank=True)
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField(null=True)
    location = models.CharField(max_length=255,null=True)
    mode = models.TextField()
    agenda = models.TextField()
    url = models.URLField(null=True)

    def __str__(self):
        return self.title
