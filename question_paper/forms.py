from django import forms
from django.core.exceptions import ValidationError

from .models import (
    QuestionPaper,
    PartAQuestions,
    PartBQuestions,
    PartCQuestions,
    Revision,
    ExamName,
    SubjectCode,
    QuestionModule,
    ModuleOutcome,
    SectionInstruction,
    SystemConfiguration,
)


# ============================================================
# QUESTION PAPER FORM
# ============================================================
class QuestionPaperForm(forms.ModelForm):
    # Custom exam name input (shown only when OTHER is selected)
    custom_exam_name = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter custom exam name",
            "id": "custom_exam_name_field"
        }),
        label="Custom Exam Name"
    )

    class Meta:
        model = QuestionPaper
        fields = [
            "question_paper_code",
            "revesion",
            "subject_code",
            "exam_name",
            "subject_name",
            "time",
            "exam_marks",
            "module1_hours",
            "module2_hours",
            "module3_hours",
            "module4_hours",
            "percent_R",
            "percent_U",
            "percent_A",
        ]
        widgets = {
            "question_paper_code": forms.NumberInput(attrs={"class": "form-control"}),
            "subject_name": forms.TextInput(attrs={"class": "form-control", "id": "subject_name_field"}),
            "time": forms.NumberInput(attrs={"class": "form-control", "min": 1, "id": "time_field"}),
            "exam_marks": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "module1_hours": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "module2_hours": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "module3_hours": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "module4_hours": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "percent_R": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": 0}),
            "percent_U": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": 0}),
            "percent_A": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---------------- Revision Dropdown ----------------
        revision_choices = [("", "--- Select Revision ---")]
        active_revisions = Revision.objects.filter(is_active=True).order_by("-year")
        revision_choices.extend([(r.year, r.year) for r in active_revisions])

        self.fields["revesion"] = forms.ChoiceField(
            choices=revision_choices,
            widget=forms.Select(attrs={"class": "form-select"}),
            label="Revision",
            required=True
        )

        # ---------------- Exam Name Dropdown ----------------
        exam_name_choices = [("", "--- Select Exam Name ---")]
        active_exam_names = ExamName.objects.filter(is_active=True).order_by("display_order", "name")
        exam_name_choices.extend([(e.name, e.name) for e in active_exam_names])
        exam_name_choices.append(("OTHER", "Other (Custom)"))

        self.fields["exam_name"] = forms.ChoiceField(
            choices=exam_name_choices,
            widget=forms.Select(attrs={
                "class": "form-select",
                "id": "exam_name_dropdown",
                "onchange": "toggleCustomExamName()"
            }),
            label="Exam Name",
            required=True
        )

        # ---------------- Subject Code Dropdown ----------------
        subject_code_choices = [("", "--- Select Subject Code ---")]
        active_subjects = SubjectCode.objects.filter(is_active=True).order_by("code")
        subject_code_choices.extend([(s.code, f"{s.code} - {s.subject_name}") for s in active_subjects])

        self.fields["subject_code"] = forms.ChoiceField(
            choices=subject_code_choices,
            widget=forms.Select(attrs={
                "class": "form-select",
                "id": "subject_code_dropdown",
                "onchange": "handleSubjectCodeChange()"
            }),
            label="Subject Code",
            required=True
        )

        # ---------------- If Editing: Set custom exam name ----------------
        if self.instance and self.instance.pk:
            predefined_names = [name for name, _ in exam_name_choices if name not in ["", "OTHER"]]
            if self.instance.exam_name and self.instance.exam_name not in predefined_names:
                self.fields["exam_name"].initial = "OTHER"
                self.fields["custom_exam_name"].initial = self.instance.exam_name

        # ---------------- Default Exam Marks from SystemConfiguration ----------------
        if not self.instance.pk:
            try:
                config = SystemConfiguration.objects.first()
                if config:
                    self.fields["exam_marks"].initial = config.default_max_marks
            except Exception:
                pass

    def clean(self):
        cleaned = super().clean()

        # Validate percentages
        r = cleaned.get("percent_R") or 0
        u = cleaned.get("percent_U") or 0
        a = cleaned.get("percent_A") or 0

        if (r + u + a) and abs((r + u + a) - 100) > 0.5:
            raise ValidationError("Sum of R + U + A should be around 100%.")

        # Handle custom exam name
        exam_name = cleaned.get("exam_name")
        custom_exam_name = cleaned.get("custom_exam_name")

        if exam_name == "OTHER":
            if not custom_exam_name:
                raise ValidationError("Please enter a custom exam name.")
            cleaned["exam_name"] = custom_exam_name

        # Convert subject_code to int if possible (matches your QuestionPaper model IntegerField)
        subject_code = cleaned.get("subject_code")
        if subject_code:
            try:
                cleaned["subject_code"] = int(subject_code)
            except (ValueError, TypeError):
                pass

        return cleaned


# ============================================================
# BASE QUESTION FORM
# ============================================================
class BaseQuestionForm(forms.ModelForm):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        question_paper_id = kwargs.pop("question_paper_id", None)
        part_type = kwargs.pop("part_type", None)
        super().__init__(*args, **kwargs)

        # CSS classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
                field.widget.attrs["class"] = "form-control"
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["rows"] = 2
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"

        # Question textbox settings
        if "question" in self.fields:
            self.fields["question"].widget.attrs["rows"] = 3
            self.fields["question"].widget.attrs["placeholder"] = "Enter text that will appear above the image"

        # Image position choices
        if "question_image_position" in self.fields:
            self.fields["question_image_position"].choices = [
                ("top", "Top - Text above image"),
                ("bottom", "Bottom - Text below image"),
                ("middle", "Middle - Text above and below image"),
            ]
            self.fields["question_image_position"].help_text = "Select image position relative to text"

        # Parent question queryset filtering
        if "parent_question" in self.fields and question_paper_id and part_type:
            if part_type == "A":
                ModelClass = PartAQuestions
                related_field = "part_a__details_id"
            elif part_type == "B":
                ModelClass = PartBQuestions
                related_field = "part_b__details_id"
            elif part_type == "C":
                ModelClass = PartCQuestions
                related_field = "part_c__details_id"
            else:
                ModelClass = None
                related_field = None

            if ModelClass and related_field:
                self.fields["parent_question"].queryset = ModelClass.objects.filter(
                    **{related_field: question_paper_id},
                    is_sub_question=False
                ).order_by("id")

        # Required fields
        required_fields = ["module", "module_outcome", "level", "question"]
        for field in required_fields:
            if field in self.fields:
                self.fields[field].required = True
                self.fields[field].widget.attrs["required"] = "required"

        # Initialize existing instance data
        if self.instance and self.instance.pk:
            if self.instance.question_image_position == "middle" and self.instance.text_below_image:
                self.fields["text_below_image"].initial = self.instance.text_below_image
            else:
                # Backward compatibility: old data stored with newline split
                if self.instance.question:
                    lines = self.instance.question.split("\n")
                    if len(lines) >= 2:
                        self.fields["question"].initial = lines[0]
                        self.fields["text_below_image"].initial = "\n".join(lines[1:])

        # Dynamic dropdowns from DB
        # Module choices
        if "module" in self.fields:
            module_choices = [("", "--- Select Module ---")]
            try:
                active_modules = QuestionModule.objects.filter(is_active=True).order_by("module_number")
                module_choices.extend([(m.module_number, f"Module {m.module_number}") for m in active_modules])
            except Exception:
                pass

            self.fields["module"] = forms.ChoiceField(
                choices=module_choices,
                widget=forms.Select(attrs={"class": "form-select"}),
                required=True
            )

        # Module outcome choices
        if "module_outcome" in self.fields:
            outcome_choices = [("", "--- Select Outcome ---")]
            try:
                active_outcomes = ModuleOutcome.objects.filter(is_active=True).order_by("outcome_code")
                outcome_choices.extend([
                    (o.outcome_code, f"{o.outcome_code} - {o.description or ''}")
                    for o in active_outcomes
                ])
            except Exception:
                pass

            self.fields["module_outcome"] = forms.ChoiceField(
                choices=outcome_choices,
                widget=forms.Select(attrs={"class": "form-select"}),
                required=True
            )


# ============================================================
# PART A QUESTION FORM
# ============================================================
class PartAQuestionsForms(BaseQuestionForm):
    class Meta:
        model = PartAQuestions
        fields = [
            "module", "module_outcome", "level", "question",
            "text_below_image",
            "question_image", "question_image_position", "question_image_size",
            "is_sub_question", "parent_question", "sub_question_letter",
            "answer", "answer_equation", "answer_image",
        ]
        widgets = {
            "question": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Enter text that will appear above the image"
            }),
            "text_below_image": forms.Textarea(attrs={
                "rows": 2,
                "class": "form-control text-below-image-field",
                "placeholder": "Enter text that will appear below the image (only for middle position)"
            }),
            "answer": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "answer_equation": forms.Textarea(attrs={
                "rows": 2,
                "class": "form-control",
                "placeholder": "Enter LaTeX equation (e.g. E=mc^2)"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["question_image_position"].initial = "top"
        self.fields["question_image_size"].initial = "medium"

        self.fields["answer"].required = True
        self.fields["answer"].widget.attrs["required"] = "required"

        self.fields["is_sub_question"].widget.attrs["onclick"] = "toggleSubQuestionFields(this)"

        if not getattr(self.instance, "is_sub_question", False):
            self.fields["parent_question"].widget = forms.HiddenInput()
            self.fields["sub_question_letter"].widget = forms.HiddenInput()


# ============================================================
# PART B QUESTION FORM
# ============================================================
class PartBQuestionsForms(BaseQuestionForm):
    class Meta:
        model = PartBQuestions
        fields = [
            "module", "module_outcome", "level", "question",
            "text_below_image",
            "question_image", "question_image_position", "question_image_size",
            "is_sub_question", "parent_question", "sub_question_letter",
            "answer_text", "answer_equation", "answer_image",
        ]
        widgets = {
            "question": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Enter text that will appear above the image"
            }),
            "text_below_image": forms.Textarea(attrs={
                "rows": 2,
                "class": "form-control text-below-image-field",
                "placeholder": "Enter text that will appear below the image (only for middle position)"
            }),
            "answer_text": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "answer_equation": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["question_image_position"].initial = "top"
        self.fields["question_image_size"].initial = "medium"

        self.fields["answer_text"].required = True
        self.fields["answer_text"].widget.attrs["required"] = "required"

        self.fields["answer_equation"].help_text = "Enter LaTeX equation if needed"

        self.fields["is_sub_question"].widget.attrs["onclick"] = "toggleSubQuestionFields(this)"

        if not getattr(self.instance, "is_sub_question", False):
            self.fields["parent_question"].widget = forms.HiddenInput()
            self.fields["sub_question_letter"].widget = forms.HiddenInput()


# ============================================================
# PART C QUESTION FORM
# ============================================================
class PartCQuestionsForms(BaseQuestionForm):
    class Meta:
        model = PartCQuestions
        fields = [
            "module", "module_outcome", "level", "question",
            "text_below_image",
            "question_image", "question_image_position", "question_image_size",
            "is_sub_question", "parent_question", "sub_question_letter",
            "answer_text", "answer_equation", "answer_image",
        ]
        widgets = {
            "question": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Enter text that will appear above the image"
            }),
            "text_below_image": forms.Textarea(attrs={
                "rows": 2,
                "class": "form-control text-below-image-field",
                "placeholder": "Enter text that will appear below the image (only for middle position)"
            }),
            "answer_text": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "answer_equation": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["question_image_position"].initial = "top"
        self.fields["question_image_size"].initial = "medium"

        self.fields["answer_text"].required = True
        self.fields["answer_text"].widget.attrs["required"] = "required"

        self.fields["answer_equation"].help_text = "Enter LaTeX equation if needed"

        self.fields["is_sub_question"].widget.attrs["onclick"] = "toggleSubQuestionFields(this)"

        if not getattr(self.instance, "is_sub_question", False):
            self.fields["parent_question"].widget = forms.HiddenInput()
            self.fields["sub_question_letter"].widget = forms.HiddenInput()


# ============================================================
# MANAGEMENT FORMS
# ============================================================
class RevisionForm(forms.ModelForm):
    class Meta:
        model = Revision
        fields = ["year", "is_active"]


class ExamNameForm(forms.ModelForm):
    class Meta:
        model = ExamName
        fields = ["name", "is_active", "display_order"]


class SubjectCodeForm(forms.ModelForm):
    class Meta:
        model = SubjectCode
        fields = ["code", "subject_name", "duration_hours", "is_active"]


class QuestionModuleForm(forms.ModelForm):
    class Meta:
        model = QuestionModule
        fields = ["module_number", "is_active"]


class ModuleOutcomeForm(forms.ModelForm):
    class Meta:
        model = ModuleOutcome
        fields = ["outcome_code", "description", "is_active"]


class SectionInstructionForm(forms.ModelForm):
    class Meta:
        model = SectionInstruction
        fields = ["text", "part_type", "is_active"]
