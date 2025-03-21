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
        # Remove all help texts
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Customize widgets
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
        
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
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
            'time_line': forms.DateInput(attrs={'type': 'date', 'class': 'form-control' ,'placeholder':'Enter deadline'}),
            "description": forms.Textarea(attrs={'class': 'form-control', 'rows': 3,"style":"resize:none",'placehoder':'Enter task description'}),
            'employee': forms.Select(attrs={'class': 'form-select','palceholder':'Select employee'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter client name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show non-superuser (employee) users in the dropdown
        self.fields['employee'].queryset = CustomUser.objects.filter(is_superuser=False)
        
class Manager_add_salary_form(forms.ModelForm):
    class Meta:
        model = SalaryCalendar
        fields = ["salary", "pf_percentage", "esi_percentage"]
        widgets = {
            'salary': forms.NumberInput(attrs={
                'class': 'form-control border border-black',
                'placeholder': 'Enter basic salary'
            }),
            'pf_percentage': forms.NumberInput(attrs={
                'class': 'form-control border border-black',
                'placeholder': 'Enter PF % (optional)',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
            'esi_percentage': forms.NumberInput(attrs={
                'class': 'form-control border border-black',
                'placeholder': 'Enter ESI % (optional)',
                'min': '0',
                'max': '100',
                'step': '0.01'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        pf_percentage = cleaned_data.get('pf_percentage')
        esi_percentage = cleaned_data.get('esi_percentage')

        if pf_percentage and (pf_percentage < 0 or pf_percentage > 100):
            raise forms.ValidationError("PF percentage must be between 0 and 100")

        if esi_percentage and (esi_percentage < 0 or esi_percentage > 100):
            raise forms.ValidationError("ESI percentage must be between 0 and 100")

        return cleaned_data


class Employee_leave_form(forms.ModelForm):
    class Meta:
        model = SalaryCalendar
        fields = ["leave_days", "leave_type"]
        widgets = {
            'leave_days': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat(),
            }),
            'leave_type': forms.Select(attrs={
                'class': 'form-control',
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
            'client_name':forms.TextInput(attrs={'class':'form-control border border-black','placeholder':'Enter client name'}),
            'todays_update':forms.Textarea(attrs={'class':'form-control border border-black', "placeholder":"Enter today's update",'rows':3,"style":"resize:none"})
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