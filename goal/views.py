import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import  GoalForm,MentorForm,AddToGoalForm, BookForm, CustomUserCreationForm, EventForm, MeetingForm, MyAccountForm, TodoForm, TodosForm, UserDetailsForm, WebsiteForm#,CustomPasswordChangeForm
from .models import Book, Goal,Mentor, MentorTodo, Todo,UserDetails,Meeting,Website, Mentor,Event
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

#HOME PAGE
def home(request):
    return render(request, 'home.html')

#USER REGISTRATION
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set the backend attribute to resolve multiple authentication backends error
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            #login(request, user)
            return redirect('login')  # Redirect to the homepage after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

#LOGIN 
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('mentor_list')
            #return redirect('home')  # Redirect to the homepage after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

#LOGOUT
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to the homepage after logout



#GOAL CREATION 
@login_required
def create_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.userId = request.user  # Assign the current user to the goal
            goal.save()
            return redirect('goal_list')
    else:
        form = GoalForm()
    return render(request, 'create_goal.html', {'form': form})

#USER'S GOAL LIST 
@login_required
def goal_list(request):
    # Retrieve goals for the authenticated user
    goals = Goal.objects.filter(userId=request.user)
    return render(request, 'goal_list.html', {'goals': goals})


#GOAL DETAIL -6
@login_required
def goal_detail(request, goal_id):
    # Retrieve the goal for the authenticated user
    goal = get_object_or_404(Goal, pk=goal_id, userId=request.user)
    
    try:
        # Retrieve the mentor associated with the goal
        mentor = get_mentor_for_goal(goal)
    except ObjectDoesNotExist:
        # Handle the case where no mentor is associated with the goal
        mentor = None
    
    return render(request, 'goal_detail.html', {'goal': goal, 'mentor': mentor})


#GET THE GOAL CREATED BY WHICH MENTOR
def get_mentor_for_goal(goal):
    # Check if the goal has a mentor associated with it
    if goal.mentor:
        # If the mentor is associated, return it
        return goal.mentor
    else:
        # If no mentor is associated, return None
        return None


