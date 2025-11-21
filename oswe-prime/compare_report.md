# Compare Report: Baseline vs Enhanced

## Summary
### Scenario: complex_nesting
* Baseline warnings: ['possible_misoperation_cta', 'mixed_types', 'unsafe_attachment']
* Enhanced warnings: ['unsafe_attachment']
* Baseline hero_size: medium
* Enhanced has_pinned_info_card: True
* Baseline scroll_lines: 0
* Enhanced scroll reduction (lines): 0
* Baseline prototype: Project_A_BaselineCourseUI/results/baseline_complex_nesting.html
* Enhanced prototype: Project_B_EnhancedCourseUI/results/enhanced_complex_nesting.html
* Baseline clarity: N/A
* Enhanced clarity: 80

### Scenario: long_scroll_flow
* Baseline warnings: ['possible_misoperation_cta', 'long_scroll']
* Enhanced warnings: []
* Baseline hero_size: large
* Enhanced has_pinned_info_card: True
* Baseline scroll_lines: 500
* Enhanced scroll reduction (lines): 500
* Baseline prototype: Project_A_BaselineCourseUI/results/baseline_long_scroll_flow.html
* Enhanced prototype: Project_B_EnhancedCourseUI/results/enhanced_long_scroll_flow.html
* Baseline clarity: N/A
* Enhanced clarity: 80

### Scenario: malformed_input
* Baseline warnings: None
* Enhanced warnings: ['malformed_tags_fixed', 'missing_instructor']
* Baseline hero_size: None
* Enhanced has_pinned_info_card: True
* Baseline scroll_lines: None
* Enhanced scroll reduction (lines): 0
* Baseline prototype: Project_A_BaselineCourseUI/results/baseline_malformed_input.html
* Enhanced prototype: Project_B_EnhancedCourseUI/results/enhanced_malformed_input.html
* Baseline clarity: N/A
* Enhanced clarity: 90

### Scenario: mis_operation_flow
* Baseline warnings: ['possible_misoperation_cta']
* Enhanced warnings: []
* Baseline hero_size: extra-large
* Enhanced has_pinned_info_card: True
* Baseline scroll_lines: 0
* Enhanced scroll reduction (lines): 0
* Baseline prototype: Project_A_BaselineCourseUI/results/baseline_mis_operation_flow.html
* Enhanced prototype: Project_B_EnhancedCourseUI/results/enhanced_mis_operation_flow.html
* Baseline clarity: N/A
* Enhanced clarity: 80

### Scenario: normal_flow
* Baseline warnings: ['possible_misoperation_cta']
* Enhanced warnings: []
* Baseline hero_size: large
* Enhanced has_pinned_info_card: True
* Baseline scroll_lines: 0
* Enhanced scroll reduction (lines): 0
* Baseline prototype: Project_A_BaselineCourseUI/results/baseline_normal_flow.html
* Enhanced prototype: Project_B_EnhancedCourseUI/results/enhanced_normal_flow.html
* Baseline clarity: N/A
* Enhanced clarity: 80

## Pass/Fail Matrix (heuristic)
| Scenario | Baseline | Enhanced |
|---|---|---|
| complex_nesting | WARN | WARN |
| long_scroll_flow | WARN | OK |
| malformed_input | OK | WARN |
| mis_operation_flow | WARN | OK |
| normal_flow | WARN | OK |