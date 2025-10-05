from django.db import models

# Create your models here.

class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    solution_explanation = models.TextField(help_text="The detailed, step-by-step breakdown of the solution logic.")
    
    def __str__(self):
        return self.title

class Schema(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='schemas')
    # The full SQL statement to create a table and insert its data
    script = models.TextField(help_text="The CREATE TABLE and INSERT INTO statements for one table.")

    def __str__(self):
        return f"Schema for {self.problem.title}"

class Solution(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE)
    query = models.TextField(help_text="The correct SQL query to solve the problem.")

    def __str__(self):
        return f"Solution for {self.problem.title}"