#INDIVIDUAL  GOAL DETAILS
def goals_detail(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    return render(request, 'goal_detail.html', {'goal': goal})


#MENTOR GOAL CREATION
@login_required
def create_mentor(request):
    if request.method == 'POST':
        form = MentorForm(request.POST)
        if form.is_valid():
            mentor = form.save(commit=False)
            mentor.userId = request.user  # Set the userId to the current user
            mentor.save()
            return redirect('mentor_detail', mentor_id=mentor.mentorId)
    else:
        form = MentorForm()
    return render(request, 'create_mentor.html', {'form': form})


#MENTOR CREATED GOALS
def mentor_list(request):
    mentors = Mentor.objects.all()
    return render(request, 'mentor_list.html', {'mentors': mentors})

#USER GOALS
def my_goals(request):
    # Retrieve goals for the authenticated user
    goals = Goal.objects.filter(userId=request.user)
    return render(request, 'goal_list.html', {'goals': goals})

#MENTOR TITLE TO USER GOALS
def add_to_goal(request, mentor_id):
    mentor = get_object_or_404(Mentor, pk=mentor_id)
    
    if request.method == 'POST':
        begin_date = request.POST.get('beginDate')
        end_date = request.POST.get('endDate')
        url = request.POST.get('url')
        imageUrl = request.POST.get('imageUrl')
        status = request.POST.get('status')

        # Check if all required fields are provided
        if begin_date and end_date and url and imageUrl and status:
            # Create a new goal object using mentor details and form data
            new_goal = Goal.objects.create(
                userId=request.user,
                goalName=mentor.title,
                beginDate=begin_date,  
                endDate=end_date,
                url=url,
                imageUrl=imageUrl,
                description=mentor.description,
                price=mentor.price,
                status=status,
                mentor_id=mentor.pk
            )

            return redirect('goal_list')  
        else:
            # If any required field is missing, render the form again with an error message
            error_message = "Please provide all required fields."
            return render(request, 'add_to_goal.html', {'mentor': mentor, 'error_message': error_message})

    # If request method is not POST, render the form
    return render(request, 'add_to_goal.html', {'mentor': mentor})

#USER ACCOUNT DETAILS
@login_required
def my_account(request):
    user_details = UserDetails.objects.get(pk=request.user.pk)  # Fetch user details from UserDetails model
    return render(request, 'my_account.html', {'user_details': user_details})

#USER ACCOUNT UPDATION-WORKING
@login_required
def update_account(request):
    if request.method == 'POST':
        form = MyAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been updated successfully.')
            return redirect('my_account')
    else:
        form = MyAccountForm(instance=request.user)
    return render(request, 'update_account.html', {'form': form})

#USER ACCOUNT DELETION
@login_required
def delete_account(request):
    if request.method == 'POST':
        # Process form submission and delete user account
        request.user.delete()
        logout(request)
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('login')  # Redirect to homepage or login page
    return render(request, 'delete_account.html')


#USER GOAL DETAILS UPDATION -7
def update_goal(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    mentor = Mentor.objects.filter(title=goal.goalName).first()
    context = {
        'goal': goal,
        'mentor': mentor,  # Pass the mentor object to the template context
    }
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully.')
            return redirect('goal_detail', goal_id=goal_id)
    else:
        initial_data = {
            'goalName': goal.goalName,
            'description': goal.description,
            'price': goal.price,
        }
        form = GoalForm(instance=goal, initial=initial_data)
    
    return render(request, 'update_goal.html', context)

#USER GOAL DELETION -8
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully.')
        return redirect('goal_list')  # Redirect to home page or any other appropriate page
    return render(request, 'delete_goal.html', {'goal': goal})


def create_todo(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            begin_date = form.cleaned_data['beginDate']
            end_date = form.cleaned_data['endDate']
            if begin_date < end_date:
                if goal.beginDate <= begin_date <= goal.endDate and goal.beginDate <= end_date <= goal.endDate:
                    todo.goalId = goal
                    todo.save()
                    return redirect('goal_detail', goal_id=goal_id)
                else:
                    form.add_error(None, "Todo's dates must fall within the goal's dates")
            else:
                form.add_error(None, "Begin Date must be before End Date")
    else:
        form = TodoForm()
    return render(request, 'create_todo.html', {'form': form, 'goal': goal})


def update_todo(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('todo_detail', todo_id=todo_id)
    else:
        form = TodoForm(instance=todo)
    return render(request, 'update_todo.html', {'form': form, 'todo': todo})

def todo_delete(request, todo_id):
    # Get the todo object to delete
    todo = get_object_or_404(Todo, pk=todo_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the todo object
        todo.delete()
        # Redirect to a relevant page after deletion (for example, back to goal detail page)
        return redirect('goal_detail', goal_id=todo.goalId.pk)

    # Render the delete confirmation page
    return render(request, 'todo_delete.html', {'todo': todo})

def user_mentor_titles(request):
    # Get the logged-in user
    logged_in_user = request.user

    # Retrieve mentor titles and descriptions created by the logged-in user
    #user_mentor_titles = Mentor.objects.filter(userId=logged_in_user).values('title', 'description')
    user_mentor_titles = Mentor.objects.filter(userId=logged_in_user)

    return render(request, 'user_mentor_titles.html', {'user_mentor_titles': user_mentor_titles})


def mentor_detail(request, mentor_id):
    # Retrieve the mentor object based on mentor_id
    mentor = get_object_or_404(Mentor, pk=mentor_id)

    # Query MentorTodo objects associated with the mentor
    mentor_todos = MentorTodo.objects.filter(mentorId=mentor)

    # Extract todoName from mentor_todos
    todo_names = [todo.todoName for todo in mentor_todos]

    # Query books associated with the mentor
    #books = [book.title for book in Book]
    mentor_books=Book.objects.filter(mentor=mentor)
    books = [book.title for book in mentor_books]


    # Query websites associated with the mentor
    #websites = Website.objects.filter(mentor=mentor)
    websites = [Website.name for website in mentor.websites.all()]

    # Query meetings associated with the mentor
    #meetings = Meeting.objects.filter(mentor=mentor)
    meetings = [meeting.title for meeting in mentor.meetings.all()]

    # Query events associated with the mentor
    #events = Event.objects.filter(mentor=mentor)
    events = [event.title for event in mentor.events.all()]

    return render(request, 'mentor_detail.html', {'mentor': mentor, 
                                                   'todo_names': todo_names,
                                                   'books': books,
                                                   'websites': websites,
                                                   'meetings': meetings,
                                                   'events': events})

def create_mentor_todo(request, mentor_id):
    mentor = get_object_or_404(Mentor, pk=mentor_id)
    if request.method == 'POST':
        form = TodosForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.mentorId = mentor
            todo.save()
            # Redirect to a success page or any other page
            return redirect('mentor_detail', mentor_id=mentor_id)  # Replace 'success_page' with the name of your success page URL pattern
    else:
        form = TodosForm()
    return render(request, 'create_mentor_todo.html', {'form': form, 'mentor': mentor})


def todo_details(request, todo_id):
    # Retrieve the todo object based on todo_id
    todo = get_object_or_404(MentorTodo, pk=todo_id)
    
    # Pass the todo object to the template for rendering
    return render(request, 'todo_details.html', {'mentortodo': todo, 'mentor': todo.mentorId})


def todo_detail(request, todo_id):
    # Retrieve the todo object from the database using the todo_id
    todo = get_object_or_404(Todo, pk=todo_id)
    
    # Pass the todo object to the template
    return render(request, 'todo_detail.html', {'todo': todo})

def update_mentor(request, mentor_id):
    mentor = get_object_or_404(Mentor, pk=mentor_id)
    print(mentor)
    if request.method == 'POST':
        form = MentorForm(request.POST, instance=mentor)
        if form.is_valid():
            form.save()
            return redirect('mentor_detail', mentor_id=mentor_id)
    else:
        form = MentorForm(instance=mentor)
    return render(request, 'update_mentor.html', {'form': form, 'mentor': mentor})


def delete_mentor(request, mentor_id):
    mentor = Mentor.objects.get(pk=mentor_id)
    if request.method == 'POST':
        mentor.delete()
        return redirect('mentor_list')  # Redirect to mentor list page after deletion
    return render(request, 'delete_mentor.html', {'mentor': mentor})


def update_todos(request, todo_id):
    todo = get_object_or_404(MentorTodo, pk=todo_id)
    if request.method == 'POST':
        form = TodosForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('todo_details', todo_id=todo_id)
    else:
        form = TodosForm(instance=todo)
    return render(request, 'update_todos.html', {'form': form, 'todo': todo})

def todos_delete(request, todo_id):
    # Get the todo object to delete
    todo = get_object_or_404(MentorTodo, pk=todo_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the todo object
        todo.delete()
        # Redirect to a relevant page after deletion (for example, back to goal detail page)
        return redirect('mentor_detail', mentor_id=todo.mentorId.pk)

    # Render the delete confirmation page
    return render(request, 'todos_delete.html', {'todo': todo})


def mentor_goal_todos(request, goal_id):
    mentor_goal = get_object_or_404(Goal, pk=goal_id)
    mentor = mentor_goal.mentor
    mentor_todos = MentorTodo.objects.filter(mentorId=mentor)

    if request.method == 'POST':
        begin_date_str = request.POST.get('beginDate')
        end_date_str = request.POST.get('endDate')
        status = request.POST.get('status')
        todo_id = request.POST.get('todo_id')
        print("Begin Date:", begin_date_str)
        print("End Date:", end_date_str)
        print("Status:", status)
        print("Todo ID:", todo_id)
        print(1)
        # Convert string dates to datetime objects
        begin_date = datetime.strptime(begin_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Assuming mentor_goal.beginDate and mentor_goal.endDate are datetime objects with timezone information
        # You should replace 'timezone' with the actual timezone of your datetime objects
        if begin_date.tzinfo is None:
            begin_date = begin_date.replace(tzinfo=mentor_goal.beginDate.tzinfo)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=mentor_goal.endDate.tzinfo)

        # Check if beginDate and endDate are provided and beginDate is before endDate
        if begin_date_str and end_date_str and begin_date < end_date:
            # Check if the selected todo begin date is before the goal's begin date
            if begin_date < mentor_goal.beginDate:
                messages.warning(request, 'The todo begin date cannot be before the goal\'s begin date.')
            else:
                # Check if the selected dates are within the goal's begin and end dates
                if mentor_goal.beginDate <= begin_date <= mentor_goal.endDate and mentor_goal.beginDate <= end_date <= mentor_goal.endDate:
                    # Check if there's already a todo with the same date
                    existing_todos = Todo.objects.filter(beginDate=begin_date, endDate=end_date)
                    if existing_todos.exists():
                        messages.error(request, 'A todo already exists with the same date.')
                    else:
                        # Create a new Todo object using form data
                        mentor_todo = get_object_or_404(MentorTodo, pk=todo_id)
                        todo = Todo.objects.create(
                            goalId=mentor_goal,
                            todoName=mentor_todo.todoName,
                            url=mentor_todo.url,
                            imageUrl=mentor_todo.imageUrl,
                            description=mentor_todo.description,
                            beginDate=begin_date,
                            endDate=end_date,
                            status=status
                        )
                        messages.success(request, 'Todo added successfully.')
                        return redirect('goal_detail', goal_id=goal_id)
                else:
                    messages.error(request, 'Please select dates within the goal\'s begin and end dates.')
                    return render(request, 'goal_detail.html', {'mentor_goal': mentor_goal, 'goal_id': goal_id})
        else:
            messages.error(request, 'Please provide valid begin and end dates.')
            return render(request, 'goal_detail.html', {'mentor_goal': mentor_goal,  'goal_id': goal_id})

    return render(request, 'goal_detail.html', {'mentor_goal': mentor_goal, 'mentor_todos': mentor_todos, 'goal_id': goal_id})


def book_create(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            # Assign the goal to the book
            book.goal = goal
            book.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'book.html', {'form': form, 'goal': goal})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_detail.html', {'book': book})

def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'book_edit.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    goal_id = book.goal_id
    if request.method == 'POST':
        book.delete()
        if goal_id: 
            return redirect('book_list', goal_id=goal_id)
    return render(request, 'book_confirm_delete.html', {'book': book})


def book_list(request, goal_id):
    # Get the goal object based on the provided goal_id
    goal = get_object_or_404(Goal, pk=goal_id)

    # Filter books associated with the specified goal
    books = Book.objects.filter(goal=goal)

    return render(request, 'book_list.html', {'books': books, 'goal': goal})


def mentor_book_create(request, mentor_id):
    mentor = get_object_or_404(Mentor, pk=mentor_id)
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.mentor = mentor
            book.save()
            return redirect('books_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'book.html', {'form': form, 'mentor': mentor})


@login_required
def books_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            return redirect('books_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'book_edit.html', {'form': form})

from django.shortcuts import redirect

def books_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    mentor_id = book.mentor_id
    if request.method == 'POST':
        book.delete()
        if mentor_id: 
            return redirect('books_list', mentor_id=mentor_id)
        else:
            return redirect('books_list')  # Redirect to general book list if no mentor_id
    return render(request, 'books_delete.html', {'book': book, 'pk': pk})  # Pass 'pk' to the template


def books_list(request, mentor_id):
    # Get the goal object based on the provided goal_id
    mentor = get_object_or_404(Mentor, pk=mentor_id)

    # Filter books associated with the specified goal
    books = Book.objects.filter(mentor=mentor)

    return render(request, 'books_list.html', {'books': books, 'mentor': mentor})


def books_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books_detail.html', {'book': book})


def get_books_uploaded_by_both(request, goal_id):
    #user_id = request.user.id  # Assuming the user is authenticated
    mentor_goal = get_object_or_404(Goal, pk=goal_id)
    print(mentor_goal)
    mentor = mentor_goal.mentor  # Retrieve the mentor associated with the goal
    print(mentor)
    if mentor and mentor == mentor_goal.mentor:
        mentor_id = mentor.mentorId
        print(mentor_id)
        books = Book.objects.filter(Q(mentor_id=mentor_id) | Q(goal_id=goal_id))
    else:
        print('no')
        books = Book.objects.filter(goal_id=goal_id)  # Retrieve only the books associated with the goal

    return render(request, 'book_lists.html', {'books': books})


def event_create(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            # Assign the goal to the book
            event.goal = goal
            event.save()
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'event.html', {'form': form, 'goal': goal})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_detail.html', {'event': event})

def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'event_edit.html', {'form': form})

def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    goal_id = event.goal_id
    if request.method == 'POST':
        event.delete()
        if goal_id: 
            return redirect('event_list', goal_id=goal_id)
    return render(request, 'event_confirm_delete.html', {'event': event})


def event_list(request, goal_id):
    # Get the goal object based on the provided goal_id
    goal = get_object_or_404(Goal, pk=goal_id)

    # Filter books associated with the specified goal
    events =Event.objects.filter(goal=goal)

    return render(request, 'event_list.html', {'events': events, 'goal': goal})


def mentor_event_create(request, mentor_id):
    mentor = get_object_or_404(Mentor, pk=mentor_id)
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.mentor = mentor
            event.save()
            return redirect('events_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'event.html', {'form': form, 'mentor': mentor})


@login_required
def events_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            return redirect('events_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'event_edit.html', {'form': form})


def events_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    mentor_id = event.mentor_id
    if request.method == 'POST':
        event.delete()
        if mentor_id: 
            return redirect('events_list', mentor_id=mentor_id)
        else:
            return redirect('events_list')  # Redirect to general book list if no mentor_id
    return render(request, 'events_delete.html', {'event': event, 'pk': pk})  # Pass 'pk' to the template


def events_list(request, mentor_id):
    # Get the goal object based on the provided goal_id
    mentor = get_object_or_404(Mentor, pk=mentor_id)

    # Filter books associated with the specified goal
    events = Event.objects.filter(mentor=mentor)

    return render(request, 'events_list.html', {'events': events, 'mentor': mentor})


def events_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events_detail.html', {'event': event})


def get_events_uploaded_by_both(request, goal_id):
    # Assuming the user is authenticated
    mentor_goal = get_object_or_404(Goal, pk=goal_id)
    mentor = mentor_goal.mentor  # Retrieve the mentor associated with the goal

    current_date_time = datetime.now()

    if mentor and mentor == mentor_goal.mentor:
        mentor_id = mentor.mentorId
        events = Event.objects.filter(Q(mentor_id=mentor_id) | Q(goal_id=goal_id))
    else:
        events = Event.objects.filter(goal_id=goal_id)

    # Filter events that are current or future events
    events = events.filter(date__gte=current_date_time.date())

    return render(request, 'event_lists.html', {'events': events})


def meeting_create(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            # Assign the goal to the book
            meeting.goal = goal
            meeting.save()
            return redirect('event_detail', pk=meeting.pk)
    else:
        form = MeetingForm()
    return render(request, 'meeting.html', {'form': form, 'goal': goal})


def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'meeting_detail.html', {'meeting': meeting})

def meeting_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            meeting = form.save()
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'meeting_edit.html', {'form': form})

def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    goal_id = meeting.goal_id
    if request.method == 'POST':
        meeting.delete()
        if goal_id: 
            return redirect('meeting_list', goal_id=goal_id)
    return render(request, 'meeting_confirm_delete.html', {'meeting':meeting})


def meeting_list(request, goal_id):
    # Get the goal object based on the provided goal_id
    goal = get_object_or_404(Goal, pk=goal_id)

    # Filter books associated with the specified goal
    meetings =Meeting.objects.filter(goal=goal)

    return render(request, 'meeting_list.html', {'meetings': meetings, 'goal': goal})


def mentor_meeting_create(request, mentor_id):
    mentor = get_object_or_404(Mentor, pk=mentor_id)
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.mentor = mentor
            meeting.save()
            return redirect('meetings_detail', pk=meeting.pk)
    else:
        form = MeetingForm()
    return render(request, 'meeting.html', {'form': form, 'mentor': mentor})


from django.contrib.auth.decorators import login_required

@login_required
def meetings_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            meeting = form.save()
            return redirect('meetings_detail', pk=meeting.pk)
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'meeting_edit.html', {'form': form})

from django.shortcuts import redirect

def meetings_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    mentor_id = meeting.mentor_id
    if request.method == 'POST':
        meeting.delete()
        if mentor_id: 
            return redirect('meetings_list', mentor_id=mentor_id)
        else:
            return redirect('meetings_list')  # Redirect to general book list if no mentor_id
    return render(request, 'meetings_delete.html', {'meeting': meeting, 'pk': pk})  # Pass 'pk' to the template


def meetings_list(request, mentor_id):
    # Get the goal object based on the provided goal_id
    mentor = get_object_or_404(Mentor, pk=mentor_id)

    # Filter books associated with the specified goal
    meetings = Meeting.objects.filter(mentor=mentor)

    return render(request, 'meetings_list.html', {'meetings': meetings, 'mentor': mentor})


def meetings_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'meetings_detail.html', {'meeting': meeting})


def get_meetings_uploaded_by_both(request, goal_id):
    # Assuming the user is authenticated
    mentor_goal = get_object_or_404(Goal, pk=goal_id)
    mentor = mentor_goal.mentor  # Retrieve the mentor associated with the goal

    current_date_time = datetime.now()

    if mentor and mentor == mentor_goal.mentor:
        mentor_id = mentor.mentorId
        meetings = Meeting.objects.filter(Q(mentor_id=mentor_id) | Q(goal_id=goal_id))
    else:
        meetings = Meeting.objects.filter(goal_id=goal_id)

    # Filter events that are current or future events
    meetings =meetings.filter(date__gte=current_date_time.date())

    return render(request, 'meeting_lists.html', {'meetings': meetings})


def website_create(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    if request.method == 'POST':
        form = WebsiteForm(request.POST)
        if form.is_valid():
            website = form.save(commit=False)
            # Assign the goal to the book
            website.goal = goal
            website.save()
            return redirect('website_detail', pk=website.pk)
    else:
        form = WebsiteForm()
    return render(request, 'website.html', {'form': form, 'goal': goal})


def website_detail(request, pk):
    website = get_object_or_404(Website, pk=pk)
    return render(request, 'website_detail.html', {'website': website})

def website_edit(request, pk):
    website = get_object_or_404(Website, pk=pk)
    if request.method == 'POST':
        form = WebsiteForm(request.POST, instance=website)
        if form.is_valid():
            website = form.save()
            return redirect('website_detail', pk=website.pk)
    else:
        form = WebsiteForm(instance=website)
    return render(request, 'website_edit.html', {'form': form})

def website_delete(request, pk):
    website = get_object_or_404(Website, pk=pk)
    goal_id = website.goal_id
    if request.method == 'POST':
        website.delete()
        if goal_id: 
            return redirect('website_list', goal_id=goal_id)
    return render(request, 'website_confirm_delete.html', {'website': website})


def website_list(request, goal_id):
    # Get the goal object based on the provided goal_id
    goal = get_object_or_404(Goal, pk=goal_id)

    # Filter books associated with the specified goal
    websites = Website.objects.filter(goal=goal)

    return render(request, 'website_list.html', {'websites': websites, 'goal': goal})


def mentor_website_create(request, mentor_id):
    mentor = get_object_or_404(Mentor, pk=mentor_id)
    if request.method == 'POST':
        form = WebsiteForm(request.POST)
        if form.is_valid():
            website = form.save(commit=False)
            website.mentor = mentor
            website.save()
            return redirect('websites_detail', pk=website.pk)
    else:
        form = WebsiteForm()
    return render(request, 'website.html', {'form': form, 'mentor': mentor})


from django.contrib.auth.decorators import login_required

@login_required
def websites_edit(request, pk):
    website = get_object_or_404(Website, pk=pk)
    if request.method == 'POST':
        form = WebsiteForm(request.POST, instance=website)
        if form.is_valid():
            website = form.save()
            return redirect('websites_detail', pk=website.pk)
    else:
        form = WebsiteForm(instance=website)
    return render(request, 'website_edit.html', {'form': form})


def websites_delete(request, pk):
    website = get_object_or_404(Website, pk=pk)
    mentor_id = website.mentor_id
    if request.method == 'POST':
        website.delete()
        if mentor_id: 
            return redirect('websites_list', mentor_id=mentor_id)
        else:
            return redirect('websites_list')  # Redirect to general book list if no mentor_id
    return render(request, 'websites_delete.html', {'website': website, 'pk': pk})  # Pass 'pk' to the template


def websites_list(request, mentor_id):
    # Get the goal object based on the provided goal_id
    mentor = get_object_or_404(Mentor, pk=mentor_id)

    # Filter books associated with the specified goal
    websites = Website.objects.filter(mentor=mentor)

    return render(request, 'websites_list.html', {'websites':websites, 'mentor': mentor})


def websites_detail(request, pk):
    website = get_object_or_404(Website, pk=pk)
    return render(request, 'websites_detail.html', {'website': website})


def get_websites_uploaded_by_both(request, goal_id):
    #user_id = request.user.id  # Assuming the user is authenticated
    mentor_goal = get_object_or_404(Goal, pk=goal_id)
    print(mentor_goal)
    mentor = mentor_goal.mentor  # Retrieve the mentor associated with the goal
    print(mentor)
    if mentor and mentor == mentor_goal.mentor:
        mentor_id = mentor.mentorId
        print(mentor_id)
        websites = Website.objects.filter(Q(mentor_id=mentor_id) | Q(goal_id=goal_id))
    else:
        print('no')
        websites = Website.objects.filter(goal_id=goal_id)  # Retrieve only the books associated with the goal

    return render(request, 'website_lists.html', {'websites': websites})


def mentor_books(request, mentor_id):
    # Retrieve the mentor object based on mentor_id
    mentor_books = Book.objects.filter(mentor_id=mentor_id)
    books_ids=[book.id for book in mentor_books]
    return render(request, 'mentor_books.html', {'mentor_books': mentor_books,'books_ids':books_ids})


def mentor_events(request, mentor_id):
    # Retrieve the mentor object based on mentor_id
    mentor_events = Event.objects.filter(mentor_id=mentor_id)
    events_ids=[event.id for event in mentor_events]
    return render(request, 'mentor_events.html', {'mentor_events': mentor_events,'events_ids':events_ids})

def mentor_websites(request, mentor_id):
    # Retrieve the mentor object based on mentor_id
    mentor_websites = Website.objects.filter(mentor_id=mentor_id)
    website_ids = [website.id for website in mentor_websites]
    return render(request, 'mentor_websites.html', {'mentor_websites': mentor_websites, 'website_ids': website_ids})

def mentor_meetings(request, mentor_id, pk=None):
    # Retrieve the mentor meetings based on mentor_id
    mentor_meetings = Meeting.objects.filter(mentor_id=mentor_id)

    # Collect all meeting IDs into a list
    meeting_ids = [meeting.id for meeting in mentor_meetings]
    

    # Pass the list of meeting IDs to the template context
    return render(request, 'mentor_meetings.html', {'mentor_meetings': mentor_meetings, 'meeting_ids': meeting_ids})

