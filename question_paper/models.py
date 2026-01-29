from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse


# ================= IMAGE POSITION CHOICES =================
QUESTION_IMAGE_POSITION_CHOICES = [
    ("top", "Top - Text above image"),
    ("middle", "Middle - Text above and below image"),
    ("bottom", "Bottom - Text below image"),
]

# Add image size choices
IMAGE_SIZE_CHOICES = [
    ("small", "Small (200px)"),
    ("medium", "Medium (400px)"),
    ("large", "Large (600px)"),
    ("xlarge", "Extra Large (800px)"),
]


# -------------------- Base Question Model --------------------
class BaseQuestion(models.Model):
    """Base model for common question fields"""
    module = models.IntegerField()
    module_outcome = models.CharField(max_length=10, blank=True, null=True)
    level = models.CharField(max_length=1, choices=[("U", "Understanding"), ("R", "Remembering"), ("A", "Application")])
    
    # Main question text (appears above image or as only text)
    question = models.TextField()
    
    # Text below image (only used when position is "middle")
    text_below_image = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Text Below Image",
        help_text="Text that will appear below the image (only for middle position)"
    )
    
    # Image fields
    question_image = models.ImageField(upload_to="question_images/", blank=True, null=True)
    question_image_position = models.CharField(
        max_length=10,
        choices=QUESTION_IMAGE_POSITION_CHOICES,
        default="top",
        blank=True,
        null=True,
    )
    question_image_size = models.CharField(
        max_length=10,
        choices=IMAGE_SIZE_CHOICES,
        default="medium",
        blank=True,
        null=True,
    )
    
    # Sub-question support
    is_sub_question = models.BooleanField(default=False)
    parent_question = models.ForeignKey('self', on_delete=models.CASCADE, 
                                       blank=True, null=True, related_name='sub_questions')
    sub_question_letter = models.CharField(max_length=5, blank=True, null=True, 
                                          help_text="For sub-questions: a, b, c, etc.")
    
    class Meta:
        abstract = True
        
    def get_split_question_text(self):
        """
        Split question text based on image position.
        Returns: (text_above, text_below)
        """
        if self.question_image_position == 'middle':
            # For middle position, use question field for text above
            # and text_below_image field for text below
            text_above = self.question or ""
            text_below = self.text_below_image or ""
            return text_above, text_below
        
        elif self.question_image_position == 'top':
            # Top: All text above image (use question field)
            return self.question or "", ""
        
        elif self.question_image_position == 'bottom':
            # Bottom: All text below image (use question field)
            return "", self.question or ""
        
        else:  # Default (top)
            return self.question or "", ""
    
    def get_text_above_image(self):
        """Get text that should appear above the image"""
        text_above, _ = self.get_split_question_text()
        return text_above
    
    def get_text_below_image(self):
        """Get text that should appear below the image"""
        _, text_below = self.get_split_question_text()
        return text_below
    
    def get_combined_question_text(self):
        """Get combined question text for form initialization"""
        if self.question_image_position == 'middle' and self.text_below_image:
            return f"{self.question}\n{self.text_below_image}"
        return self.question


# -------------------- Dropdown Lookup Models --------------------
class Revision(models.Model):
    """Model to store available revision years"""
    year = models.CharField(max_length=10, unique=True, help_text="Revision year (e.g., 2015, 2021)")
    is_active = models.BooleanField(default=True, help_text="Show this revision in dropdown")
    
    class Meta:
        ordering = ['-year']
        verbose_name = "Revision"
        verbose_name_plural = "Revisions"
    
    def __str__(self):
        return self.year


class ExamName(models.Model):
    """Model to store predefined exam names"""
    name = models.CharField(max_length=500, unique=True, help_text="Exam name")
    is_active = models.BooleanField(default=True, help_text="Show this exam name in dropdown")
    display_order = models.IntegerField(default=0, help_text="Order in dropdown (lower numbers first)")
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Exam Name"
        verbose_name_plural = "Exam Names"
    
    def __str__(self):
        return self.name


class SubjectCode(models.Model):
    """Model to store subject codes with associated details"""
    code = models.CharField(max_length=20, unique=True, help_text="Subject code")
    subject_name = models.CharField(max_length=500, help_text="Full subject name")
    duration_hours = models.IntegerField(default=3, help_text="Exam duration in hours")
    is_active = models.BooleanField(default=True, help_text="Show this subject in dropdown")
    
    class Meta:
        ordering = ['code']
        verbose_name = "Subject Code"
        verbose_name_plural = "Subject Codes"
    
    def __str__(self):
        return f"{self.code} - {self.subject_name}"


