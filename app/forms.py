from django import forms
from django.contrib.auth.forms import UserCreationForm  
from app.models import CustomUser, DailyReport, SalaryCalendar, Task
from django.utils import timezone

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    department = forms.ChoiceField(choices=CustomUser.DEPARTMENT_CHOICES)
    joining_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CustomUser
        fields = ['username','email','department','joining_date','password1','password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'joining_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help texts and customize password fields
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
        
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
    


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter password'}))

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )

class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data
    
class Manager_Task_Assign_To_Employee_form(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["employee", "client_name", "time_line", "description"]
        widgets = {
            'time_line': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            "description": forms.Textarea(attrs={'class': 'form-control', 'rows': 3,"style":"resize:none"}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show non-superuser (employee) users in the dropdown
        self.fields['employee'].queryset = CustomUser.objects.filter(is_superuser=False)
        
class Manager_add_salary_form(forms.ModelForm):
    class Meta:
        model = SalaryCalendar
        fields = ["salary"]
        widgets = {
            'salary': forms.NumberInput(attrs={'class': 'form-control border border-black' }),
        }

class Employee_leave_form(forms.ModelForm):
    class Meta:
        model = SalaryCalendar
        fields = ["leave_days"]
        widgets = {
            'leave_days': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat(),  # Set minimum date to today
            })
        }
    
    def clean_leave_days(self):
        leave_date = self.cleaned_data.get('leave_days')
        if leave_date and leave_date < timezone.now().date():
            raise forms.ValidationError("Cannot select a past date")
        return leave_date
    
class Daily_report_form(forms.ModelForm):
    class Meta:
        model=DailyReport
        fields=["client_name","todays_update"]
        widgets={
            'client_name':forms.TextInput(attrs={'class':'form-control'}),
            'todays_update':forms.Textarea(attrs={'class':'form-control','rows':3,"style":"resize:none"})
        }

class Employee_update_form(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields=['username','email','department','joining_date']
        widgets={
            'username':forms.TextInput(attrs={'class':'form-control'}),
            'email':forms.EmailInput(attrs={'class':'form-control'}),
            'department':forms.Select(attrs={'class':'form-select'}),
            'joining_date':forms.DateInput(attrs={'class':'form-control','type':'date'})
        }