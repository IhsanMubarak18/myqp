from django.utils import timezone
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from reportlab.platypus import Image as RLImage 
from django.views.generic import View
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from PIL import Image, ImageOps
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import json



from .forms import (
    QuestionPaperForm,
    PartAQuestionsForms,
    PartBQuestionsForms,
    PartCQuestionsForms,
)
from .models import (
    PartA,
    PartAQuestions,
    QuestionPaper,
    PartB,
    PartBQuestions,
    PartCQuestions,
    PartC,
    Revision, ExamName, SubjectCode,
    SectionInstruction
)
from .utils import render_to_pdf

# ReportLab imports for clean Answer Sheet PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image as RLImage,
    KeepTogether,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------------------------------------------------
# HELPER FUNCTIONS - UPDATED FOR NEW TEXT_BELOW_IMAGE FIELD
# ---------------------------------------------------------------------
def split_text_for_image(question):
    """
    Get text above and below image based on question fields.
    Uses the new text_below_image field for middle position.
    """
    if question.question_image_position == 'middle':
        # For middle position:
        # - question field contains text above image
        # - text_below_image field contains text below image
        text_above = question.question or ""
        text_below = question.text_below_image or ""
        return text_above, text_below
    
    elif question.question_image_position == 'top':
        # For top position: all text above image
        return question.question or "", ""
    
    elif question.question_image_position == 'bottom':
        # For bottom position: all text below image
        return "", question.question or ""
    
    else:  # Default (top)
        return question.question or "", ""


def get_question_display_html(question):
    """Generate HTML for question display with image positioning"""
    if not hasattr(question, 'question_image'):
        return question.question
    
    if not question.question_image:
        return question.question
    
    # Get image size class
    size_class = f"img-{question.question_image_size}" if question.question_image_size else "img-medium"
    
    # Get text based on position
    text_above, text_below = split_text_for_image(question)
    
    html = ""
    
    if text_above:
        html += f'<div class="question-text-above">{text_above}</div>'
    
    html += f'''
    <div class="question-image-container">
        <img src="{question.question_image.url}" 
             alt="Question Image" 
             class="question-img {size_class}">
    </div>
    '''
    
    if text_below:
        html += f'<div class="question-text-below">{text_below}</div>'
    
    return html


@require_GET
def get_parent_questions(request, part_type, question_paper_id):
    """API endpoint to get parent questions for sub-questions"""
    try:
        qp = QuestionPaper.objects.get(id=question_paper_id)
        
        if part_type == 'A':
            questions = PartAQuestions.objects.filter(
                part_a__details=qp,
                is_sub_question=False
            ).order_by('id')
        elif part_type == 'B':
            questions = PartBQuestions.objects.filter(
                part_b__details=qp,
                is_sub_question=False
            ).order_by('id')
        elif part_type == 'C':
            questions = PartCQuestions.objects.filter(
                part_c__details=qp,
                is_sub_question=False
            ).order_by('id')
        else:
            return JsonResponse([], safe=False)
        
        data = []
        for i, q in enumerate(questions, 1):
            data.append({
                'id': q.id,
                'text': q.question[:100] + ('...' if len(q.question) > 100 else ''),
                'display_number': i
            })
        
        return JsonResponse(data, safe=False)
    
    except QuestionPaper.DoesNotExist:
        return JsonResponse([], safe=False)


@require_GET
def get_subject_details(request):
    """API endpoint to get subject details by code"""
    from .models import SubjectCode
    
    subject_code = request.GET.get('code', '')
    
    try:
        subject = SubjectCode.objects.get(code=subject_code, is_active=True)
        return JsonResponse({
            'success': True,
            'subject_name': subject.subject_name,
            'duration_hours': subject.duration_hours
        })
    except SubjectCode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Subject code not found'
        }, status=404)


# ---------------------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------------------
class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Custom admin dashboard for managing dropdown content"""
    
    login_url = '/admin/login/'
    
    def test_func(self):
        """Only allow superusers/staff to access"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get(self, request, *args, **kwargs):
        from .models import (
            Revision, ExamName, SubjectCode, 
            QuestionModule, ModuleOutcome, SectionInstruction
        )
        
        # Get statistics
        context = {
            'total_revisions': Revision.objects.filter(is_active=True).count(),
            'total_exam_names': ExamName.objects.filter(is_active=True).count(),
            'total_subject_codes': SubjectCode.objects.filter(is_active=True).count(),
            'total_modules': QuestionModule.objects.filter(is_active=True).count(),
            'total_outcomes': ModuleOutcome.objects.filter(is_active=True).count(),
            'total_instructions': SectionInstruction.objects.filter(is_active=True).count(),
            'total_question_papers': QuestionPaper.objects.count(),
            
            # Get recent data
            'recent_revisions': Revision.objects.filter(is_active=True).order_by('-year')[:5],
            'recent_exam_names': ExamName.objects.filter(is_active=True).order_by('display_order')[:5],
            'recent_subject_codes': SubjectCode.objects.filter(is_active=True).order_by('code')[:10],
            'recent_modules': QuestionModule.objects.filter(is_active=True).order_by('module_number')[:5],
            'recent_outcomes': ModuleOutcome.objects.filter(is_active=True).order_by('outcome_code')[:5],
            'recent_instructions': SectionInstruction.objects.filter(is_active=True).order_by('-id')[:5],
            'recent_question_papers': QuestionPaper.objects.order_by('-id')[:5],
            
            # User info
            'admin_user': request.user,

        }
        
        return render(request, 'admin_dashboard.html', context)


# ---------------------------------------------------------------------
# HEADING / PART A / PART B / PART C (CREATE)
# ---------------------------------------------------------------------

