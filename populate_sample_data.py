#!/usr/bin/env python
"""
Script to populate sample data for dropdown fields in the Question Paper system.
Run this script with: python manage.py shell < populate_sample_data.py
"""

from question_paper.models import Revision, ExamName, SubjectCode

# Clear existing data (optional - comment out if you want to keep existing data)
print("Clearing existing data...")
Revision.objects.all().delete()
ExamName.objects.all().delete()
SubjectCode.objects.all().delete()

# Add Revisions
print("Adding revisions...")
revisions = ['2015', '2021', '2024']
for year in revisions:
    Revision.objects.create(year=year, is_active=True)
    print(f"  ✓ Added revision: {year}")

# Add Exam Names
print("\nAdding exam names...")
exam_names = [
    ("First Semester B.Tech Degree Examination", 1),
    ("Second Semester B.Tech Degree Examination", 2),
    ("Third Semester B.Tech Degree Examination", 3),
    ("Fourth Semester B.Tech Degree Examination", 4),
    ("Fifth Semester B.Tech Degree Examination", 5),
    ("Sixth Semester B.Tech Degree Examination", 6),
    ("Seventh Semester B.Tech Degree Examination", 7),
    ("Eighth Semester B.Tech Degree Examination", 8),
]

for name, order in exam_names:
    ExamName.objects.create(name=name, display_order=order, is_active=True)
    print(f"  ✓ Added exam name: {name}")

# Add Subject Codes
print("\nAdding subject codes...")
subjects = [
    ("CS101", "Introduction to Programming", 3),
    ("CS201", "Data Structures and Algorithms", 3),
    ("CS301", "Database Management Systems", 3),
    ("CS302", "Operating Systems", 3),
    ("CS401", "Computer Networks", 3),
    ("CS402", "Software Engineering", 3),
    ("MA101", "Engineering Mathematics I", 3),
    ("MA201", "Engineering Mathematics II", 3),
    ("PH101", "Engineering Physics", 3),
    ("EC201", "Digital Electronics", 3),
]

for code, name, duration in subjects:
    SubjectCode.objects.create(
        code=code,
        subject_name=name,
        duration_hours=duration,
        is_active=True
    )
    print(f"  ✓ Added subject: {code} - {name}")


# Add Modules
print("\nAdding modules...")
from question_paper.models import QuestionModule, ModuleOutcome

QuestionModule.objects.all().delete()
ModuleOutcome.objects.all().delete()

for i in range(1, 6):
    QuestionModule.objects.create(module_number=i, is_active=True)
    print(f"  ✓ Added module: {i}")

# Add Outcomes
print("\nAdding module outcomes...")
outcomes = [
    ("M1.01", "Understand basic concepts"),
    ("M1.02", "Apply knowledge"),
    ("M2.01", "Analyze problems"),
    ("M2.02", "Evaluate solutions"),
    ("M3.01", "Create designs"),
]

for code, desc in outcomes:
    ModuleOutcome.objects.create(outcome_code=code, description=desc, is_active=True)
    print(f"  ✓ Added outcome: {code}")


# Add Section Instructions
print("\nAdding section instructions...")
from question_paper.models import SectionInstruction

SectionInstruction.objects.all().delete()

# Part A Instruction
SectionInstruction.objects.create(
    part_type='A',
    text="Part A - MCQ Section contain default as 9 questions of 1 mark. All questions are compulsory.",
    is_active=True
)
print("  ✓ Added Part A default instruction")

# Part B Instruction
SectionInstruction.objects.create(
    part_type='B', 
    text="Part B - Descriptive Section. Answer all questions.", 
    is_active=True
)
print("  ✓ Added Part B default instruction")


print("\n" + "="*50)
print("✅ Sample data populated successfully!")
print("="*50)
print(f"\nSummary:")
print(f"  - Revisions: {Revision.objects.count()}")
print(f"  - Exam Names: {ExamName.objects.count()}")
print(f"  - Subject Codes: {SubjectCode.objects.count()}")
print(f"  - Modules: {QuestionModule.objects.count()}")
print(f"  - Outcomes: {ModuleOutcome.objects.count()}")
print(f"  - Instructions: {SectionInstruction.objects.count()}")
