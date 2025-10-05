from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Problem, Schema, Solution

# This line tells the admin site to display the Problem model
admin.site.register(Problem)

# This line does the same for the Schema model
admin.site.register(Schema)

# And this one for the Solution model
admin.site.register(Solution)