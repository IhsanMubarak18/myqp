from django.urls import path
from .views import (
    HeadingPage,
    CreatePartA,
    CreatePartB,
    CreatePartC,
    ReviewPage,
    EditHeading,
    EditPartA,
    EditPartB,
    EditPartC,
    DownloadPage,
    QuestionPaperPDF,
    AnswerSheetPDF,
    BlueprintPDF,
    download_answer_sheet,
    download_blueprint,
    download_question_paper,
    get_parent_questions,
    get_subject_details,
    AdminDashboardView,
    ResumeQPView,
    ResumeListPage,
    DeleteQPView,

    # Management Views
    RevisionListView,
    RevisionCreateView,
    RevisionUpdateView,
    RevisionDeleteView,
    ExamNameListView,
    ExamNameCreateView,
    ExamNameUpdateView,
    ExamNameDeleteView,
    SubjectCodeListView,
    SubjectCodeCreateView,
    SubjectCodeUpdateView,
    SubjectCodeDeleteView,
    ModuleListView,
    ModuleCreateView,
    ModuleUpdateView,
    ModuleDeleteView,
    OutcomeListView,
    OutcomeCreateView,
    OutcomeUpdateView,
    OutcomeDeleteView,
    InstructionListView,
    InstructionCreateView,
    InstructionUpdateView,
    InstructionDeleteView,
    loading_view,
)

app_name = "question_paper"

urlpatterns = [
    path('', loading_view, name='loading'),
    # Admin Dashboard
    path("admin-dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("resume/<int:pk>/", ResumeQPView.as_view(), name="resume"),
    path("resume-list/", ResumeListPage.as_view(), name="resume_list"),
    path("delete-qp/<int:pk>/", DeleteQPView.as_view(), name="delete_qp"),

    # Management URLs - Revisions
    path("manage/revisions/", RevisionListView.as_view(), name="revision_list"),
    path("manage/revisions/add/", RevisionCreateView.as_view(), name="revision_add"),
    path("manage/revisions/<int:pk>/edit/", RevisionUpdateView.as_view(), name="revision_edit"),
    path("manage/revisions/<int:pk>/delete/", RevisionDeleteView.as_view(), name="revision_delete"),

    # Management URLs - Exam Names
    path("manage/exam-names/", ExamNameListView.as_view(), name="exam_name_list"),
    path("manage/exam-names/add/", ExamNameCreateView.as_view(), name="exam_name_add"),
    path("manage/exam-names/<int:pk>/edit/", ExamNameUpdateView.as_view(), name="exam_name_edit"),
    path("manage/exam-names/<int:pk>/delete/", ExamNameDeleteView.as_view(), name="exam_name_delete"),

    # Management URLs - Subject Codes
    path("manage/subject-codes/", SubjectCodeListView.as_view(), name="subject_code_list"),
    path("manage/subject-codes/add/", SubjectCodeCreateView.as_view(), name="subject_code_add"),
    path("manage/subject-codes/<int:pk>/edit/", SubjectCodeUpdateView.as_view(), name="subject_code_edit"),
    path("manage/subject-codes/<int:pk>/delete/", SubjectCodeDeleteView.as_view(), name="subject_code_delete"),

    # Management URLs - Modules
    path("manage/modules/", ModuleListView.as_view(), name="module_list"),
    path("manage/modules/add/", ModuleCreateView.as_view(), name="module_add"),
    path("manage/modules/<int:pk>/edit/", ModuleUpdateView.as_view(), name="module_edit"),
    path("manage/modules/<int:pk>/delete/", ModuleDeleteView.as_view(), name="module_delete"),

    # Management URLs - Outcomes
    path("manage/outcomes/", OutcomeListView.as_view(), name="outcome_list"),
    path("manage/outcomes/add/", OutcomeCreateView.as_view(), name="outcome_add"),
    path("manage/outcomes/<int:pk>/edit/", OutcomeUpdateView.as_view(), name="outcome_edit"),
    path("manage/outcomes/<int:pk>/delete/", OutcomeDeleteView.as_view(), name="outcome_delete"),

    # Management URLs - Instructions
    path("manage/instructions/", InstructionListView.as_view(), name="instruction_list"),
    path("manage/instructions/add/", InstructionCreateView.as_view(), name="instruction_add"),
    path("manage/instructions/<int:pk>/edit/", InstructionUpdateView.as_view(), name="instruction_edit"),
    path("manage/instructions/<int:pk>/delete/", InstructionDeleteView.as_view(), name="instruction_delete"),

    # Main flow
    path("heading/", HeadingPage.as_view(), name="heading"),
    path("part-a/", CreatePartA.as_view(), name="PartA"),
    path("part-b/", CreatePartB.as_view(), name="PartB"),
    path("part-c/", CreatePartC.as_view(), name="PartC"),

    path("<int:pk>/review/", ReviewPage.as_view(), name="review"),

    # ✅ FIXED NAME HERE
    path("<int:pk>/edit-heading/", EditHeading.as_view(), name="edit_heading"),

    path("<int:pk>/edit-part-a/", EditPartA.as_view(), name="edit_part_a"),
    path("<int:pk>/edit-part-b/", EditPartB.as_view(), name="edit_part_b"),
    path("<int:pk>/edit-part-c/", EditPartC.as_view(), name="edit_part_c"),

    path("<int:pk>/downloads/", DownloadPage.as_view(), name="downloads"),

    # PDF
    path("<int:pk>/question-pdf/", QuestionPaperPDF.as_view(), name="question_pdf"),
    path("<int:pk>/answer-pdf/", AnswerSheetPDF.as_view(), name="answer_pdf"),
    path("<int:pk>/blueprint-pdf/", BlueprintPDF.as_view(), name="blueprint_pdf"),

    # APIs
    path("api/get-parent-questions/<str:part_type>/<int:question_paper_id>/",
         get_parent_questions, name="get_parent_questions"),
    path("api/get-subject-details/", get_subject_details, name="get_subject_details"),
    path(
        "download/question-paper/<int:pk>/",
        download_question_paper,
        name="download_question_paper"
    ),
    path(
        "download/answer-sheet/<int:pk>/",
        download_answer_sheet,
        name="download_answer_sheet",
    ),
    path(
        "download/blueprint/<int:pk>/",
        download_blueprint,
        name="download_blueprint",
    ),
]
