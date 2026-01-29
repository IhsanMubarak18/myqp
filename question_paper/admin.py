from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from .models import (
    PartA, PartAQuestions, QuestionPaper, PartB, PartBQuestions,
    PartC, PartCQuestions, Revision, ExamName, SubjectCode,
    QuestionModule, ModuleOutcome, SectionInstruction, SystemConfiguration
)


# ==================== CUSTOM ADMIN SITE ====================
class CustomAdminSite(admin.AdminSite):
    site_header = "Question Paper Administration"
    site_title = "Question Paper Admin"
    index_title = "Welcome to Question Paper Management System"

    def index(self, request, extra_context=None):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return redirect(reverse("question_paper:admin_dashboard"))
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = CustomAdminSite(name="admin")


# ==================== SYSTEM CONFIGURATION ====================
@admin.register(SystemConfiguration, site=admin_site)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ("default_max_marks",)

    def has_add_permission(self, request):
        if SystemConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)


# ==================== DROPDOWN MODELS ====================
@admin.register(Revision, site=admin_site)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ("year", "is_active")
    list_filter = ("is_active",)
    search_fields = ("year",)
    list_editable = ("is_active",)
    ordering = ("-year",)


@admin.register(ExamName, site=admin_site)
class ExamNameAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("display_order", "is_active")
    ordering = ("display_order", "name")


@admin.register(SubjectCode, site=admin_site)
class SubjectCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "subject_name", "duration_hours", "is_active")
    list_filter = ("is_active", "duration_hours")
    search_fields = ("code", "subject_name")
    list_editable = ("is_active",)
    ordering = ("code",)


@admin.register(QuestionModule, site=admin_site)
class QuestionModuleAdmin(admin.ModelAdmin):
    list_display = ("module_number", "is_active")
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    ordering = ("module_number",)


@admin.register(ModuleOutcome, site=admin_site)
class ModuleOutcomeAdmin(admin.ModelAdmin):
    list_display = ("outcome_code", "description", "is_active")
    list_filter = ("is_active",)
    search_fields = ("outcome_code", "description")
    list_editable = ("is_active",)
    ordering = ("outcome_code",)


@admin.register(SectionInstruction, site=admin_site)
class SectionInstructionAdmin(admin.ModelAdmin):
    list_display = ("text", "part_type", "is_active")
    list_filter = ("part_type", "is_active")
    search_fields = ("text",)
    list_editable = ("is_active",)


# ==================== MAIN MODELS ====================
@admin.register(QuestionPaper, site=admin_site)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ("question_paper_code", "subject_name", "subject_code", "exam_name", "revesion", "maximum_mark")
    list_filter = ("revesion", "time")
    search_fields = ("subject_name", "exam_name", "subject_code", "question_paper_code")
    ordering = ("-id",)


@admin.register(PartA, site=admin_site)
class PartAAdmin(admin.ModelAdmin):
    list_display = ("details", "each_question_mark", "total")
    search_fields = ("details__subject_name",)


@admin.register(PartAQuestions, site=admin_site)
class PartAQuestionsAdmin(admin.ModelAdmin):
    list_display = ("id", "part_a", "module", "level", "question_preview", "is_sub_question")
    list_filter = ("module", "level", "is_sub_question")
    search_fields = ("question", "answer")

    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question

    question_preview.short_description = "Question"


@admin.register(PartB, site=admin_site)
class PartBAdmin(admin.ModelAdmin):
    list_display = ("details", "required_questions", "each_questions_mark", "total")
    search_fields = ("details__subject_name",)


@admin.register(PartBQuestions, site=admin_site)
class PartBQuestionsAdmin(admin.ModelAdmin):
    list_display = ("id", "part_b", "module", "level", "question_preview", "is_sub_question")
    list_filter = ("module", "level", "is_sub_question")
    search_fields = ("question",)

    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question

    question_preview.short_description = "Question"


@admin.register(PartC, site=admin_site)
class PartCAdmin(admin.ModelAdmin):
    list_display = ("details", "required_questions", "each_questions_mark", "or_question", "total")
    search_fields = ("details__subject_name",)
    list_filter = ("or_question",)


@admin.register(PartCQuestions, site=admin_site)
class PartCQuestionsAdmin(admin.ModelAdmin):
    list_display = ("id", "part_c", "module", "level", "question_preview", "is_or_group", "or_group_number")
    list_filter = ("module", "level", "is_or_group")
    search_fields = ("question",)

    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question

    question_preview.short_description = "Question"
