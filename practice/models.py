# --- START OF FILE models.py ---

# practice/models.py
from django.db import models

# Create your models here.

class Problem(models.Model):
    title = models.CharField(max_length=200, unique=True, help_text="A unique title for the problem")
    description = models.TextField(help_text="The markdown description of the SQL problem.") # Keep as description
    solution_explanation = models.TextField(help_text="The detailed, step-by-step breakdown of the solution logic.")
    
    def __str__(self):
        return self.title

class Schema(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='schemas')
    script = models.TextField(help_text="The CREATE TABLE and INSERT INTO statements for one table.")
    order = models.PositiveIntegerField(default=0, help_text="Order in which schema scripts should be executed for a problem.") # THIS IS THE NEW FIELD

    class Meta:
        ordering = ['order']
        # If you need uniqueness across problem and order, uncomment this:
        unique_together = ('problem', 'order') # Recommended for enforcing order uniqueness

    def __str__(self):
        return f"Schema for {self.problem.title} (Order: {self.order})"

class Solution(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='solution') # Keep related_name
    query = models.TextField(help_text="The correct SQL query to solve the problem.")

    def __str__(self):
        return f"Solution for {self.problem.title}"