class HeadingPage(View):
    def get(self, request, *args, **kwargs):
        form = QuestionPaperForm()
        return render(request, "heading.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = QuestionPaperForm(request.POST)
        if form.is_valid():
            qp = form.save()
            request.session["question_paper_id"] = qp.id
            return redirect("question_paper:PartA")
        return render(request, "heading.html", {"form": form})


class CreatePartA(View):
    def get(self, request, *args, **kwargs):
        qp_id = request.session.get("question_paper_id")
        if not qp_id:
            return redirect("question_paper:heading")
        qp = get_object_or_404(QuestionPaper, id=qp_id)

        return render(
            request,
            "create_part_a.html",
            {
                "step": 0,
                "question_paper": qp,
                "part_type": "A"
            },
        )

    def post(self, request, *args, **kwargs):
        qp_id = request.session.get("question_paper_id")
        if not qp_id:
            return redirect("question_paper:heading")
        qp = get_object_or_404(QuestionPaper, id=qp_id)

        # ================= STEP 1 =================
        if request.POST.get("step") == "1":
            num_questions = int(request.POST.get("num_questions"))
            each_mark = float(request.POST.get("each_question_mark"))
            if each_mark.is_integer():
                each_mark = int(each_mark)

            request.session["num_questions_a"] = num_questions
            request.session["each_mark_a"] = each_mark
            
            total_marks = num_questions * each_mark

            PartAFormset = modelformset_factory(
                PartAQuestions,
                form=PartAQuestionsForms,
                extra=num_questions,
            )

            formset = PartAFormset(
                queryset=PartAQuestions.objects.none(),
                form_kwargs={'question_paper_id': qp_id, 'part_type': 'A'}
            )

            return render(
                request,
                "create_part_a.html",
                {
                    "step": 1,
                    "formset": formset,
                    "question_paper": qp,
                    "num_questions": num_questions,
                    "each_question_mark": each_mark,
                    "total_marks": total_marks,
                    "part_type": "A",
                    "instructions": SectionInstruction.objects.filter(part_type='A', is_active=True),
                },
            )

        # ================= STEP 2 =================
        # ================= STEP 2 =================
        num_questions = int(request.session.get("num_questions_a"))
        each_mark = float(request.session.get("each_mark_a"))
        if each_mark.is_integer():
            each_mark = int(each_mark)
        total_marks = num_questions * each_mark

        PartAFormset = modelformset_factory(
            PartAQuestions,
            form=PartAQuestionsForms,
            extra=0,
        )

        formset = PartAFormset(
            request.POST,
            request.FILES,
            queryset=PartAQuestions.objects.none(),
            form_kwargs={'question_paper_id': qp_id, 'part_type': 'A'}
        )

        # Validate Section Instructions
        info = request.POST.get("info", "").strip()
        if not info:
             return render(
                request,
                "create_part_a.html",
                {
                    "step": 1,
                    "formset": formset,
                    "question_paper": qp,
                    "part_type": "A",
                    "error_message": "⚠️ Section Information/Instructions are required.",
                     "instructions": SectionInstruction.objects.filter(part_type='A', is_active=True),
                },
            )


        if formset.is_valid():
            # Create or update PartA
            part_a, created = PartA.objects.get_or_create(
                details=qp,
                defaults={
                    "info": request.POST.get("info"),
                    "each_question_mark": each_mark,
                    "total": total_marks,
                },
            )

            if not created:
                old_total = part_a.total or 0
                part_a.info = request.POST.get("info")
                part_a.each_question_mark = each_mark
                part_a.total = total_marks
                part_a.save()
                # Remove old questions
                part_a.questions.all().delete()
                qp.maximum_mark = (qp.maximum_mark or 0) - old_total + total_marks
            else:
                qp.maximum_mark = (qp.maximum_mark or 0) + total_marks

            qp.save()

            # Save all questions with their sub-question relationships
            saved_questions = []
            for form in formset:
                if form.cleaned_data:
                    q = form.save(commit=False)
                    q.part_a = part_a
                    
                    # Handle sub-question logic
                    if q.is_sub_question and q.parent_question:
                        # Ensure parent question is in the same PartA
                        if q.parent_question.part_a != part_a:
                            # Find or create parent in current part_a
                            parent_q = PartAQuestions.objects.filter(
                                part_a=part_a,
                                question=q.parent_question.question
                            ).first()
                            if not parent_q:
                                parent_q = PartAQuestions.objects.create(
                                    part_a=part_a,
                                    module=q.parent_question.module,
                                    level=q.parent_question.level,
                                    question=q.parent_question.question,
                                    text_below_image=q.parent_question.text_below_image,
                                    answer=q.parent_question.answer,
                                    question_image=q.parent_question.question_image,
                                    question_image_position=q.parent_question.question_image_position,
                                    question_image_size=q.parent_question.question_image_size,
                                    is_sub_question=False
                                )
                            q.parent_question = parent_q
                    
                    q.save()
                    saved_questions.append(q)
            
            # Handle orphaned sub-questions (those with parent_question but is_sub_question not checked)
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('is_sub_question'):
                    q = form.save(commit=False)
                    if hasattr(q, 'sub_questions'):
                        for sub in q.sub_questions.all():
                            sub.parent_question = None
                            sub.is_sub_question = False
                            sub.save()

            return redirect("question_paper:PartB")

        # If formset is invalid
        return render(
            request,
            "create_part_a.html",
            {
                "step": 1,
                "formset": formset,
                "question_paper": qp,
                "part_type": "A",
                "error_message": "⚠️ Please fill all required fields correctly."
            },
        )


class CreatePartB(View):
    def get(self, request, *args, **kwargs):
        qp_id = request.session.get("question_paper_id")
        if not qp_id:
            return redirect("question_paper:heading")
        qp = get_object_or_404(QuestionPaper, id=qp_id)

        return render(
            request,
            "create_part_b.html",
            {
                "step": 0,
                "question_paper": qp,
                "part_type": "B"
            },
        )

    def post(self, request, *args, **kwargs):
        qp_id = request.session.get("question_paper_id")
        if not qp_id:
            return redirect("question_paper:heading")
        qp = get_object_or_404(QuestionPaper, id=qp_id)

        # ================= STEP 1 =================
        if request.POST.get("step") == "1":
            try:
                num_questions = int(request.POST.get("num_questions"))
                required_questions = int(request.POST.get("required_questions"))
                each_questions_mark = int(request.POST.get("each_questions_mark"))

                if required_questions > num_questions:
                    return render(
                        request,
                        "create_part_b.html",
                        {
                            "step": 0,
                            "question_paper": qp,
                            "error_message": "⚠️ Required questions cannot be greater than total questions",
                            "part_type": "B"
                        },
                    )

            except ValueError:
                return render(
                    request,
                    "create_part_b.html",
                    {
                        "step": 0,
                        "question_paper": qp,
                        "error_message": "⚠️ Invalid number entered",
                        "part_type": "B"
                    },
                )

            # Save for step 2
            request.session["num_questions_b"] = num_questions
            request.session["required_questions_b"] = required_questions
            request.session["each_mark_b"] = each_questions_mark

            PartBQuestionsFormSet = modelformset_factory(
                PartBQuestions,
                form=PartBQuestionsForms,
                extra=num_questions,
            )

            formset = PartBQuestionsFormSet(
                queryset=PartBQuestions.objects.none(),
                form_kwargs={'question_paper_id': qp_id, 'part_type': 'B'}
            )

            return render(
                request,
                "create_part_b.html",
                {
                    "step": 1,
                    "formset": formset,
                    "question_paper": qp,
                    "required_questions": required_questions,
                    "each_questions_mark": each_questions_mark,
                    "each_questions_mark": each_questions_mark,
                    "part_type": "B",
                    "instructions": SectionInstruction.objects.filter(part_type='B', is_active=True),
                },

            )

        # ================= STEP 2 =================
        PartBQuestionsFormSet = modelformset_factory(
            PartBQuestions,
            form=PartBQuestionsForms,
            extra=0,
            validate_min=True,
        )

        formset = PartBQuestionsFormSet(
            request.POST,
            request.FILES,
            queryset=PartBQuestions.objects.none(),
            form_kwargs={'question_paper_id': qp_id, 'part_type': 'B'}
        )
        
        # Validate Section Instructions
        info = request.POST.get("info", "").strip()
        if not info:
             return render(
                request,
                "create_part_b.html",
                {
                    "step": 1,
                    "formset": formset,
                    "question_paper": qp,
                    "required_questions": int(request.POST.get("required_questions", 0)),
                    "each_questions_mark": int(request.POST.get("each_questions_mark", 0)),
                    "part_type": "B",
                    "error_message": "⚠️ Section Information/Instructions are required.",
                    "instructions": SectionInstruction.objects.filter(part_type='B', is_active=True),
                },
            )


        if formset.is_valid():
            required_questions = int(request.POST.get("required_questions"))
            each_questions_mark = int(request.POST.get("each_questions_mark"))
            total = required_questions * each_questions_mark

            # Create or update PartB
            part_b, created = PartB.objects.get_or_create(
                details=qp,
                defaults={
                    "info": request.POST.get("info"),
                    "required_questions": required_questions,
                    "each_questions_mark": each_questions_mark,
                    "total": total,
                },
            )

            if created:
                qp.maximum_mark = (qp.maximum_mark or 0) + total
            else:
                old_total = part_b.total or 0
                part_b.info = request.POST.get("info")
                part_b.required_questions = required_questions
                part_b.each_questions_mark = each_questions_mark
                part_b.total = total
                part_b.save()
                # Remove old questions
                part_b.questions.all().delete()
                qp.maximum_mark = (qp.maximum_mark or 0) - old_total + total

            qp.save()

            # Save all questions
            for form in formset:
                if form.cleaned_data:
                    question = form.save(commit=False)
                    question.part_b = part_b
                    
                    # Handle sub-question logic
                    if question.is_sub_question and question.parent_question:
                        # Ensure parent question is in the same PartB
                        if question.parent_question.part_b != part_b:
                            # Find or create parent in current part_b
                            parent_q = PartBQuestions.objects.filter(
                                part_b=part_b,
                                question=question.parent_question.question
                            ).first()
                            if not parent_q:
                                parent_q = PartBQuestions.objects.create(
                                    part_b=part_b,
                                    module=question.parent_question.module,
                                    level=question.parent_question.level,
                                    question=question.parent_question.question,
                                    text_below_image=question.parent_question.text_below_image,
                                    answer_text=question.parent_question.answer_text,
                                    answer_equation=question.parent_question.answer_equation,
                                    answer_image=question.parent_question.answer_image,
                                    question_image=question.parent_question.question_image,
                                    question_image_position=question.parent_question.question_image_position,
                                    question_image_size=question.parent_question.question_image_size,
                                    is_sub_question=False
                                )
                            question.parent_question = parent_q
                    
                    question.save()

            return redirect("question_paper:PartC")

        # If formset invalid
        return render(
            request,
            "create_part_b.html",
            {
                "step": 1,
                "formset": formset,
                "question_paper": qp,
                "info": request.POST.get("info"),
                "required_questions": request.POST.get("required_questions"),
                "each_questions_mark": request.POST.get("each_questions_mark"),
                "part_type": "B",
                "error_message": "⚠️ Please fill all required fields correctly."
            },
        )


class CreatePartC(View):
    def get(self, request, *args, **kwargs):
        qp_id = request.session.get("question_paper_id")
        if not qp_id:
            return redirect("question_paper:heading")
        qp = get_object_or_404(QuestionPaper, id=qp_id)

        return render(
            request,
            "create_part_c.html",
            {
                "step": 0,
                "question_paper": qp,
                "part_type": "C"
            },
        )

    def post(self, request, *args, **kwargs):
        qp_id = request.session.get("question_paper_id")
        if not qp_id:
            return redirect("question_paper:heading")
        qp = get_object_or_404(QuestionPaper, id=qp_id)

        # ---------- STEP 1 : ask counts ----------
        if request.POST.get("step") == "1":
            try:
                num_questions = int(request.POST.get("num_questions"))
                required_questions = int(request.POST.get("required_questions"))
                each_questions_mark = int(request.POST.get("each_questions_mark"))

                # OR → must be even
                if num_questions % 2 != 0:
                    return render(
                        request,
                        "create_part_c.html",
                        {
                            "step": 0,
                            "question_paper": qp,
                            "error_message": "⚠️ For OR type, Number of Questions must be EVEN (2, 4, 6 ...).",
                            "part_type": "C"
                        },
                    )

                if required_questions > num_questions:
                    return render(
                        request,
                        "create_part_c.html",
                        {
                            "step": 0,
                            "question_paper": qp,
                            "error_message": "⚠️ Required questions cannot be greater than total number of questions",
                            "part_type": "C"
                        },
                    )
            except ValueError:
                return render(
                    request,
                    "create_part_c.html",
                    {
                        "step": 0,
                        "question_paper": qp,
                        "error_message": "⚠️ Invalid number entered",
                        "part_type": "C"
                    },
                )

            # Save these in session for step 2
            request.session["num_questions_c"] = num_questions
            request.session["required_questions_c"] = required_questions
            request.session["each_mark_c"] = each_questions_mark

            PartCQuestionsFormset = modelformset_factory(
                PartCQuestions,
                form=PartCQuestionsForms,
                extra=num_questions
            )
            formset = PartCQuestionsFormset(
                queryset=PartCQuestions.objects.none(),
                form_kwargs={'question_paper_id': qp_id, 'part_type': 'C'}
            )

            return render(
                request,
                "create_part_c.html",
                {
                    "step": 1,
                    "formset": formset,
                    "question_paper": qp,
                    "required_questions": required_questions,
                    "each_questions_mark": each_questions_mark,
                    "or_question": True,
                    "part_type": "C",
                    "instructions": SectionInstruction.objects.filter(part_type='C', is_active=True),
                },

            )

        # ---------- STEP 2 : save questions ----------
        PartCQuestionsFormset = modelformset_factory(
            PartCQuestions,
            form=PartCQuestionsForms,
            extra=0,
            validate_min=True
        )
        formset = PartCQuestionsFormset(
            request.POST,
            request.FILES,
            queryset=PartCQuestions.objects.none(),
            form_kwargs={'question_paper_id': qp_id, 'part_type': 'C'}
        )
        
        # Validate Section Instructions
        info = request.POST.get("info", "").strip()
        if not info:
             return render(
                request,
                "create_part_c.html",
                {
                    "step": 1,
                    "formset": formset,
                    "question_paper": qp,
                    "required_questions": int(request.POST.get("required_questions", 0)),
                    "each_questions_mark": int(request.POST.get("each_questions_mark", 0)),
                    "or_question": True,
                    "part_type": "C",
                    "error_message": "⚠️ Section Information/Instructions are required.",
                    "instructions": SectionInstruction.objects.filter(part_type='C', is_active=True),
                },
            )


        required_questions = int(request.POST.get("required_questions"))
        each_questions_mark = int(request.POST.get("each_questions_mark"))

        if formset.is_valid():
            or_question = True
            total = required_questions * each_questions_mark

            # Get existing PartC for this QP if it exists, otherwise create
            part_c, created = PartC.objects.get_or_create(
                details=qp,
                defaults={
                    "info": request.POST.get("info"),
                    "required_questions": required_questions,
                    "each_questions_mark": each_questions_mark,
                    "or_question": or_question,
                    "total": total,
                },
            )

            if created:
                # first time creating Part C for this QP
                qp.maximum_mark = (qp.maximum_mark or 0) + total
            else:
                # Part C already exists → update it & adjust maximum_mark
                old_total = part_c.total or 0
                part_c.info = request.POST.get("info")
                part_c.required_questions = required_questions
                part_c.each_questions_mark = each_questions_mark
                part_c.or_question = or_question
                part_c.total = total
                part_c.save()
                # remove old questions before saving new ones
                part_c.questions.all().delete()
                qp.maximum_mark = (qp.maximum_mark or 0) - old_total + total

            qp.save()

            # Save all questions first
            saved_questions = []
            for form in formset:
                if form.cleaned_data:
                    q = form.save(commit=False)
                    q.part_c = part_c
                    q.save()
                    saved_questions.append(q)
            
            # Organize into OR groups (pairs) and validate modules
            for i in range(0, len(saved_questions), 2):
                if i + 1 < len(saved_questions):
                    q1 = saved_questions[i]
                    q2 = saved_questions[i + 1]
                    
                    # Server-side enforcement: ensure modules match
                    if q1.module != q2.module:
                        q2.module = q1.module
                        q2.save()

                    # Mark both as OR group
                    q1.is_or_group = True
                    q2.is_or_group = True
                    
                    # Assign same OR group number
                    or_group_number = (i // 2) + 1
                    q1.or_group_number = or_group_number
                    q2.or_group_number = or_group_number
                    
                    q1.save()
                    q2.save()

            # ✅ Only redirect when everything is valid and saved
            return redirect("question_paper:review", pk=qp.id)

        # ❌ Formset invalid → stay on STEP 2 page with errors
        return render(
            request,
            "create_part_c.html",
            {
                "step": 1,
                "formset": formset,
                "question_paper": qp,
                "required_questions": required_questions,
                "each_questions_mark": each_questions_mark,
                "or_question": True,
                "part_type": "C",
                "error_message": "⚠️ Please fill all required fields correctly."
            },
        )


# ---------------------------------------------------------------------
# REVIEW PAGE + EDIT VIEWS
# ---------------------------------------------------------------------
class ReviewPage(View):
    """
    Shows a summary of Heading, Part A, B, C with Edit buttons.
    From here user can go to DownloadPage.
    """

    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        part_a = getattr(qp, "part_a_details", None)
        part_b = getattr(qp, "part_b_details", None)
        part_c = getattr(qp, "part_c_details", None)

        # Calculate completion status
        completed_count = 0
        if part_a: completed_count += 1
        if part_b: completed_count += 1
        if part_c: completed_count += 1

        context = {
            "qp": qp,
            "part_a": part_a,
            "part_b": part_b,
            "part_c": part_c,
            "completed_count": completed_count,
        }
        return render(request, "review.html", context)


class EditHeading(View):
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        form = QuestionPaperForm(instance=qp)
        return render(request, "edit_heading.html", {"form": form, "qp": qp})

    def post(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        form = QuestionPaperForm(request.POST, instance=qp)
        if form.is_valid():
            form.save()
            return redirect("question_paper:review", pk=qp.id)
        return render(request, "edit_heading.html", {"form": form, "qp": qp})


class EditPartA(View):
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        part_a = get_object_or_404(PartA, details=qp)

        PartAFormset = modelformset_factory(
            PartAQuestions,
            form=PartAQuestionsForms,
            extra=0
        )

        formset = PartAFormset(
            queryset=part_a.questions.all(),
            form_kwargs={'question_paper_id': qp.id, 'part_type': 'A'}
        )

        return render(
            request,
            "edit_part_a.html",
            {
                "question_paper": qp,
                "part_a": part_a,
                "formset": formset,
                "part_type": "A",
                "instructions": SectionInstruction.objects.filter(part_type='A', is_active=True),
            },
        )

    def post(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        part_a = get_object_or_404(PartA, details=qp)

        PartAFormset = modelformset_factory(
            PartAQuestions,
            form=PartAQuestionsForms,
            extra=0
        )

        formset = PartAFormset(
            request.POST,
            request.FILES,
            queryset=part_a.questions.all(),
            form_kwargs={'question_paper_id': qp.id, 'part_type': 'A'}
        )

        if formset.is_valid():
            part_a.info = request.POST.get("info", part_a.info)
            part_a.save()

            # Save all forms
            formset.save()

            # Handle sub-question relationships
            for form in formset:
                if form.cleaned_data:
                    q = form.instance
                    if q.is_sub_question and q.parent_question:
                        # Ensure parent is in same part
                        if q.parent_question.part_a != part_a:
                            q.parent_question = None
                            q.save()

            return redirect("question_paper:review", pk=qp.id)

        # ❌ Only when invalid
        return render(
            request,
            "edit_part_a.html",
            {
                "question_paper": qp,
                "part_a": part_a,
                "formset": formset,
                "part_type": "A",
                "instructions": SectionInstruction.objects.filter(part_type='A', is_active=True),
            },
        )


class EditPartB(View):
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        part_b = get_object_or_404(PartB, details=qp)

        PartBFormset = modelformset_factory(
            PartBQuestions,
            form=PartBQuestionsForms,
            extra=0
        )

        formset = PartBFormset(
            queryset=part_b.questions.all(),
            form_kwargs={'question_paper_id': qp.id, 'part_type': 'B'}
        )

        return render(
            request,
            "edit_part_b.html",
            {
                "question_paper": qp,
                "part_b": part_b,
                "formset": formset,
                "part_type": "B"
            },
        )

    def post(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        part_b = get_object_or_404(PartB, details=qp)

        PartBFormset = modelformset_factory(
            PartBQuestions,
            form=PartBQuestionsForms,
            extra=0
        )

        formset = PartBFormset(
            request.POST,
            request.FILES,
            queryset=part_b.questions.all(),
            form_kwargs={'question_paper_id': qp.id, 'part_type': 'B'}
        )

        if formset.is_valid():
            part_b.info = request.POST.get("info", part_b.info)
            part_b.save()

            formset.save()

            return redirect("question_paper:review", pk=qp.id)

        return render(
            request,
            "edit_part_b.html",
            {
                "question_paper": qp,
                "part_b": part_b,
                "formset": formset,
                "part_type": "B"
            },
        )


class EditPartC(View):
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        part_c = get_object_or_404(PartC, details=qp)

        PartCFormset = modelformset_factory(
            PartCQuestions,
            form=PartCQuestionsForms,
            extra=0
        )

        formset = PartCFormset(
            queryset=part_c.questions.order_by("or_group_number", "id"),
            form_kwargs={'question_paper_id': qp.id, 'part_type': 'C'}
        )

        return render(
            request,
            "edit_part_c.html",
            {
                "question_paper": qp,
                "part_c": part_c,
                "formset": formset,
                "part_type": "C"
            },
        )

    def post(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        part_c = get_object_or_404(PartC, details=qp)

        PartCFormset = modelformset_factory(
            PartCQuestions,
            form=PartCQuestionsForms,
            extra=0
        )

        formset = PartCFormset(
            request.POST,
            request.FILES,
            queryset=part_c.questions.order_by("or_group_number", "id"),
            form_kwargs={'question_paper_id': qp.id, 'part_type': 'C'}
        )

        if formset.is_valid():
            part_c.info = request.POST.get("info", part_c.info)
            part_c.save()

            formset.save()

            return redirect("question_paper:review", pk=qp.id)

        return render(
            request,
            "edit_part_c.html",
            {
                "question_paper": qp,
                "part_c": part_c,
                "formset": formset,
                "part_type": "C"
            },
        )


# ---------------------------------------------------------------------
# Download page (shows 3 buttons)
# ---------------------------------------------------------------------
class DownloadPage(View):
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        return render(request, "pdf_download.html", {"question_paper": qp})


# ---------------------------------------------------------------------
# PDF Views
# ---------------------------------------------------------------------
class QuestionPaperPDF(View):
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)

        part_a = getattr(qp, "part_a_details", None)
        part_b = getattr(qp, "part_b_details", None)
        part_c = getattr(qp, "part_c_details", None)

        context = {
            "qp": qp,
            "part_a": part_a,
            "part_b": part_b,
            "part_c": part_c,
            "questions_a": part_a.questions.all() if part_a else [],
            "questions_b": part_b.questions.all() if part_b else [],
            "questions_c": (
                part_c.questions.order_by("or_group_number", "id")
                if part_c else []
            ),
        }

        return render_to_pdf("pdf/question_paper_pdf.html", context)


# ---------------------------------------------------------------------------------------
def get_exam_style_image(image_path, max_width=None, max_height=None):
    """
    Exam-style image for Question Paper & Answer Sheet:
    - Pure black & white
    - High contrast
    - Proper A4 size (4.5cm x 3.5cm max)
    """
    from PIL import Image, ImageOps
    from io import BytesIO
    from reportlab.platypus import Image as RLImage
    from reportlab.lib.units import cm

    if max_width is None: max_width = 4.5 * cm
    if max_height is None: max_height = 3.5 * cm

    img = Image.open(image_path)

    # Convert to grayscale
    img = img.convert("L")

    # Improve contrast
    img = ImageOps.autocontrast(img, cutoff=2)

    # Convert to pure black & white
    img = img.point(lambda x: 0 if x < 150 else 255, "1")

    # Add margin like exam paper
    img = ImageOps.expand(img, border=12, fill=255)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    rl_img = RLImage(buffer)
    rl_img._restrictSize(max_width, max_height)

    return rl_img


# ------------------------------------------------------------------------------------
class AnswerSheetPDF(View):
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)

        part_a = getattr(qp, "part_a_details", None)
        part_b = getattr(qp, "part_b_details", None)
        part_c = getattr(qp, "part_c_details", None)

        qa = part_a.questions.all() if part_a else []
        qb = part_b.questions.all() if part_b else []
        qc = part_c.questions.order_by("or_group_number", "id") if part_c else []

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="answer_sheet_{qp.id}.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30,
        )

        styles = getSampleStyleSheet()
        story = []

        # ---------------- HEADER ----------------
        story.append(Paragraph("SCORING INDICATORS", styles["Title"]))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"COURSE NAME : {qp.subject_name.upper()}", styles["Normal"]))
        story.append(
            Paragraph(
                f"COURSE CODE : TED({qp.revesion}){qp.subject_code} &nbsp;&nbsp; QID : __________",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        # ---------------- TABLE DATA ----------------
        data = [
            ["Q No", "Scoring Indicators", "Split", "Sub Total", "Total"]
        ]

        # ================= PART A =================
        if part_a:
            data.append(["", "PART A", "", "", str(len(qa))])

            for i, q in enumerate(qa, start=1):
                total_col = str(len(qa)) if i == 1 else ""
                data.append([
                    f"I.{i}",
                    Paragraph(q.answer or "", styles["Normal"]),
                    "1",
                    "1",
                    total_col,
                ])

        # ================= PART B =================
        if part_b:
            data.append(["", "PART B", "", "", str(part_b.total)])

            for i, q in enumerate(qb, start=1):
                cell_flow = []

                if q.answer_text:
                    cell_flow.append(Paragraph(q.answer_text, styles["Normal"]))

                if q.answer_equation:
                    cell_flow.append(Spacer(1, 4))
                    cell_flow.append(Paragraph(q.answer_equation, styles["Normal"]))

                if q.answer_image:
                    try:
                        cell_flow.append(Spacer(1, 6))
                        cell_flow.append(Paragraph("<b>Diagram:</b>", styles["Normal"]))
                        cell_flow.append(Spacer(1, 4))
                        img = get_exam_style_image(q.answer_image.path)
                        cell_flow.append(img)
                    except Exception:
                        cell_flow.append(Paragraph("[Diagram could not be loaded]", styles["Normal"]))

                if not cell_flow:
                    cell_flow = [Paragraph("", styles["Normal"])]

                total_col = str(part_b.total) if i == 1 else ""

                data.append([
                    f"II.{i}",
                    cell_flow,
                    str(part_b.each_questions_mark),
                    str(part_b.each_questions_mark),
                    total_col,
                ])

        # ================= PART C (OR) =================
        if part_c:
            data.append(["", "PART C", "", "", str(part_c.total)])

            from itertools import groupby

            for idx, (_, group) in enumerate(
                groupby(qc, key=lambda x: x.or_group_number), start=1
            ):
                group = list(group)

                def build_flow(q, label):
                    flow = []

                    if q.answer_text:
                        flow.append(Paragraph(f"{label} {q.answer_text}", styles["Normal"]))

                    if q.answer_equation:
                        flow.append(Spacer(1, 4))
                        flow.append(Paragraph(q.answer_equation, styles["Normal"]))

                    if q.answer_image:
                        try:
                            flow.append(Spacer(1, 6))
                            flow.append(Paragraph("<b>Diagram:</b>", styles["Normal"]))
                            flow.append(Spacer(1, 4))
                            img = get_exam_style_image(q.answer_image.path)
                            flow.append(img)
                        except Exception:
                            flow.append(Paragraph("[Diagram could not be loaded]", styles["Normal"]))

                    return flow or [Paragraph("", styles["Normal"])]

                total_col = str(part_c.total) if idx == 1 else ""

                data.append([
                    f"III.{idx}",
                    build_flow(group[0], "(i)"),
                    str(part_c.each_questions_mark),
                    str(part_c.each_questions_mark),
                    total_col,
                ])
                data.append([
                    "",
                    Paragraph("<b>OR</b>", styles["Normal"]),
                    "",
                    "",
                    "",
                ])
                data.append([
                    "",
                    build_flow(group[1], "(ii)"),
                    "",
                    "",
                    "",
                ])

        # ---------------- TABLE ----------------
        table = Table(
            data,
            colWidths=[40, 320, 60, 60, 60],
            repeatRows=1,
            splitByRow=1,   # prevents LayoutError
        )

        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),
                    ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                ]
            )
        )

        story.append(table)
        doc.build(story)
        return response


