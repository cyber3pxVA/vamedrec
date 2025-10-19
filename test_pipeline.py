"""
Test Script for Clinical Med Rec Pipeline
Tests the 3-stage medication reconciliation pipeline end-to-end.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.med_rec_pipeline import MedRecPipeline
import json


def test_clinical_extraction():
    """Test Stage 1: Clinical extraction."""
    print("\n" + "=" * 80)
    print("TEST 1: Clinical Extraction (Stage 1)")
    print("=" * 80)
    
    pipeline = MedRecPipeline()
    
    test_text = """
    Current Medications:
    1. Metformin 500mg PO BID - for diabetes
    2. Lisinopril 10mg PO daily - for hypertension
    3. Patient stopped taking aspirin 81mg 3 weeks ago
    """
    
    try:
        meds = pipeline.run_extraction_only(test_text, "current")
        print(f"\n✓ Extracted {len(meds)} medications")
        
        for med in meds:
            print(f"\n  Drug: {med.drug_name_norm}")
            print(f"  Dose: {med.dose_strength}{med.dose_unit}")
            print(f"  Frequency: {med.frequency}")
            print(f"  Negated: {med.is_negated}")
            print(f"  Text: {med.raw_text_snippet[:60]}...")
        
        print("\n✓ Test 1 PASSED")
        return True
    
    except Exception as e:
        print(f"\n✗ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test full 3-stage pipeline."""
    print("\n" + "=" * 80)
    print("TEST 2: Full 3-Stage Pipeline")
    print("=" * 80)
    
    pipeline = MedRecPipeline()
    
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
    
    try:
        result = pipeline.run_full_pipeline(
            prior_text=prior_text,
            current_text=current_text,
            patient_id="TEST-123",
            encounter_id="ENC-TEST-001"
        )
        
        summary = result['reconciliation']['summary']
        
        print(f"\n✓ Pipeline completed successfully")
        print(f"\n  Prior medications: {summary.get('total_prior_meds', 0)}")
        print(f"  Current medications: {summary.get('total_current_meds', 0)}")
        print(f"  Matched: {summary.get('matched_count', 0)}")
        print(f"  Discrepancies: {summary.get('discrepancy_count', 0)}")
        print(f"  Additions: {summary.get('addition_count', 0)}")
        print(f"  Discontinuations: {summary.get('discontinuation_count', 0)}")
        print(f"  Ambiguities: {summary.get('ambiguity_count', 0)}")
        
        print("\n✓ Test 2 PASSED")
        return True
    
    except Exception as e:
        print(f"\n✗ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generation():
    """Test report generation."""
    print("\n" + "=" * 80)
    print("TEST 3: Report Generation")
    print("=" * 80)
    
    from core.report_generator import ReportGenerator
    
    test_result = {
        "matched": [
            {
                "drug_name": "metformin",
                "status": "continuing",
                "notes": "Same dose"
            }
        ],
        "discrepancies": [
            {
                "drug_name": "lisinopril",
                "discrepancy_type": "dose_change",
                "prior_value": "10mg",
                "current_value": "20mg",
                "notes": "Dose increased"
            }
        ],
        "additions": [],
        "discontinuations": [
            {
                "drug_name": "aspirin",
                "reason": "explicitly_discontinued",
                "notes": "GI side effects"
            }
        ],
        "ambiguities": [],
        "summary": {
            "total_prior_meds": 4,
            "total_current_meds": 4,
            "matched_count": 1,
            "discrepancy_count": 1,
            "addition_count": 0,
            "discontinuation_count": 1,
            "ambiguity_count": 0,
            "clinical_notes": "Test reconciliation"
        },
        "metadata": {
            "reconciliation_method": "llm_powered",
            "model": "gpt-4o"
        }
    }
    
    try:
        generator = ReportGenerator()
        report = generator.generate_report(test_result)
        
        # Check that report contains expected sections
        assert "Medication Reconciliation Report" in report
        assert "Executive Summary" in report
        assert "Matched Medications" in report
        assert "Discrepancies" in report
        assert "Action Items" in report
        
        print("\n✓ Report generated successfully")
        print(f"\n  Report length: {len(report)} characters")
        print("\n✓ Test 3 PASSED")
        return True
    
    except Exception as e:
        print(f"\n✗ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("CLINICAL MED REC PIPELINE TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Clinical Extraction", test_clinical_extraction),
        ("Full Pipeline", test_full_pipeline),
        ("Report Generation", test_report_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
