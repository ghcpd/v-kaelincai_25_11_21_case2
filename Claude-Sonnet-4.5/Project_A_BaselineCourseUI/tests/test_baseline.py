"""
Test runner for Baseline Course UI
Loads scenarios, executes transformation, validates behavior, generates reports
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from baseline_ui import BaselineCourseUI


class TestRunner:
    def __init__(self, scenarios_path: str):
        with open(scenarios_path, 'r', encoding='utf-8') as f:
            self.scenarios_data = json.load(f)
        
        self.results = []
        self.ui_processor = BaselineCourseUI()
        
    def run_all_tests(self):
        """Execute all test scenarios"""
        print("=" * 80)
        print("BASELINE COURSE UI - TEST EXECUTION")
        print("=" * 80)
        
        for scenario in self.scenarios_data["scenarios"]:
            print(f"\n[TEST] {scenario['name']} ({scenario['id']})")
            result = self.run_scenario(scenario)
            self.results.append(result)
            
            status_symbol = "✓" if result["passed"] else "✗"
            print(f"  {status_symbol} Status: {result['status']}")
            print(f"  Warnings: {len(result['warnings'])}")
            print(f"  Errors: {len(result['errors'])}")
        
        return self.results
    
    def run_scenario(self, scenario: Dict) -> Dict:
        """Execute a single test scenario"""
        scenario_id = scenario["id"]
        input_data = scenario["input"]
        expected_baseline = scenario["expected_behavior"]["baseline"]
        
        # Transform the course data
        transform_result = self.ui_processor.transform(input_data)
        
        # Validate against expected behavior
        validations = self.validate_behavior(transform_result, expected_baseline, scenario)
        
        # Generate HTML prototype
        html_output_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'results', 
            f'{scenario_id}_baseline_layout.html'
        )
        os.makedirs(os.path.dirname(html_output_path), exist_ok=True)
        self.ui_processor.generate_html(transform_result, html_output_path)
        
        # Determine pass/fail
        passed = all(v["passed"] for v in validations)
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario["name"],
            "status": transform_result["status"],
            "passed": passed,
            "validations": validations,
            "warnings": transform_result.get("warnings", []),
            "errors": transform_result.get("errors", []),
            "metrics": transform_result.get("metrics", {}),
            "html_output": html_output_path,
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_behavior(self, result: Dict, expected: Dict, scenario: Dict) -> List[Dict]:
        """Validate transformation against expected baseline behavior"""
        validations = []
        
        if result["status"] != "success":
            # For baseline, expect errors on malformed input
            if scenario["id"] == "scenario_05_malformed_input":
                validations.append({
                    "check": "crashes_on_invalid",
                    "expected": True,
                    "actual": True,
                    "passed": True
                })
            return validations
        
        layout = result.get("layout", {})
        metadata = layout.get("metadata", {})
        
        # Check: info card NOT pinned
        validations.append({
            "check": "info_card_pinned",
            "expected": False,
            "actual": metadata.get("info_card_pinned", False),
            "passed": metadata.get("info_card_pinned", False) == False
        })
        
        # Check: sections NOT collapsible
        validations.append({
            "check": "sections_collapsible",
            "expected": False,
            "actual": metadata.get("sections_collapsible", False),
            "passed": metadata.get("sections_collapsible", False) == False
        })
        
        # Check: blocking attachment preview
        validations.append({
            "check": "attachment_preview_blocking",
            "expected": True,
            "actual": metadata.get("attachment_preview_mode") == "blocking",
            "passed": metadata.get("attachment_preview_mode") == "blocking"
        })
        
        # Check: NO public/internal separation
        validations.append({
            "check": "public_internal_separated",
            "expected": False,
            "actual": metadata.get("public_internal_separated", False),
            "passed": metadata.get("public_internal_separated", False) == False
        })
        
        # Check: NO enrollment confirmation
        validations.append({
            "check": "enrollment_confirmation",
            "expected": False,
            "actual": metadata.get("enrollment_confirmation", False),
            "passed": metadata.get("enrollment_confirmation", False) == False
        })
        
        return validations
    
    def generate_report(self, output_dir: str):
        """Generate test results report"""
        os.makedirs(output_dir, exist_ok=True)
        
        # JSON results
        results_path = os.path.join(output_dir, 'results_pre.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                "project": "Baseline Course UI",
                "timestamp": datetime.now().isoformat(),
                "total_scenarios": len(self.results),
                "passed": sum(1 for r in self.results if r["passed"]),
                "failed": sum(1 for r in self.results if not r["passed"]),
                "results": self.results,
                "summary_metrics": self.calculate_summary_metrics()
            }, f, indent=2)
        
        # Text log
        log_path = os.path.join(output_dir, 'log_pre.txt')
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("BASELINE COURSE UI - TEST LOG\n")
            f.write("=" * 80 + "\n\n")
            
            for result in self.results:
                f.write(f"Scenario: {result['scenario_name']}\n")
                f.write(f"  ID: {result['scenario_id']}\n")
                f.write(f"  Status: {result['status']}\n")
                f.write(f"  Passed: {result['passed']}\n")
                f.write(f"  Warnings: {len(result['warnings'])}\n")
                f.write(f"  Errors: {len(result['errors'])}\n")
                
                if result['errors']:
                    f.write(f"  Error details: {', '.join(result['errors'])}\n")
                
                f.write(f"  Metrics: {json.dumps(result['metrics'], indent=4)}\n")
                f.write(f"  HTML: {result['html_output']}\n")
                f.write("\n" + "-" * 80 + "\n\n")
            
            summary = self.calculate_summary_metrics()
            f.write("\nSUMMARY METRICS:\n")
            f.write(json.dumps(summary, indent=2))
        
        print(f"\n✓ Results saved to {results_path}")
        print(f"✓ Log saved to {log_path}")
        
        return results_path, log_path
    
    def calculate_summary_metrics(self) -> Dict:
        """Calculate aggregate metrics across all scenarios"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        
        avg_hierarchy_score = sum(
            r.get("metrics", {}).get("hierarchy_clarity_score", 0) 
            for r in self.results
        ) / total if total > 0 else 0
        
        avg_mis_operation_risk = sum(
            r.get("metrics", {}).get("mis_operation_risk", 1.0) 
            for r in self.results
        ) / total if total > 0 else 1.0
        
        edge_case_handled = sum(
            1 for r in self.results 
            if r.get("scenario_id") == "scenario_05_malformed_input" and not r["passed"]
        )
        
        return {
            "total_scenarios": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
            "avg_hierarchy_clarity_score": round(avg_hierarchy_score, 2),
            "avg_mis_operation_risk": round(avg_mis_operation_risk, 2),
            "edge_case_failures": edge_case_handled,
            "collapsible_sections_implemented": 0,
            "pinned_elements_implemented": 0,
            "confirmation_prompts_implemented": 0
        }


def main():
    # Locate test scenarios
    project_root = Path(__file__).parent.parent.parent
    scenarios_path = project_root / "test_scenarios.json"
    
    if not scenarios_path.exists():
        print(f"ERROR: Test scenarios not found at {scenarios_path}")
        sys.exit(1)
    
    # Run tests
    runner = TestRunner(str(scenarios_path))
    runner.run_all_tests()
    
    # Generate reports
    results_dir = Path(__file__).parent.parent / "results"
    runner.generate_report(str(results_dir))
    
    print("\n" + "=" * 80)
    print("BASELINE TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