class QuestionModule(models.Model):
    """Model to store available modules (e.g. 1, 2, 3, 4)"""
    module_number = models.IntegerField(unique=True, help_text="Module Number")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['module_number']
        verbose_name = "Module"
        verbose_name_plural = "Modules"

    def __str__(self):
        return str(self.module_number)


class ModuleOutcome(models.Model):
    """Model to store module outcomes (e.g. M1.01)"""
    outcome_code = models.CharField(max_length=20, unique=True, help_text="Module Outcome Code (e.g. M1.01)")
    description = models.CharField(max_length=500, blank=True, null=True, help_text="Description of the outcome")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['outcome_code']
        verbose_name = "Module Outcome"
        verbose_name_plural = "Module Outcomes"

    def __str__(self):
        return self.outcome_code


class SectionInstruction(models.Model):
    """Model to store preset section instructions"""
    text = models.TextField(help_text="Instruction text")
    part_type = models.CharField(max_length=1, choices=[('A', 'Part A'), ('B', 'Part B'), ('C', 'Part C')], default='A')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Section Instruction"
        verbose_name_plural = "Section Instructions"

    def __str__(self):
        return f"{self.get_part_type_display()}: {self.text[:50]}..."


class SystemConfiguration(models.Model):
    """Singleton model for system-wide settings"""
    default_max_marks = models.IntegerField(default=75, help_text="Default Maximum Marks for new Question Papers")
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"

    def save(self, *args, **kwargs):
        if not self.pk and SystemConfiguration.objects.exists():
            existing = SystemConfiguration.objects.first()
            existing.default_max_marks = self.default_max_marks
            existing.save()
            self.pk = existing.pk
            return
        super().save(*args, **kwargs)


    def __str__(self):
        return "System Configuration"


# -------------------- QuestionPaper --------------------
class QuestionPaper(models.Model):
    question_paper_code = models.IntegerField()
    revesion = models.CharField(max_length=10)
    subject_code = models.CharField(max_length=20)
    exam_name = models.CharField(max_length=500)
    subject_name = models.CharField(max_length=500)
    time = models.IntegerField(help_text="Exam duration in hours")
    exam_marks = models.IntegerField(default=75, help_text="Maximum Marks to be printed on the paper")
    maximum_mark = models.IntegerField(null=True, blank=True)
    
    module1_hours = models.IntegerField(null=True, blank=True)
    module2_hours = models.IntegerField(null=True, blank=True)
    module3_hours = models.IntegerField(null=True, blank=True)
    module4_hours = models.IntegerField(null=True, blank=True)
    
    percent_R = models.FloatField(null=True, blank=True)
    percent_U = models.FloatField(null=True, blank=True)
    percent_A = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.subject_name} ({self.subject_code})"
    
    def clean(self):
        """Validate percentages"""
        r = self.percent_R or 0
        u = self.percent_U or 0
        a = self.percent_A or 0
        
        if (r + u + a) > 0 and abs((r + u + a) - 100) > 0.5:
            raise ValidationError("Sum of R + U + A should be around 100%.")

    @property
    def get_status(self):
        """Determine the current status based on completed parts"""
        if not hasattr(self, 'part_a_details'):
            return "Part A Pending"
        if not hasattr(self, 'part_b_details'):
            return "Part B Pending"
        if not hasattr(self, 'part_c_details'):
            return "Part C Pending"
        return "Complete"

    @property
    def get_resume_url(self):
        """Get the URL to resume creation from the last incomplete step"""
        if not hasattr(self, 'part_a_details'):
            return reverse("question_paper:PartA")
        if not hasattr(self, 'part_b_details'):
            return reverse("question_paper:PartB")
        if not hasattr(self, 'part_c_details'):
            return reverse("question_paper:PartC")
        return reverse("question_paper:review", kwargs={'pk': self.pk})


# -------------------- PART A --------------------
class PartA(models.Model):
    info = models.TextField()
    each_question_mark = models.IntegerField(default=1)
    total = models.IntegerField(default=0)
    details = models.OneToOneField(QuestionPaper, on_delete=models.CASCADE, related_name="part_a_details")
    
    def total_marks(self):
        return self.total
    
    def get_main_questions(self):
        """Get only main questions (not sub-questions)"""
        return self.questions.filter(is_sub_question=False)
    
    def __str__(self):
        return f"Part A - {self.details.subject_name}"


