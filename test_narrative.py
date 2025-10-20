"""Test the narrative generation in reconciliation reports."""

import os
os.environ['MEDREC_SKIP_LLM'] = 'True'

from core.med_rec_pipeline import MedRecPipeline

# Sample clinical text with clear medication changes
prior_text = """
PRIOR MEDICATION LIST (Home Medications):
    1. Metformin 500mg tablet by mouth twice daily - for diabetes
    2. Lisinopril 10mg tablet by mouth once daily - for hypertension
    3. Aspirin 81mg tablet by mouth once daily - for cardiovascular protection
    4. Atorvastatin 20mg tablet by mouth at bedtime - for cholesterol
"""

current_text = """
CURRENT MEDICATIONS (From Clinic Visit):
    Patient continues metformin 500mg PO BID for diabetes control.
    Increased lisinopril to 20mg PO daily due to elevated BP readings.
    Patient stopped taking aspirin 3 weeks ago due to GI upset.
    Continue atorvastatin 20mg QHS.
    Started insulin glargine 10 units subcutaneous at bedtime for better glycemic control.
"""

print("="*80)
print("TESTING NARRATIVE GENERATION")
print("="*80)

# Initialize pipeline
pipeline = MedRecPipeline()

# Run reconciliation
result = pipeline.run_full_pipeline(prior_text, current_text)

# Save reports first
with open('test_narrative_report.md', 'w', encoding='utf-8') as f:
    f.write(result['report_markdown'])

with open('test_narrative_report.html', 'w', encoding='utf-8') as f:
    f.write(result['report_html'])

# Display the markdown report
print("\n" + "="*80)
print("MARKDOWN REPORT WITH NARRATIVE")
print("="*80)
# Print to file to avoid unicode issues
with open('test_narrative_report.md', 'r', encoding='utf-8') as f:
    print(f.read())

print("\n" + "="*80)
print("Reports saved:")
print("  - test_narrative_report.md")
print("  - test_narrative_report.html")
print("="*80)
