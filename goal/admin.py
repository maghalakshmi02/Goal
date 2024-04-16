from django.contrib import admin
from .models import UserDetails, Goal, Mentor, Todo, MentorTodo

@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('username', 'firstName', 'lastName', 'email', 'phoneNo', 'linkedIn')
    list_filter = ('username','firstName', 'lastName', 'email')
    search_fields = ('username','firstName', 'lastName', 'email')
    
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('goalName', 'beginDate', 'endDate', 'description', 'status')
    list_filter = ('goalName','status', 'beginDate', 'endDate')
    search_fields = ('goalName', 'description')
    list_editable = ('status','beginDate', 'endDate')
    

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'price', 'ratings', 'availability')
    list_filter = ('availability', 'ratings')
    search_fields = ('title', 'description')
    list_editable = ('availability', 'ratings')
    

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('todoName', 'beginDate', 'endDate', 'status')
    list_filter = ('status',)
    search_fields = ('todoName',)
    list_editable = ('status','beginDate', 'endDate')
    

@admin.register(MentorTodo)
class MentorTodoAdmin(admin.ModelAdmin):
    list_display = ('mentorId', 'todoName')
    search_fields = ('todoName',)
    