class BlueprintPDF(View):
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)

        part_a = getattr(qp, "part_a_details", None)
        part_b = getattr(qp, "part_b_details", None)
        part_c = getattr(qp, "part_c_details", None)

        qa = part_a.questions.all() if part_a else PartAQuestions.objects.none()
        qb = part_b.questions.all() if part_b else PartBQuestions.objects.none()
        qc = part_c.questions.all() if part_c else PartCQuestions.objects.none()

        # --------- module hours from user ----------
        hours_map = {
            1: qp.module1_hours or 0,
            2: qp.module2_hours or 0,
            3: qp.module3_hours or 0,
            4: qp.module4_hours or 0,
        }
        total_hours = sum(hours_map.values())
        total_marks_all = qp.maximum_mark or 0

        # ---------- Module-wise data (I,II,III,IV) ----------
        modules = [1, 2, 3, 4]
        module_rows = []

        total_a_q = total_a_m = 0
        total_b_q = total_b_m = 0
        total_c_q = total_c_m = 0
        total_q_all = total_m_all = 0

        for m in modules:
            a_count = qa.filter(module=m).count()
            b_count = qb.filter(module=m).count()
            c_count = qc.filter(module=m).count()

            a_marks = a_count * 1
            b_marks = b_count * (part_b.each_questions_mark if part_b else 0)
            c_marks = c_count * (part_c.each_questions_mark if part_c else 0)

            row_total_q = a_count + b_count + c_count
            row_total_m = a_marks + b_marks + c_marks

            hrs = hours_map.get(m, 0)
            hr_mark_share = 0
            if total_hours and total_marks_all and hrs:
                hr_mark_share = round(hrs / total_hours * total_marks_all, 2)

            module_rows.append({
                "module": m,
                "hours": hrs,
                "hrs_mark_share": hr_mark_share,
                "a_q": a_count,
                "a_m": a_marks,
                "b_q": b_count,
                "b_m": b_marks,
                "c_q": c_count,
                "c_m": c_marks,
                "total_q": row_total_q,
                "total_m": row_total_m,
            })

            total_a_q += a_count
            total_a_m += a_marks
            total_b_q += b_count
            total_b_m += b_marks
            total_c_q += c_count
            total_c_m += c_marks
            total_q_all += row_total_q
            total_m_all += row_total_m

        module_totals = {
            "a_q": total_a_q,
            "a_m": total_a_m,
            "b_q": total_b_q,
            "b_m": total_b_m,
            "c_q": total_c_q,
            "c_m": total_c_m,
            "total_q": total_q_all,
            "total_m": total_m_all,
        }

        # ---------- Cognitive-level-wise data ----------
        target_percent = {
            "R": qp.percent_R,
            "U": qp.percent_U,
            "A": qp.percent_A,
        }

        levels = [("R", "Remembering"), ("U", "Understanding"), ("A", "Application")]
        level_rows = []

        total_level_a_q = total_level_a_m = 0
        total_level_b_q = total_level_b_m = 0
        total_level_c_q = total_level_c_m = 0
        total_level_q_all = total_level_m_all = 0

        for code, name in levels:
            a_q = qa.filter(level=code).count()
            b_q = qb.filter(level=code).count()
            c_q = qc.filter(level=code).count()

            a_m = a_q * 1
            b_m = b_q * (part_b.each_questions_mark if part_b else 0)
            c_m = c_q * (part_c.each_questions_mark if part_c else 0)

            level_total_m = a_m + b_m + c_m
            user_percent = target_percent.get(code)

            level_rows.append({
                "code": code,
                "name": name,
                "percent": user_percent,
                "a_q": a_q,
                "a_m": a_m,
                "b_q": b_q,
                "b_m": b_m,
                "c_q": c_q,
                "c_m": c_m,
                "total_q": a_q + b_q + c_q,
                "total_m": level_total_m,
            })

            total_level_a_q += a_q
            total_level_a_m += a_m
            total_level_b_q += b_q
            total_level_b_m += b_m
            total_level_c_q += c_q
            total_level_c_m += c_m
            total_level_q_all += (a_q + b_q + c_q)
            total_level_m_all += level_total_m

        level_totals = {
            "percent": (qp.percent_R or 0) + (qp.percent_U or 0) + (qp.percent_A or 0),
            "a_q": total_level_a_q,
            "a_m": total_level_a_m,
            "b_q": total_level_b_q,
            "b_m": total_level_b_m,
            "c_q": total_level_c_q,
            "c_m": total_level_c_m,
            "total_q": total_level_q_all,
            "total_m": total_level_m_all,
        }

        context = {
            "qp": qp,
            "module_rows": module_rows,
            "module_totals": module_totals,
            "level_rows": level_rows,
            "level_totals": level_totals,
            "total_marks_all": total_marks_all,
        }
        return render_to_pdf("pdf/blueprint_pdf.html", context)


