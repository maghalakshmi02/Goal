from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,UserChangeForm, PasswordChangeForm
from .models import UserDetails,Goal ,Book, Website, Event, Meeting,MentorTodo,Mentor,Todo
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    firstName = forms.CharField(max_length=30, required=True)
    lastName = forms.CharField(max_length=30, required=True)
    phoneNo = forms.CharField(max_length=20, required=False)
    linkedIn = forms.CharField(max_length=40, required=False)

    class Meta:
        model = UserDetails
        fields = ['username', 'firstName', 'lastName', 'email', 'phoneNo', 'linkedIn', 'password1', 'password2']



class UserLoginForm(AuthenticationForm):
    class Meta:
        model = UserDetails
        fields = ['username', 'password']




class GoalForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    PRICE_CHOICES = [
        ('Free', 'Free'),
        ('Paid', 'Paid'),
    ]
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, label='Status', required=True)
    price = forms.ChoiceField(choices=PRICE_CHOICES, label='Price', required=True)

    class Meta:
        model = Goal
        fields = ['goalName', 'beginDate', 'endDate', 'url', 'imageUrl', 'description', 'price', 'status']
        widgets = {
            'beginDate': forms.DateInput(attrs={'type': 'date'}),
            'endDate': forms.DateInput(attrs={'type': 'date'}),
            'goalName': forms.TextInput(attrs={'class': 'small-inputs'}),
            'description': forms.Textarea(attrs={'class': 'small-input', 'rows': 4, 'cols': 50}),
        }

    def clean(self):
        cleaned_data = super().clean()
        begin_date = cleaned_data.get('beginDate')
        end_date = cleaned_data.get('endDate')

        if begin_date and end_date and begin_date >= end_date:
            raise forms.ValidationError("End date must be after begin date.")
        
        return cleaned_data


class MentorForm(forms.ModelForm):
    PRICE_CHOICES = [
        ('Free', 'Free'),
        ('Paid', 'Paid'),
    ]
    price = forms.ChoiceField(choices=PRICE_CHOICES, label='Price', required=True)
    class Meta:
        model = Mentor
        fields = ['title', 'description', 'price', 'amount', 'discount', 'currencyType', 'ratings', 'availability']

    widgets = {
        'title': forms.TextInput(attrs={'class': 'small-inputs'}),
        'description': forms.Textarea(attrs={'class': 'small-input', 'rows': 2, 'cols': 50}),
    }



class AddToGoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['goalName', 'beginDate', 'endDate', 'url', 'imageUrl', 'description', 'price', 'status']#['goalName', 'description', 'price', 'status']  # Add fields as needed



class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ['email', 'firstName', 'lastName', 'phoneNo', 'linkedIn', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }



class MyAccountForm(UserChangeForm):
    password = None  # Exclude password field from this form

    class Meta(UserChangeForm.Meta):
        model = UserDetails
        fields = ['username', 'email', 'firstName', 'lastName', 'phoneNo', 'linkedIn']




class TodoForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, label='Status', required=True)

    class Meta:
        model = Todo
        fields = [ 'todoName', 'beginDate', 'endDate', 'url', 'imageUrl', 'description', 'status']#, 'price'
        widgets = {
            'beginDate': forms.DateInput(attrs={'type': 'date'}),
            'endDate': forms.DateInput(attrs={'type': 'date'}),
            'todoName': forms.TextInput(attrs={'class': 'small-inputs'}),
            'description': forms.Textarea(attrs={'class': 'small-input', 'rows': 4, 'cols': 50}),

        }
        

class TodosForm(forms.ModelForm):

    class Meta:
        model = MentorTodo
        fields = [ 'todoName',  'url', 'imageUrl', 'description']#'beginDate', 'endDate', 'status'
        widgets = {
            
            'todoName': forms.TextInput(attrs={'class': 'small-input'}),
            'description': forms.Textarea(attrs={'class': 'small-input', 'rows': 4, 'cols': 60}),

        }




class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'ratings', 'isbn', 'description', 'url']

class WebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ['name', 'url', 'description']

class EventForm(forms.ModelForm):
    MODE_CHOICES = [
        ('On-line', 'On-line'),
        ('Off-line', 'Off-line'),
        
    ]
    
    mode = forms.ChoiceField(choices=MODE_CHOICES, label='mode', required=True)
    class Meta:
        model = Event
        fields = ['title', 'date', 'location', 'description', 'mode', 'url']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
    }

class MeetingForm(forms.ModelForm):
    MODE_CHOICES = [
        ('On-line', 'On-line'),
        ('Off-line', 'Off-line'),
        
    ]
    
    mode = forms.ChoiceField(choices=MODE_CHOICES, label='mode', required=True)
    class Meta:
        model = Meeting
        fields = ['title', 'date', 'time', 'location', 'mode', 'agenda', 'url']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
    }



from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if not UserDetails.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no user registered with the specified email address.")
        return email


class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm new password', widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if 'new_password1' in cleaned_data and 'new_password2' in cleaned_data:
            if cleaned_data['new_password1'] != cleaned_data['new_password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data
