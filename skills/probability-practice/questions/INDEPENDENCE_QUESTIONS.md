### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Check if A and B are independent by testing if P(A ∩ B) = P(A) × P(B).

**Solution:**
P(A) = {{marginal_A}}/{{total}}
P(B) = {{marginal_B}}/{{total}}
P(A) × P(B) = ({{marginal_A}}/{{total}}) × ({{marginal_B}}/{{total}}) = {{product_num}}/{{total_squared}}

P(A ∩ B) = {{joint_AB}}/{{total}}

{{independence_conclusion}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Check if A and B are independent by testing if P(A | B) = P(A).

**Solution:**
P(A) = {{marginal_A}}/{{total}} = {{prob_A}}
P(A | B) = {{joint_AB}}/{{marginal_B}} = {{prob_A_given_B}}

{{independence_conclusion}}

### Question 3

**Prompt:**
Given the contingency table:

{{table}}

Compute the chi-squared statistic: χ² = Σ (observed - expected)² / expected for all four cells, where expected = (row total × column total) / grand total.

**Solution:**
Expected counts under independence:
E(A ∩ B) = {{marginal_A}} × {{marginal_B}} / {{total}} = {{exp_AB}}
E(A ∩ ¬B) = {{marginal_A}} × {{marginal_notB}} / {{total}} = {{exp_A_notB}}
E(¬A ∩ B) = {{marginal_notA}} × {{marginal_B}} / {{total}} = {{exp_notA_B}}
E(¬A ∩ ¬B) = {{marginal_notA}} × {{marginal_notB}} / {{total}} = {{exp_notA_notB}}

χ² = ({{joint_AB}} - {{exp_AB}})² / {{exp_AB}} + ({{joint_A_notB}} - {{exp_A_notB}})² / {{exp_A_notB}} + ({{joint_notA_B}} - {{exp_notA_B}})² / {{exp_notA_B}} + ({{joint_notA_notB}} - {{exp_notA_notB}})² / {{exp_notA_notB}}
   = {{chi_squared}}

{{independence_interpretation}}

## hard

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Verify all three equivalent definitions of independence:
1. P(A ∩ B) = P(A) × P(B)
2. P(A | B) = P(A)
3. P(B | A) = P(B)

If any one fails, all three should fail.

**Solution:**
Test 1: P(A ∩ B) ?= P(A) × P(B)
  {{joint_AB}}/{{total}} ?= ({{marginal_A}}/{{total}}) × ({{marginal_B}}/{{total}})
  {{joint_AB}}/{{total}} ?= {{product_num}}/{{total_squared}}
  {{test1_result}}

Test 2: P(A | B) ?= P(A)
  {{joint_AB}}/{{marginal_B}} ?= {{marginal_A}}/{{total}}
  {{test2_result}}

Test 3: P(B | A) ?= P(B)
  {{joint_AB}}/{{marginal_A}} ?= {{marginal_B}}/{{total}}
  {{test3_result}}

{{independence_conclusion}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Assume A and B were independent. Compute what the cell counts would be. Compare to actual counts to measure departure from independence.

**Solution:**
Under independence, expected counts:
E(A ∩ B) = {{marginal_A}} × {{marginal_B}} / {{total}} = {{exp_AB}}
E(A ∩ ¬B) = {{marginal_A}} × {{marginal_notB}} / {{total}} = {{exp_A_notB}}
E(¬A ∩ B) = {{marginal_notA}} × {{marginal_B}} / {{total}} = {{exp_notA_B}}
E(¬A ∩ ¬B) = {{marginal_notA}} × {{marginal_notB}} / {{total}} = {{exp_notA_notB}}

Actual counts:
{{joint_AB}}, {{joint_A_notB}}, {{joint_notA_B}}, {{joint_notA_notB}}

Differences:
Δ(A ∩ B) = {{joint_AB}} - {{exp_AB}} = {{diff_AB}}
Δ(A ∩ ¬B) = {{joint_A_notB}} - {{exp_A_notB}} = {{diff_A_notB}}
Δ(¬A ∩ B) = {{joint_notA_B}} - {{exp_notA_B}} = {{diff_notA_B}}
Δ(¬A ∩ ¬B) = {{joint_notA_notB}} - {{exp_notA_notB}} = {{diff_notA_notB}}

{{independence_interpretation}}