# ---------------------------------------------------------------------
# ADDITIONAL IMPORTANT FUNCTIONS
# ---------------------------------------------------------------------
def handle_sub_question_logic(question, part_obj, part_type):
    """
    Helper function to handle sub-question parent relationships
    """
    if question.is_sub_question and question.parent_question:
        # Ensure parent question is in the same part
        if part_type == 'A' and question.parent_question.part_a != part_obj:
            # Find or create parent in current part_a
            parent_q = PartAQuestions.objects.filter(
                part_a=part_obj,
                question=question.parent_question.question
            ).first()
            if not parent_q:
                parent_q = PartAQuestions.objects.create(
                    part_a=part_obj,
                    module=question.parent_question.module,
                    level=question.parent_question.level,
                    question=question.parent_question.question,
                    text_below_image=question.parent_question.text_below_image,
                    answer=question.parent_question.answer,
                    question_image=question.parent_question.question_image,
                    question_image_position=question.parent_question.question_image_position,
                    question_image_size=question.parent_question.question_image_size,
                    is_sub_question=False
                )
            question.parent_question = parent_q
        
        elif part_type == 'B' and question.parent_question.part_b != part_obj:
            # Find or create parent in current part_b
            parent_q = PartBQuestions.objects.filter(
                part_b=part_obj,
                question=question.parent_question.question
            ).first()
            if not parent_q:
                parent_q = PartBQuestions.objects.create(
                    part_b=part_obj,
                    module=question.parent_question.module,
                    level=question.parent_question.level,
                    question=question.parent_question.question,
                    text_below_image=question.parent_question.text_below_image,
                    answer_text=question.parent_question.answer_text,
                    answer_equation=question.parent_question.answer_equation,
                    answer_image=question.parent_question.answer_image,
                    question_image=question.parent_question.question_image,
                    question_image_position=question.parent_question.question_image_position,
                    question_image_size=question.parent_question.question_image_size,
                    is_sub_question=False
                )
            question.parent_question = parent_q
    
    return question


