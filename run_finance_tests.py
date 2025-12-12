"""
Test Runner for Finance Agent Tests
Handles encoding issues and generates comprehensive reports
"""
import sys
import os
import io
import json
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import and run tests
import unittest
from test_finance_strategy import (
    TestReceiptOCRTool,
    TestTransactionValidator,
    TestDocumentAgent,
    TestOrchestratorAgent,
    TestReceiptToTransactionFlow,
    TestMonthlyReportGeneration,
    TestDailyExpenseLogging,
    TestReceiptProcessingE2E,
    TestPerformance
)

def run_test_suite(test_classes, suite_name="All Tests"):
    """Run a specific test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Capture output
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    output = stream.getvalue()
    
    return {
        "suite_name": suite_name,
        "result": result,
        "output": output,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success": result.wasSuccessful()
    }

def main():
    """Main test runner"""
    print("="*70)
    print("FINANCE AGENT COMPREHENSIVE TEST SUITE")
    print("Based on Testing Strategy Document")
    print("="*70)
    print(f"\nTest Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_results = []
    
    # Unit Tests (Quick - No LLM calls)
    print("\n" + "="*70)
    print("UNIT TESTS (Quick - No LLM calls)")
    print("="*70)
    
    unit_tests = [
        (TestReceiptOCRTool, "Receipt OCR Tool Tests"),
        (TestTransactionValidator, "Transaction Validator Tests"),
        (TestDocumentAgent, "Document Agent Tests (Mocked)")
    ]
    
    for test_class, name in unit_tests:
        print(f"\nRunning {name}...")
        result = run_test_suite([test_class], name)
        all_results.append(result)
        print(f"  Tests: {result['tests_run']}, Passed: {result['tests_run'] - result['failures'] - result['errors']}, Failed: {result['failures']}, Errors: {result['errors']}")
    
    # Integration and E2E Tests (Require LLM)
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        print("\n" + "="*70)
        print("INTEGRATION & E2E TESTS (Requires LLM API calls)")
        print("="*70)
        print("Note: These tests make real LLM API calls and may take several minutes.\n")
        
        integration_tests = [
            (TestOrchestratorAgent, "Orchestrator Agent Tests"),
            (TestReceiptToTransactionFlow, "Receipt to Transaction Flow"),
            (TestMonthlyReportGeneration, "Monthly Report Generation"),
            (TestDailyExpenseLogging, "Daily Expense Logging E2E"),
            (TestReceiptProcessingE2E, "Receipt Processing E2E"),
            (TestPerformance, "Performance Tests")
        ]
        
        for test_class, name in integration_tests:
            print(f"\nRunning {name}...")
            try:
                result = run_test_suite([test_class], name)
                all_results.append(result)
                print(f"  Tests: {result['tests_run']}, Passed: {result['tests_run'] - result['failures'] - result['errors']}, Failed: {result['failures']}, Errors: {result['errors']}")
            except Exception as e:
                print(f"  ERROR: {str(e)}")
                all_results.append({
                    "suite_name": name,
                    "error": str(e),
                    "tests_run": 0,
                    "failures": 0,
                    "errors": 1,
                    "skipped": 0,
                    "success": False
                })
    else:
        print("\n" + "="*70)
        print("SKIPPING INTEGRATION & E2E TESTS")
        print("="*70)
        print("Use --full flag to run integration and E2E tests (requires LLM API calls)")
    
    # Generate Summary Report
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = sum(r.get('tests_run', 0) for r in all_results)
    total_failures = sum(r.get('failures', 0) for r in all_results)
    total_errors = sum(r.get('errors', 0) for r in all_results)
    total_skipped = sum(r.get('skipped', 0) for r in all_results)
    total_passed = total_tests - total_failures - total_errors
    
    print(f"\nTotal Tests Run: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failures}")
    print(f"  Errors: {total_errors}")
    print(f"  Skipped: {total_skipped}")
    
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
    else:
        success_rate = 0
    
    # Detailed Results
    print("\n" + "-"*70)
    print("DETAILED RESULTS BY SUITE")
    print("-"*70)
    
    for result in all_results:
        suite_name = result.get('suite_name', 'Unknown')
        tests_run = result.get('tests_run', 0)
        failures = result.get('failures', 0)
        errors = result.get('errors', 0)
        skipped = result.get('skipped', 0)
        passed = tests_run - failures - errors
        
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"\n{status} {suite_name}")
        print(f"  Tests: {tests_run} | Passed: {passed} | Failed: {failures} | Errors: {errors} | Skipped: {skipped}")
        
        if failures > 0 and 'result' in result:
            print("  Failures:")
            for failure in result['result'].failures:
                print(f"    - {failure[0]}")
        
        if errors > 0 and 'result' in result:
            print("  Errors:")
            for error in result['result'].errors:
                print(f"    - {error[0]}")
    
    # Save Report to JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failures,
            "errors": total_errors,
            "skipped": total_skipped,
            "success_rate": success_rate
        },
        "suites": []
    }
    
    for result in all_results:
        suite_report = {
            "name": result.get('suite_name', 'Unknown'),
            "tests_run": result.get('tests_run', 0),
            "passed": result.get('tests_run', 0) - result.get('failures', 0) - result.get('errors', 0),
            "failures": result.get('failures', 0),
            "errors": result.get('errors', 0),
            "skipped": result.get('skipped', 0),
            "success": result.get('success', False)
        }
        
        if 'result' in result:
            suite_report['failures_detail'] = [str(f[0]) for f in result['result'].failures]
            suite_report['errors_detail'] = [str(e[0]) for e in result['result'].errors]
        
        report['suites'].append(suite_report)
    
    report_file = "test_finance_strategy_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"📄 Detailed report saved to: {report_file}")
    print(f"{'='*70}\n")
    
    # Exit with appropriate code
    return 0 if total_failures == 0 and total_errors == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)