class PartAQuestions(BaseQuestion):
    part_a = models.ForeignKey(PartA, on_delete=models.CASCADE, related_name="questions")
    answer = models.TextField()
    answer_equation = models.TextField(blank=True, null=True, help_text="LaTeX equation for answer")
    answer_image = models.ImageField(upload_to="answers/", blank=True, null=True)
    
    class Meta:
        ordering = ['id', 'sub_question_letter']
        verbose_name = "Part A Question"
        verbose_name_plural = "Part A Questions"
    
    def __str__(self):
        if self.is_sub_question and self.sub_question_letter:
            parent_id = self.parent_question.id if self.parent_question else "?"
            return f"Q{parent_id}({self.sub_question_letter}) - Part A"
        return f"Q{self.id} - Part A: {self.question[:60]}..."
    
    def get_full_question_display(self):
        """Get the full question text with image position consideration"""
        text_above, text_below = self.get_split_question_text()
        
        display = ""
        if text_above:
            display += text_above
        if self.question_image:
            display += f"\n[Image: {self.question_image.name}]"
        if text_below:
            display += f"\n{text_below}"
        
        return display.strip()


# -------------------- PART B --------------------
class PartB(models.Model):
    info = models.TextField()
    required_questions = models.IntegerField()
    each_questions_mark = models.IntegerField()
    total = models.IntegerField()
    details = models.OneToOneField(QuestionPaper, on_delete=models.CASCADE, related_name="part_b_details")
    
    def get_main_questions(self):
        """Get only main questions (not sub-questions)"""
        return self.questions.filter(is_sub_question=False)
    
    def __str__(self):
        return f"Part B - {self.details.subject_name}"


class PartBQuestions(BaseQuestion):
    part_b = models.ForeignKey(PartB, on_delete=models.CASCADE, related_name="questions")
    
    # Answer fields
    answer_text = models.TextField(blank=True, null=True)
    answer_equation = models.TextField(blank=True, null=True)
    answer_image = models.ImageField(upload_to="answers/", blank=True, null=True)
    
    class Meta:
        ordering = ['id', 'sub_question_letter']
        verbose_name = "Part B Question"
        verbose_name_plural = "Part B Questions"
    
    def __str__(self):
        if self.is_sub_question and self.sub_question_letter:
            parent_id = self.parent_question.id if self.parent_question else "?"
            return f"Q{parent_id}({self.sub_question_letter}) - Part B"
        return f"Q{self.id} - Part B: {self.question[:60]}..."
    
    def get_full_question_display(self):
        """Get the full question text with image position consideration"""
        text_above, text_below = self.get_split_question_text()
        
        display = ""
        if text_above:
            display += text_above
        if self.question_image:
            display += f"\n[Image: {self.question_image.name}]"
        if text_below:
            display += f"\n{text_below}"
        
        return display.strip()
    
    def clean(self):
        # Add any custom validation for Part B questions
        pass


# -------------------- PART C --------------------
class PartC(models.Model):
    info = models.TextField()
    required_questions = models.IntegerField()
    or_question = models.BooleanField(default=False)
    each_questions_mark = models.IntegerField()
    total = models.IntegerField()
    details = models.OneToOneField(QuestionPaper, on_delete=models.CASCADE, related_name="part_c_details")
    
    def get_main_questions(self):
        """Get only main questions (not sub-questions)"""
        return self.questions.filter(is_sub_question=False)
    
    def __str__(self):
        return f"Part C - {self.details.subject_name}"


class PartCQuestions(BaseQuestion):
    part_c = models.ForeignKey(PartC, on_delete=models.CASCADE, related_name="questions")
    
    answer_text = models.TextField(blank=True, null=True)
    answer_equation = models.TextField(blank=True, null=True)
    answer_image = models.ImageField(upload_to="answers/", blank=True, null=True)
    
    is_or_group = models.BooleanField(default=False)
    or_group_number = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['or_group_number', 'id', 'sub_question_letter']
        verbose_name = "Part C Question"
        verbose_name_plural = "Part C Questions"
    
    def __str__(self):
        if self.is_or_group:
            return f"{self.question[:60]}... (OR Group {self.or_group_number})"
        if self.is_sub_question and self.sub_question_letter:
            parent_id = self.parent_question.id if self.parent_question else "?"
            return f"Q{parent_id}({self.sub_question_letter}) - Part C"
        return f"Q{self.id} - Part C: {self.question[:60]}..."
    
    def get_full_question_display(self):
        """Get the full question text with image position consideration"""
        text_above, text_below = self.get_split_question_text()
        
        display = ""
        if text_above:
            display += text_above
        if self.question_image:
            display += f"\n[Image: {self.question_image.name}]"
        if text_below:
            display += f"\n{text_below}"
        
        return display.strip()
    
    def clean(self):
        # Add any custom validation for Part C questions
        pass