"""
Test runner for Enhanced Course UI
Loads scenarios, executes transformation, validates improvements, generates reports
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from enhanced_ui import EnhancedCourseUI


class TestRunner:
    def __init__(self, scenarios_path: str):
        with open(scenarios_path, 'r', encoding='utf-8') as f:
            self.scenarios_data = json.load(f)
        
        self.results = []
        self.ui_processor = EnhancedCourseUI()
        
    def run_all_tests(self):
        """Execute all test scenarios"""
        print("=" * 80)
        print("ENHANCED COURSE UI - TEST EXECUTION")
        print("=" * 80)
        
        for scenario in self.scenarios_data["scenarios"]:
            print(f"\n[TEST] {scenario['name']} ({scenario['id']})")
            result = self.run_scenario(scenario)
            self.results.append(result)
            
            status_symbol = "✓" if result["passed"] else "✗"
            print(f"  {status_symbol} Status: {result['status']}")
            print(f"  Improvements: {', '.join(result.get('improvements', []))}")
            print(f"  Warnings: {len(result['warnings'])}")
            print(f"  Edge cases handled: {len(result.get('edge_case_flags', []))}")
        
        return self.results
    
    def run_scenario(self, scenario: Dict) -> Dict:
        """Execute a single test scenario"""
        scenario_id = scenario["id"]
        input_data = scenario["input"]
        expected_enhanced = scenario["expected_behavior"]["enhanced"]
        
        # Transform the course data
        transform_result = self.ui_processor.transform(input_data)
        
        # Validate against expected enhanced behavior
        validations = self.validate_behavior(transform_result, expected_enhanced, scenario)
        
        # Identify improvements
        improvements = self.identify_improvements(transform_result, scenario)
        
        # Generate HTML prototype
        html_output_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'results', 
            f'{scenario_id}_enhanced_layout.html'
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
            "improvements": improvements,
            "warnings": transform_result.get("warnings", []),
            "errors": transform_result.get("errors", []),
            "edge_case_flags": transform_result.get("edge_case_flags", []),
            "metrics": transform_result.get("metrics", {}),
            "html_output": html_output_path,
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_behavior(self, result: Dict, expected: Dict, scenario: Dict) -> List[Dict]:
        """Validate transformation against expected enhanced behavior"""
        validations = []
        
        if result["status"] not in ["success", "recovered"]:
            return validations
        
        layout = result.get("layout", {})
        metadata = layout.get("metadata", {})
        
        # Check: info card IS pinned
        validations.append({
            "check": "info_card_pinned",
            "expected": True,
            "actual": metadata.get("info_card_pinned", False),
            "passed": metadata.get("info_card_pinned", False) == True
        })
        
        # Check: sections ARE collapsible
        validations.append({
            "check": "sections_collapsible",
            "expected": True,
            "actual": metadata.get("sections_collapsible", False),
            "passed": metadata.get("sections_collapsible", False) == True
        })
        
        # Check: NON-blocking attachment preview
        validations.append({
            "check": "attachment_preview_non_blocking",
            "expected": "side_panel",
            "actual": metadata.get("attachment_preview_mode"),
            "passed": metadata.get("attachment_preview_mode") == "side_panel"
        })
        
        # Check: public/internal separation
        validations.append({
            "check": "public_internal_separated",
            "expected": True,
            "actual": metadata.get("public_internal_separated", False),
            "passed": metadata.get("public_internal_separated", False) == True
        })
        
        # Check: enrollment confirmation
        validations.append({
            "check": "enrollment_confirmation",
            "expected": True,
            "actual": metadata.get("enrollment_confirmation", False),
            "passed": metadata.get("enrollment_confirmation", False) == True
        })
        
        # Check: mobile optimization
        validations.append({
            "check": "mobile_optimized",
            "expected": True,
            "actual": metadata.get("mobile_optimized", False),
            "passed": metadata.get("mobile_optimized", False) == True
        })
        
        return validations
    
    def identify_improvements(self, result: Dict, scenario: Dict) -> List[str]:
        """Identify specific improvements made"""
        improvements = []
        
        if result["status"] not in ["success", "recovered"]:
            return improvements
        
        metrics = result.get("metrics", {})
        layout = result.get("layout", {})
        metadata = layout.get("metadata", {})
        
        # Hero optimization
        if metrics.get("hero_reduction_percent", 0) > 0:
            improvements.append(f"hero_reduced_{metrics['hero_reduction_percent']:.0f}%")
        
        # Collapsible sections
        collapsible_count = metrics.get("collapsible_sections", 0)
        if collapsible_count > 0:
            improvements.append(f"{collapsible_count}_collapsible_sections")
        
        # Pinned elements
        pinned_count = metrics.get("pinned_elements", 0)
        if pinned_count > 0:
            improvements.append(f"{pinned_count}_pinned_elements")
        
        # Scroll reduction
        scroll_reduction = metrics.get("scroll_reduction_percent", 0)
        if scroll_reduction > 0:
            improvements.append(f"scroll_reduced_{scroll_reduction:.0f}%")
        
        # Hierarchy improvement
        hierarchy_score = metrics.get("hierarchy_clarity_score", 0)
        if hierarchy_score > 0.5:
            improvements.append("hierarchy_clarity_improved")
        
        # Mis-operation prevention
        mis_op_reduction = metrics.get("mis_operation_risk_reduction", 0)
        if mis_op_reduction > 0:
            improvements.append(f"mis_operation_risk_reduced_{int(mis_op_reduction*100)}%")
        
        # Edge case handling
        edge_score = metrics.get("edge_case_handling_score", 0)
        if edge_score >= 0.8:
            improvements.append("robust_edge_case_handling")
        
        # Safety features
        if metadata.get("public_internal_separated"):
            improvements.append("content_separation")
        
        if metadata.get("enrollment_confirmation"):
            improvements.append("confirmation_prompts")
        
        return improvements
    
    def generate_report(self, output_dir: str):
        """Generate test results report"""
        os.makedirs(output_dir, exist_ok=True)
        
        # JSON results
        results_path = os.path.join(output_dir, 'results_post.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                "project": "Enhanced Course UI",
                "timestamp": datetime.now().isoformat(),
                "total_scenarios": len(self.results),
                "passed": sum(1 for r in self.results if r["passed"]),
                "failed": sum(1 for r in self.results if not r["passed"]),
                "results": self.results,
                "summary_metrics": self.calculate_summary_metrics(),
                "improvements_summary": self.calculate_improvements_summary()
            }, f, indent=2)
        
        # Text log
        log_path = os.path.join(output_dir, 'log_post.txt')
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("ENHANCED COURSE UI - TEST LOG\n")
            f.write("=" * 80 + "\n\n")
            
            for result in self.results:
                f.write(f"Scenario: {result['scenario_name']}\n")
                f.write(f"  ID: {result['scenario_id']}\n")
                f.write(f"  Status: {result['status']}\n")
                f.write(f"  Passed: {result['passed']}\n")
                f.write(f"  Improvements: {', '.join(result.get('improvements', []))}\n")
                f.write(f"  Edge cases handled: {len(result.get('edge_case_flags', []))}\n")
                
                if result.get('edge_case_flags'):
                    f.write(f"  Edge case flags: {', '.join(result['edge_case_flags'])}\n")
                
                f.write(f"  Metrics: {json.dumps(result['metrics'], indent=4)}\n")
                f.write(f"  HTML: {result['html_output']}\n")
                f.write("\n" + "-" * 80 + "\n\n")
            
            summary = self.calculate_summary_metrics()
            f.write("\nSUMMARY METRICS:\n")
            f.write(json.dumps(summary, indent=2))
            
            improvements = self.calculate_improvements_summary()
            f.write("\n\nIMPROVEMENTS SUMMARY:\n")
            f.write(json.dumps(improvements, indent=2))
        
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
        
        avg_scroll_reduction = sum(
            r.get("metrics", {}).get("scroll_reduction_percent", 0) 
            for r in self.results
        ) / total if total > 0 else 0
        
        avg_edge_case_score = sum(
            r.get("metrics", {}).get("edge_case_handling_score", 0) 
            for r in self.results
        ) / total if total > 0 else 0
        
        total_edge_cases_handled = sum(
            len(r.get("edge_case_flags", [])) 
            for r in self.results
        )
        
        return {
            "total_scenarios": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
            "avg_hierarchy_clarity_score": round(avg_hierarchy_score, 2),
            "avg_mis_operation_risk": round(avg_mis_operation_risk, 2),
            "avg_scroll_reduction_percent": round(avg_scroll_reduction, 1),
            "avg_edge_case_handling_score": round(avg_edge_case_score, 2),
            "total_edge_cases_handled": total_edge_cases_handled,
            "collapsible_sections_avg": round(sum(
                r.get("metrics", {}).get("collapsible_sections", 0) 
                for r in self.results
            ) / total if total > 0 else 0, 1),
            "pinned_elements_avg": round(sum(
                r.get("metrics", {}).get("pinned_elements", 0) 
                for r in self.results
            ) / total if total > 0 else 0, 1)
        }
    
    def calculate_improvements_summary(self) -> Dict:
        """Calculate improvements summary"""
        all_improvements = []
        for result in self.results:
            all_improvements.extend(result.get("improvements", []))
        
        improvement_counts = {}
        for imp in all_improvements:
            improvement_counts[imp] = improvement_counts.get(imp, 0) + 1
        
        return {
            "total_improvements": len(all_improvements),
            "unique_improvement_types": len(improvement_counts),
            "improvement_breakdown": improvement_counts,
            "most_common_improvements": sorted(
                improvement_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
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
    print("ENHANCED TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