# ---------------------------------------------------------------------
# ERROR HANDLING VIEWS
# ---------------------------------------------------------------------
class ErrorView(View):
    """Generic error page view"""
    def get(self, request, *args, **kwargs):
        error_message = request.GET.get('message', 'An unexpected error occurred.')
        return render(request, "error.html", {"error_message": error_message})


class SessionExpiredView(View):
    """View for when session expires"""
    def get(self, request, *args, **kwargs):
        return render(request, "session_expired.html")


# ---------------------------------------------------------------------
# HEALTH CHECK ENDPOINT
# ---------------------------------------------------------------------
@require_GET
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        "status": "healthy",
        "timestamp": timezone.now().isoformat()
    })


# ---------------------------------------------------------------------
# RESUME CREATION VIEW
# ---------------------------------------------------------------------
class ResumeQPView(View):
    """
    Sets the session variable for the selected question paper and redirects
    to the appropriate step based on progress.
    """
    def get(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        
        # Set session variable so creation views know which QP we are working on
        request.session["question_paper_id"] = qp.id
        
        # Redirect to the correct step
        return redirect(qp.get_resume_url)

# ---------------------------------------------------------------------
# RESUME LIST VIEW
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# RESUME LIST VIEW
# ---------------------------------------------------------------------
class ResumeListPage(View):
    """Page to list incomplete question papers for resuming"""
    
    def get(self, request, *args, **kwargs):
        recent_question_papers = QuestionPaper.objects.order_by('-id')[:20]
        return render(request, "resume_list.html", {
            "recent_question_papers": recent_question_papers
        })


class DeleteQPView(LoginRequiredMixin, View):
    """Delete a question paper"""
    login_url = '/admin/login/'
    
    def post(self, request, pk, *args, **kwargs):
        qp = get_object_or_404(QuestionPaper, pk=pk)
        qp.delete()
        return redirect("question_paper:resume_list")





# =====================================================================
# MANAGEMENT VIEWS - CRUD FOR DROPDOWN MODELS
# =====================================================================

from .forms import (
    RevisionForm,
    ExamNameForm,
    SubjectCodeForm,
    QuestionModuleForm,
    ModuleOutcomeForm,
    SectionInstructionForm,
)
from .models import (
    Revision,
    ExamName,
    SubjectCode,
    QuestionModule,
    ModuleOutcome,
    SectionInstruction,
)
from django.contrib import messages
from django.db.models import Q



# ---------------------------------------------------------------------
# REVISION MANAGEMENT
# ---------------------------------------------------------------------
class RevisionListView(LoginRequiredMixin, View):
    """List all revisions with search and pagination"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        revisions = Revision.objects.all().order_by('-year')
        
        if search_query:
            revisions = revisions.filter(year__icontains=search_query)
        
        context = {
            'revisions': revisions,
            'search_query': search_query,
        }
        return render(request, 'manage_revisions.html', context)


class RevisionCreateView(LoginRequiredMixin, View):
    """Create a new revision"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        form = RevisionForm()
        return render(request, 'revision_form.html', {'form': form, 'action': 'Add'})
    
    def post(self, request, *args, **kwargs):
        form = RevisionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Revision added successfully!')
            return redirect('question_paper:revision_list')
        return render(request, 'revision_form.html', {'form': form, 'action': 'Add'})


class RevisionUpdateView(LoginRequiredMixin, View):
    """Update an existing revision"""
    login_url = '/admin/login/'
    
    def get(self, request, pk, *args, **kwargs):
        revision = get_object_or_404(Revision, pk=pk)
        form = RevisionForm(instance=revision)
        return render(request, 'revision_form.html', {'form': form, 'action': 'Edit', 'object': revision})
    
    def post(self, request, pk, *args, **kwargs):
        revision = get_object_or_404(Revision, pk=pk)
        form = RevisionForm(request.POST, instance=revision)
        if form.is_valid():
            form.save()
            messages.success(request, 'Revision updated successfully!')
            return redirect('question_paper:revision_list')
        return render(request, 'revision_form.html', {'form': form, 'action': 'Edit', 'object': revision})


class RevisionDeleteView(LoginRequiredMixin, View):
    """Delete a revision"""
    login_url = '/admin/login/'
    
    def post(self, request, pk, *args, **kwargs):
        revision = get_object_or_404(Revision, pk=pk)
        revision.delete()
        messages.success(request, 'Revision deleted successfully!')
        return redirect('question_paper:revision_list')


# ---------------------------------------------------------------------
# EXAM NAME MANAGEMENT
# ---------------------------------------------------------------------
class ExamNameListView(LoginRequiredMixin, View):
    """List all exam names with search"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        exam_names = ExamName.objects.all().order_by('display_order', 'name')
        
        if search_query:
            exam_names = exam_names.filter(name__icontains=search_query)
        
        context = {
            'exam_names': exam_names,
            'search_query': search_query,
        }
        return render(request, 'manage_exam_names.html', context)


class ExamNameCreateView(LoginRequiredMixin, View):
    """Create a new exam name"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        form = ExamNameForm()
        return render(request, 'exam_name_form.html', {'form': form, 'action': 'Add'})
    
    def post(self, request, *args, **kwargs):
        form = ExamNameForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam name added successfully!')
            return redirect('question_paper:exam_name_list')
        return render(request, 'exam_name_form.html', {'form': form, 'action': 'Add'})


class ExamNameUpdateView(LoginRequiredMixin, View):
    """Update an existing exam name"""
    login_url = '/admin/login/'
    
    def get(self, request, pk, *args, **kwargs):
        exam_name = get_object_or_404(ExamName, pk=pk)
        form = ExamNameForm(instance=exam_name)
        return render(request, 'exam_name_form.html', {'form': form, 'action': 'Edit', 'object': exam_name})
    
    def post(self, request, pk, *args, **kwargs):
        exam_name = get_object_or_404(ExamName, pk=pk)
        form = ExamNameForm(request.POST, instance=exam_name)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam name updated successfully!')
            return redirect('question_paper:exam_name_list')
        return render(request, 'exam_name_form.html', {'form': form, 'action': 'Edit', 'object': exam_name})


class ExamNameDeleteView(LoginRequiredMixin, View):
    """Delete an exam name"""
    login_url = '/admin/login/'
    
    def post(self, request, pk, *args, **kwargs):
        exam_name = get_object_or_404(ExamName, pk=pk)
        exam_name.delete()
        messages.success(request, 'Exam name deleted successfully!')
        return redirect('question_paper:exam_name_list')


# ---------------------------------------------------------------------
# SUBJECT CODE MANAGEMENT
# ---------------------------------------------------------------------
class SubjectCodeListView(LoginRequiredMixin, View):
    """List all subject codes with search"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        subject_codes = SubjectCode.objects.all().order_by('code')
        
        if search_query:
            subject_codes = subject_codes.filter(
                Q(code__icontains=search_query) | Q(subject_name__icontains=search_query)
            )
        
        context = {
            'subject_codes': subject_codes,
            'search_query': search_query,
        }
        return render(request, 'manage_subject_codes.html', context)


class SubjectCodeCreateView(LoginRequiredMixin, View):
    """Create a new subject code"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        form = SubjectCodeForm()
        return render(request, 'subject_code_form.html', {'form': form, 'action': 'Add'})
    
    def post(self, request, *args, **kwargs):
        form = SubjectCodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject code added successfully!')
            return redirect('question_paper:subject_code_list')
        return render(request, 'subject_code_form.html', {'form': form, 'action': 'Add'})


class SubjectCodeUpdateView(LoginRequiredMixin, View):
    """Update an existing subject code"""
    login_url = '/admin/login/'
    
    def get(self, request, pk, *args, **kwargs):
        subject_code = get_object_or_404(SubjectCode, pk=pk)
        form = SubjectCodeForm(instance=subject_code)
        return render(request, 'subject_code_form.html', {'form': form, 'action': 'Edit', 'object': subject_code})
    
    def post(self, request, pk, *args, **kwargs):
        subject_code = get_object_or_404(SubjectCode, pk=pk)
        form = SubjectCodeForm(request.POST, instance=subject_code)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject code updated successfully!')
            return redirect('question_paper:subject_code_list')
        return render(request, 'subject_code_form.html', {'form': form, 'action': 'Edit', 'object': subject_code})


class SubjectCodeDeleteView(LoginRequiredMixin, View):
    """Delete a subject code"""
    login_url = '/admin/login/'
    
    def post(self, request, pk, *args, **kwargs):
        subject_code = get_object_or_404(SubjectCode, pk=pk)
        subject_code.delete()
        messages.success(request, 'Subject code deleted successfully!')
        return redirect('question_paper:subject_code_list')


# ---------------------------------------------------------------------
# MODULE MANAGEMENT
# ---------------------------------------------------------------------
class ModuleListView(LoginRequiredMixin, View):
    """List all modules"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        modules = QuestionModule.objects.all().order_by('module_number')
        return render(request, 'manage_modules.html', {'modules': modules})


class ModuleCreateView(LoginRequiredMixin, View):
    """Create a new module"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        form = QuestionModuleForm()
        return render(request, 'module_form.html', {'form': form, 'action': 'Add'})
    
    def post(self, request, *args, **kwargs):
        form = QuestionModuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module added successfully!')
            return redirect('question_paper:module_list')
        return render(request, 'module_form.html', {'form': form, 'action': 'Add'})


class ModuleUpdateView(LoginRequiredMixin, View):
    """Update an existing module"""
    login_url = '/admin/login/'
    
    def get(self, request, pk, *args, **kwargs):
        module = get_object_or_404(QuestionModule, pk=pk)
        form = QuestionModuleForm(instance=module)
        return render(request, 'module_form.html', {'form': form, 'action': 'Edit', 'object': module})
    
    def post(self, request, pk, *args, **kwargs):
        module = get_object_or_404(QuestionModule, pk=pk)
        form = QuestionModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module updated successfully!')
            return redirect('question_paper:module_list')
        return render(request, 'module_form.html', {'form': form, 'action': 'Edit', 'object': module})


class ModuleDeleteView(LoginRequiredMixin, View):
    """Delete a module"""
    login_url = '/admin/login/'
    
    def post(self, request, pk, *args, **kwargs):
        module = get_object_or_404(QuestionModule, pk=pk)
        module.delete()
        messages.success(request, 'Module deleted successfully!')
        return redirect('question_paper:module_list')


# ---------------------------------------------------------------------
# OUTCOME MANAGEMENT
# ---------------------------------------------------------------------
class OutcomeListView(LoginRequiredMixin, View):
    """List all module outcomes with search"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        outcomes = ModuleOutcome.objects.all().order_by('outcome_code')
        
        if search_query:
            outcomes = outcomes.filter(
                Q(outcome_code__icontains=search_query) | Q(description__icontains=search_query)
            )
        
        context = {
            'outcomes': outcomes,
            'search_query': search_query,
        }
        return render(request, 'manage_outcomes.html', context)


class OutcomeCreateView(LoginRequiredMixin, View):
    """Create a new module outcome"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        form = ModuleOutcomeForm()
        return render(request, 'outcome_form.html', {'form': form, 'action': 'Add'})
    
    def post(self, request, *args, **kwargs):
        form = ModuleOutcomeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module outcome added successfully!')
            return redirect('question_paper:outcome_list')
        return render(request, 'outcome_form.html', {'form': form, 'action': 'Add'})


class OutcomeUpdateView(LoginRequiredMixin, View):
    """Update an existing module outcome"""
    login_url = '/admin/login/'
    
    def get(self, request, pk, *args, **kwargs):
        outcome = get_object_or_404(ModuleOutcome, pk=pk)
        form = ModuleOutcomeForm(instance=outcome)
        return render(request, 'outcome_form.html', {'form': form, 'action': 'Edit', 'object': outcome})
    
    def post(self, request, pk, *args, **kwargs):
        outcome = get_object_or_404(ModuleOutcome, pk=pk)
        form = ModuleOutcomeForm(request.POST, instance=outcome)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module outcome updated successfully!')
            return redirect('question_paper:outcome_list')
        return render(request, 'outcome_form.html', {'form': form, 'action': 'Edit', 'object': outcome})


class OutcomeDeleteView(LoginRequiredMixin, View):
    """Delete a module outcome"""
    login_url = '/admin/login/'
    
    def post(self, request, pk, *args, **kwargs):
        outcome = get_object_or_404(ModuleOutcome, pk=pk)
        outcome.delete()
        messages.success(request, 'Module outcome deleted successfully!')
        return redirect('question_paper:outcome_list')


# ---------------------------------------------------------------------
# INSTRUCTION MANAGEMENT
# ---------------------------------------------------------------------
class InstructionListView(LoginRequiredMixin, View):
    """List all section instructions"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        instructions = SectionInstruction.objects.all().order_by('part_type', 'id')
        
        if search_query:
            instructions = instructions.filter(text__icontains=search_query)
        
        context = {
            'instructions': instructions,
            'search_query': search_query,
        }
        return render(request, 'manage_instructions.html', context)


class InstructionCreateView(LoginRequiredMixin, View):
    """Create a new section instruction"""
    login_url = '/admin/login/'
    
    def get(self, request, *args, **kwargs):
        form = SectionInstructionForm()
        return render(request, 'instruction_form.html', {'form': form, 'action': 'Add'})
    
    def post(self, request, *args, **kwargs):
        form = SectionInstructionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section instruction added successfully!')
            return redirect('question_paper:instruction_list')
        return render(request, 'instruction_form.html', {'form': form, 'action': 'Add'})


class InstructionUpdateView(LoginRequiredMixin, View):
    """Update an existing section instruction"""
    login_url = '/admin/login/'
    
    def get(self, request, pk, *args, **kwargs):
        instruction = get_object_or_404(SectionInstruction, pk=pk)
        form = SectionInstructionForm(instance=instruction)
        return render(request, 'instruction_form.html', {'form': form, 'action': 'Edit', 'object': instruction})
    
    def post(self, request, pk, *args, **kwargs):
        instruction = get_object_or_404(SectionInstruction, pk=pk)
        form = SectionInstructionForm(request.POST, instance=instruction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section instruction updated successfully!')
            return redirect('question_paper:instruction_list')
        return render(request, 'instruction_form.html', {'form': form, 'action': 'Edit', 'object': instruction})


class InstructionDeleteView(LoginRequiredMixin, View):
    """Delete a section instruction"""
    login_url = '/admin/login/'
    
    def post(self, request, pk, *args, **kwargs):
        instruction = get_object_or_404(SectionInstruction, pk=pk)
        instruction.delete()
        messages.success(request, 'Section instruction deleted successfully!')
        return redirect('question_paper:instruction_list')

