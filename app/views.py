from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.mail import send_mail
from .models import CustomUser, DailyReport, SalaryCalendar, Task
from .forms import SignupForm, LoginForm,ForgotPasswordForm, ResetPasswordForm, Manager_Task_Assign_To_Employee_form,Manager_add_salary_form,Employee_leave_form,Daily_report_form,Employee_update_form
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError


# Create your views here.

def send_email_otp(user):
    user.generate_otp()
    subject = "Kindly Verify your Email Address"
    message = f"otp for your Account verification is {user.otp}"
    from_email = "abhinavabhi192018@gmail.com"
    recipient_list = [user.email]
    send_mail(subject,message,from_email,recipient_list)




# view for register/otp-verification/login/logout 

def SignupView(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.is_verified = False
                
                # Generate unique employee ID
                try:
                    last_user = CustomUser.objects.filter(
                        employee_id__isnull=False,
                        employee_id__startswith='IZ',
                        is_superuser=False
                    ).order_by('-employee_id').first()
                    
                    if last_user and last_user.employee_id:
                        try:
                            last_num = int(last_user.employee_id[2:])  # Get number after 'IZ'
                            next_num = last_num + 1
                            new_id = f'IZ{next_num:02d}'
                            
                            # Make sure the new ID is unique
                            while CustomUser.objects.filter(employee_id=new_id).exists():
                                next_num += 1
                                new_id = f'IZ{next_num:02d}'
                                
                            user.employee_id = new_id
                        except (ValueError, IndexError):
                            # If parsing fails, start from IZ0001
                            user.employee_id = 'IZ01'
                    else:
                        # If no existing users, start from IZ0001
                        user.employee_id = 'IZ01'
                except Exception as e:
                    messages.error(request, f"Error generating employee ID: {str(e)}")
                    return render(request, 'signup.html', {'form': form})
                
                user.save()
                send_email_otp(user)
                return redirect('verify')
                
            except IntegrityError as e:
                if 'username' in str(e).lower():
                    messages.error(request, "Username already exists. Please choose a different username.")
                elif 'email' in str(e).lower():
                    messages.error(request, "Email already registered. Please use a different email.")
                elif 'employee_id' in str(e).lower():
                    messages.error(request, "Employee ID generation failed. Please try again.")
                else:
                    messages.error(request, f"Error creating account: {str(e)}")
                return render(request, 'signup.html', {'form': form})
            except Exception as e:
                messages.error(request, f"Unexpected error: {str(e)}")
                return render(request, 'signup.html', {'form': form})
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def Verify_otp_View(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user = CustomUser.objects.get(otp=otp)
        if otp == user.otp:
            user.is_active = True
            user.is_verified = True
            user.otp = None
            user.save()
            return redirect('login')
    return render(request, 'verify.html')


def LoginView(request):
    if request.method == 'POST':
        form_instance = LoginForm(request.POST)
        if form_instance.is_valid():
            username = form_instance.cleaned_data.get('username')
            password = form_instance.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    print("Redirecting superuser to assign-task-employee")
                    return redirect('assign-task-employee')
                else:
                    return redirect('employee-tasks')
    else:
        form_instance = LoginForm()
    return render(request, 'login.html', {'form': form_instance})


def LOgoutView(request):
    logout(request)
    return redirect('login')





# reset password 

def Forgot_password_View(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                # Generate and send OTP
                send_email_otp(user)
                request.session['reset_email'] = email
                return redirect('verify-reset-otp')
            except CustomUser.DoesNotExist:
                messages.error(request, "No account found with this email address.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

def Verify_reset_otp_View(request):
    if 'reset_email' not in request.session:
        return redirect('forgot-password')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(email=request.session['reset_email'])
            if otp == user.otp:
                request.session['reset_user_id'] = user.id
                user.otp = None
                user.save()
                return redirect('reset-password')
            else:
                messages.error(request, "Invalid OTP")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found")
    return render(request, 'verify_reset_otp.html')

def reset_password_View(request):
    if 'reset_user_id' not in request.session:
        return redirect('forgot-password')
        
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.get(id=request.session['reset_user_id'])
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Clear session data
            del request.session['reset_email']
            del request.session['reset_user_id']
            
            messages.success(request, "Password reset successfully!")
            return redirect('login')
    else:
        form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form})





# manager 




def assign_task_to_employee(request):
    if not request.user.is_superuser:
        return redirect('employee-dashboard')  # Only managers can assign tasks
        
    if request.method == 'POST':
        form = Manager_Task_Assign_To_Employee_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager-task-list')  # Redirect to task list after successful assignment
    else:
        form = Manager_Task_Assign_To_Employee_form()
    
    return render(request, 'Manager_assign_task.html', {'form': form})






from django.utils import timezone

def Manager_assigned_task_list(request):
    
    current_date = timezone.now().date()
    tasks = Task.objects.filter(time_line__gte=current_date).order_by('time_line')
    return render(request, 'Manager_assigned_task_list.html', {'tasks': tasks})



 
def Manager_list_all_employees(request):
    if not request.user.is_superuser:
        return redirect('employee-dashboard')
        
    employees = CustomUser.objects.filter(is_superuser=False)
    
    # Get current salary for each employee
    for employee in employees:
        employee.current_salary = SalaryCalendar.objects.filter(employee=employee).last()
    
    return render(request, 'Manager_list_all_employees.html', {'employees': employees})



def Manager_employee_daily_report_view(request):
    if not request.user.is_superuser:
        return redirect('employee-dashboard')

    # Initialize queryset with all reports
    reports = DailyReport.objects.all()

    # Get filter parameters
    selected_date = request.GET.get('date')
    selected_employee = request.GET.get('employee')

    # Apply date filter
    if selected_date:
        # Convert string date to datetime
        try:
            filter_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
            reports = reports.filter(report_date=filter_date)
        except ValueError:
            messages.error(request, "Invalid date format")
    
    # Apply employee filter
    if selected_employee:
        reports = reports.filter(employee=selected_employee)

    # Get all employees for the filter dropdown
    employees = CustomUser.objects.filter(is_superuser=False)

    # Order reports by date descending
    reports = reports.order_by('-report_date')

    context = {
        'qs': reports,
        'employees': employees,
        'selected_date': selected_date,
        'selected_employee': selected_employee,
        'today': timezone.now().date()
    }
    
    return render(request, 'Manager_employee_daily_report.html', context)



def Manager_employee_details(request, pk):

        employee = CustomUser.objects.get(pk=pk)
        current_date = timezone.now().date()
        
        # Get current month's leaves
        current_month_leaves = SalaryCalendar.objects.filter(
            employee=employee,
            leave_days__month=current_date.month,
            leave_days__year=current_date.year
        )
        
        # Get current salary
        current_salary = SalaryCalendar.objects.filter(employee=employee).last()
        
        context = {
            'employee': employee,
            'current_salary': current_salary,
            'month_leaves_count': current_month_leaves.count(),
            'current_month': current_date.strftime('%B'),
            'month_leaves': current_month_leaves,  # For detailed leave dates
        }
        
        return render(request, 'Manager_employee_details.html', context)
        
    




def Manager_employee_salary_add_nd_update_view(request, pk):
    if not request.user.is_superuser:
        return redirect('employee-dashboard')
        
    try:
        employee = CustomUser.objects.get(pk=pk)
        
        if request.method == 'POST':
            salary_form = Manager_add_salary_form(request.POST)
            if salary_form.is_valid():
                salary = salary_form.save(commit=False)
                salary.employee = employee
                salary.leave_days = timezone.now().date()
                
                try:
                    salary.save()
                    # Calculate deductions for success message
                    pf_message = f", PF Deduction: ₹{salary.pf_amount:.2f}" if salary.pf_percentage else ""
                    esi_message = f", ESI Deduction: ₹{salary.esi_amount:.2f}" if salary.esi_percentage else ""
                    net_salary = f", Net Salary: ₹{salary.net_salary:.2f}"
                    
                    messages.success(
                        request, 
                        f"Salary added successfully for {employee.username}"
                        f" (Basic: ₹{salary.salary:.2f}{pf_message}{esi_message}{net_salary})"
                    )
                except Exception as e:
                    messages.error(request, f"Error saving salary: {str(e)}")
                
                return redirect('manager-employee-details', pk=pk)
        else:
            salary_form = Manager_add_salary_form()
        
        # Get current salary if exists
        current_salary = SalaryCalendar.objects.filter(employee=employee).last()
        
        # Calculate total deductions for current month
        current_date = timezone.now().date()
        month_leaves = SalaryCalendar.objects.filter(
            employee=employee,
            leave_days__month=current_date.month,
            leave_days__year=current_date.year
        )
        
        context = {
            'employee': employee,
            'salary_form': salary_form,
            'current_salary': current_salary,
            'month_leaves_count': month_leaves.count(),
            'current_month': current_date.strftime('%B'),
            'deductions': {
                'pf': current_salary.pf_amount if current_salary else 0,
                'esi': current_salary.esi_amount if current_salary else 0,
                'total': current_salary.total_deductions if current_salary else 0
            }
        }
        
        return render(request, 'Manager_employee_add-salary.html', context)
        
    except CustomUser.DoesNotExist:
        messages.error(request, "Employee not found")
        return redirect('manager-employee-list')





def Manager_delete_employee(request,pk):
    if not request.user.is_superuser:
        return redirect("employee-dashboard")
    CustomUser.objects.get(pk=pk).delete()
    return redirect('manager-employee-list')






# employee 

def Employee_task_list_view(request):

    if request.user.is_superuser:
        return redirect('manager-task-list')
    
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        
        if not task_id:
            messages.error(request, "Invalid task ID!")
            return redirect('employee-task-list')
            
        try:
            task = Task.objects.get(id=int(task_id), employee=request.user)
            task.status = new_status
            task.save()
            messages.success(request, "Task status updated successfully!")
        except (Task.DoesNotExist, ValueError):
            messages.error(request, "Task not found or invalid ID!")
        
        return redirect('employee-tasks')
    
    current_date = timezone.now().date()
    tasks = Task.objects.filter(employee=request.user,time_line__gte=current_date).order_by("time_line")
    return render(request, 'Employee_task_list.html', {'tasks': tasks})





def Employee_leave_view(request):
    if request.method == 'POST':
        form = Employee_leave_form(request.POST)
        if form.is_valid():
            leave_date = form.cleaned_data['leave_days']
            
            # Check if date is not in past
            if leave_date < timezone.now().date():
                messages.error(request, "Cannot select a past date")
                return redirect('employee-leave')
            
            # Check existing salary record
            salary_record = SalaryCalendar.objects.filter(employee=request.user).last()
            if not salary_record:
                messages.error(request, "No salary record found. Please contact your manager.")
                return redirect('employee-leave')
            
            # Check for existing leave on same date
            if SalaryCalendar.objects.filter(
                employee=request.user,
                leave_days=leave_date
            ).exists():
                messages.error(request, "You already have a leave request for this date")
                return redirect('employee-leave')
            
            # Check leaves in current month
            current_month_leaves = SalaryCalendar.objects.filter(
                employee=request.user,
                leave_days__month=leave_date.month,
                leave_days__year=leave_date.year
            ).count()

            # Calculate salary after leave
            original_salary = salary_record.salary
            if current_month_leaves >= 1:
                # Calculate per day salary 
                per_day_salary = original_salary / 30
                # Deduct one day salary
                new_salary = original_salary - per_day_salary
                messages.warning(request, 
                    f"This is your {current_month_leaves + 1}th leave. Salary deduction: ₹{per_day_salary:.2f}")
            else:
                new_salary = original_salary
                messages.info(request, "First leave of the month - No salary deduction")
            
            # Create new leave record
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.salary = new_salary
            leave.save()
            
            messages.success(request, f"Leave request submitted for {leave_date}")
            return redirect('employee-leave')
    else:
        form = Employee_leave_form()
    
    # Get all leave records
    all_leaves = SalaryCalendar.objects.filter(
        employee=request.user
    ).order_by('-leave_days')
    
    current_date = timezone.now().date()
    
    # Calculate total salary deductions this month
    current_month_leaves = all_leaves.filter(
        leave_days__month=current_date.month,
        leave_days__year=current_date.year
    )
    
    current_salary = SalaryCalendar.objects.filter(employee=request.user).last()
    total_deduction = 0
    
    if current_salary and current_month_leaves.count() > 1:
        per_day_salary = current_salary.salary / 30
        total_deduction = per_day_salary * (current_month_leaves.count() - 1)
    
    context = {
        'form': form,
        'past_leaves': all_leaves.filter(leave_days__lt=current_date),
        'upcoming_leaves': all_leaves.filter(leave_days__gte=current_date),
        'month_leaves_count': current_month_leaves.count(),
        'current_month': current_date.strftime('%B'),
        'current_salary': current_salary,
        'total_deduction': total_deduction,
        'salary_after_deduction': current_salary.salary - total_deduction if current_salary else 0
    }
    
    return render(request, 'Employee_leave.html', context)

def Employee_daily_report_view(request):
    if request.user.is_superuser:
        return redirect('manager-dashboard')
        
    if request.method == "POST":
        form = Daily_report_form(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.employee = request.user
            report.save()
            messages.success(request, "Report Submitted Successfully")
            return redirect('employee-daily-report')    
        else:
            messages.error(request, "Please check your form inputs")
    else:
        form = Daily_report_form()

    # Get today's reports
    today_reports = DailyReport.objects.filter(
        employee=request.user,
        report_date=timezone.now().date()
    ).order_by('-report_date')

    context = {
        "form": form,
        "today_reports": today_reports
    }
    
    return render(request, "employee_daily_report.html", context)




def Employee_about_view(request):
    about=CustomUser.objects.get(id=request.user.id)
    salary=SalaryCalendar.objects.filter(employee=about).last()
    return render(request,"employee_about.html",{'about':about,'salary':salary})


def Employee_Details_update_view(request):
    if request.method == 'POST':
        form = Employee_update_form(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('employee-about')
    else:
        form = Employee_update_form(instance=request.user)
    return render(request, 'employee_update.html', {'form': form})


def Employee_Details_update_view(request):
    if request.method == 'POST':
        form = Employee_update_form(request.POST, instance=request.user)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                # Add validation for any unique fields
                if CustomUser.objects.exclude(id=request.user.id).filter(email=user.email).exists():
                    messages.error(request, "This email is already in use.")
                    return render(request, 'employee_update.html', {'form': form})
                
                user.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('employee-about')
            except Exception as e:
                messages.error(request, f"Error updating profile: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = Employee_update_form(instance=request.user)
    
    return render(request, 'employee_update.html', {
        'form': form,
        'employee': request.user
    })