# Comparison Report

## Pass/Fail Matrix
| Scenario | Baseline | Enhanced |
| --- | --- | --- |
| complex_nesting | ok | ok |
| long_scroll_flow | ok | ok |
| malformed_input | ok | degraded |
| mis_operation_flow | ok | ok |
| normal_flow | ok | ok |

## Hierarchy & Scroll Improvements
- Average hierarchy clarity gain: 51.3
- Average scroll-length reduction: 532.0 px
- Average mis-operation risk reduction: 43.0
- Average edge-case coverage delta: 31.52 pts

## Attachment Preview & Interaction Safety
- Baseline preview mode: overlay (blocking); Enhanced: side-panel with inline fallback.
- Confirmation prompts added for enrollment/payment plus sticky mobile CTA.

## Prototype References
- complex_nesting: baseline -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_A_BaselineCourseUI/prototypes/baseline_layout_complex_nesting.html, enhanced -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_B_EnhancedCourseUI/prototypes/enhanced_layout_complex_nesting.html
- long_scroll_flow: baseline -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_A_BaselineCourseUI/prototypes/baseline_layout_long_scroll_flow.html, enhanced -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_B_EnhancedCourseUI/prototypes/enhanced_layout_long_scroll_flow.html
- malformed_input: baseline -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_A_BaselineCourseUI/prototypes/baseline_layout_malformed_input.html, enhanced -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_B_EnhancedCourseUI/prototypes/enhanced_layout_malformed_input.html
- mis_operation_flow: baseline -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_A_BaselineCourseUI/prototypes/baseline_layout_mis_operation_flow.html, enhanced -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_B_EnhancedCourseUI/prototypes/enhanced_layout_mis_operation_flow.html
- normal_flow: baseline -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_A_BaselineCourseUI/prototypes/baseline_layout_normal_flow.html, enhanced -> /mnt/e/acv_data/bug_bash/2025_11_21/case_2/codex/v-kaelincai_25_11_21_case2/Project_B_EnhancedCourseUI/prototypes/enhanced_layout_normal_flow.html

## Summaries
- Baseline pass rate: 5/5
- Enhanced pass rate: 5/5
- Baseline avg hierarchy clarity: 31.4
- Enhanced avg hierarchy clarity: 82.7
- Baseline avg scroll length: 1836
- Enhanced avg scroll length: 1304