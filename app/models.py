from django.db import models
from django.utils import timezone
from datetime import date
from random import randint
from django.contrib.auth.models import AbstractUser
from decimal import Decimal

class CustomUser(AbstractUser):
    DEPARTMENT_CHOICES = [
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        ('FIN', 'Finance'),
        ('MKT', 'Marketing'),
        ('OPS', 'Operations'),
    ]

    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(unique=True)
    employee_id = models.CharField(max_length=10, unique=True, null=True)
    department = models.CharField(max_length=3, choices=DEPARTMENT_CHOICES, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    def generate_otp(self):
        self.otp = str(randint(1000, 9999))
        self.save()

    def save(self, *args, **kwargs):
        if not self.employee_id and not self.is_superuser:
            # Generate employee ID only for non-superusers (employees)
            last_user = CustomUser.objects.filter(
                employee_id__isnull=False
            ).order_by('-employee_id').last()
            
            if last_user and last_user.employee_id:
                # Extract number from last ID and increment
                try:
                    last_num = int(last_user.employee_id[2:])  # Get number after 'IZ'
                    next_num = last_num + 1
                    self.employee_id = f'IZ{next_num:02d}'  # Pad with zeros to 2 digits
                except ValueError:
                    self.employee_id = 'IZ01'  # Fallback if parsing fails
            else:
                self.employee_id = 'IZ01'  # First employee
        super().save(*args, **kwargs)
        

    def __str__(self):
        if self.is_superuser:
            return f"Manager - {self.username}"
        return f"{self.employee_id} - {self.username}"
    

class DailyReport(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=255)
    report_date = models.DateField(default=timezone.now)
    todays_update = models.TextField()

    def __str__(self):
        return f'Report by {self.employee.username} on {self.report_date}'




class SalaryCalendar(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_days = models.DateField(null=True, blank=True)  # Make it nullable
    salary = models.FloatField()
    pf_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True, 
        blank=True,
    )
    esi_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True, 
        blank=True,
    )
    leave_type = models.CharField(
        max_length=4,
        choices=[('full', 'Full Day'), ('half', 'Half Day')],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def per_day_salary(self):
        """Calculate per day salary"""
        return Decimal(str(self.salary)) / Decimal('30.0')

    @property
    def deduction_amount(self):
        """Calculate leave deduction amount based on leave type"""
        if self.leave_type == 'half':
            return self.per_day_salary / Decimal('2.0')
        return self.per_day_salary

    @property
    def net_salary(self):
        """Calculate net salary after all deductions"""
        return Decimal(str(self.salary)) - self.total_deductions

    def __str__(self):
        return f'Calendar for {self.employee.username}'
    
    @property
    def pf_amount(self):
        """Calculate PF deduction if applicable"""
        if self.pf_percentage:
            return (Decimal(str(self.salary)) * self.pf_percentage) / Decimal('100.0')
        return Decimal('0.0')

    @property
    def esi_amount(self):
        """Calculate ESI deduction if applicable"""
        if self.esi_percentage:
            return (Decimal(str(self.salary)) * self.esi_percentage) / Decimal('100.0')
        return Decimal('0.0')

    @property
    def per_day_salary(self):
        """Calculate per day salary"""
        return Decimal(str(self.salary)) / Decimal('30.0')

    @property
    def total_deductions(self):
        """Calculate total deductions including PF and ESI"""
        return self.pf_amount + self.esi_amount

    @property
    def net_salary(self):
        """Calculate net salary after all deductions"""
        return Decimal(str(self.salary)) - self.total_deductions

    def __str__(self):
        return f'Calendar for {self.employee.username}'


class Task(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    time_line = models.DateField()
    status_choices = (
        ('accepted', 'Accepted'),
        ('not_accepted', 'Not Accepted'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=status_choices, default='not_accepted')
    update_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f'Task for {self.client_name} - {self.status} by {self.employee.username}'