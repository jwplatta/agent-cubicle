### Question

**Prompt:**
Given the contingency table:

{{table}}

You know B occurred. Use Bayes' rule to find P(A | B) from P(B | A), P(A), and P(B).

**Solution:**
P(B | A) = {{joint_AB}}/{{marginal_A}}
P(A) = {{marginal_A}}/{{total}}
P(B) = {{marginal_B}}/{{total}}

P(A | B) = P(B | A) × P(A) / P(B) = ({{joint_AB}}/{{marginal_A}}) × ({{marginal_A}}/{{total}}) / ({{marginal_B}}/{{total}}) = {{joint_AB}}/{{marginal_B}} = {{simplified}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Compute P(B | A) directly. Then verify using Bayes' rule: P(B | A) = P(A | B) × P(B) / P(A).

**Solution:**
Direct: P(B | A) = {{joint_AB}}/{{marginal_A}}

Bayes: P(A | B) = {{joint_AB}}/{{marginal_B}}, P(B) = {{marginal_B}}/{{total}}, P(A) = {{marginal_A}}/{{total}}
P(B | A) = ({{joint_AB}}/{{marginal_B}}) × ({{marginal_B}}/{{total}}) / ({{marginal_A}}/{{total}}) = {{joint_AB}}/{{marginal_A}} ✓

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Suppose you observe event B. Use Bayes' theorem to update your belief about A:
- Prior: P(A) = ?
- Likelihood: P(B | A) = ?
- Evidence: P(B) = ?
- Posterior: P(A | B) = ?

**Solution:**
Prior: P(A) = {{marginal_A}}/{{total}}
Likelihood: P(B | A) = {{joint_AB}}/{{marginal_A}}
Evidence: P(B) = {{marginal_B}}/{{total}}

Posterior: P(A | B) = P(B | A) × P(A) / P(B) = ({{joint_AB}}/{{marginal_A}}) × ({{marginal_A}}/{{total}}) / ({{marginal_B}}/{{total}}) = {{joint_AB}}/{{marginal_B}} = {{simplified}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Compute the odds ratio: [P(A|B) / P(¬A|B)] / [P(A|¬B) / P(¬A|¬B)]. This measures how much B affects the odds of A.

**Solution:**
P(A | B) = {{joint_AB}}/{{marginal_B}}, P(¬A | B) = {{joint_notA_B}}/{{marginal_B}}
Odds of A given B = ({{joint_AB}}/{{marginal_B}}) / ({{joint_notA_B}}/{{marginal_B}}) = {{joint_AB}}/{{joint_notA_B}}

P(A | ¬B) = {{joint_A_notB}}/{{marginal_notB}}, P(¬A | ¬B) = {{joint_notA_notB}}/{{marginal_notB}}
Odds of A given ¬B = ({{joint_A_notB}}/{{marginal_notB}}) / ({{joint_notA_notB}}/{{marginal_notB}}) = {{joint_A_notB}}/{{joint_notA_notB}}

Odds ratio = ({{joint_AB}}/{{joint_notA_B}}) / ({{joint_A_notB}}/{{joint_notA_notB}}) = ({{joint_AB}} × {{joint_notA_notB}}) / ({{joint_notA_B}} × {{joint_A_notB}}) = {{odds_ratio}}

### Question 3

**Prompt:**
Given the contingency table:

{{table}}

Show that P(A | B) > P(A) if and only if P(B | A) > P(B). Verify using the table.

**Solution:**
P(A) = {{marginal_A}}/{{total}} = {{prob_A}}
P(A | B) = {{joint_AB}}/{{marginal_B}} = {{prob_A_given_B}}
Comparison: P(A | B) {{comparison_A}} P(A)

P(B) = {{marginal_B}}/{{total}} = {{prob_B}}
P(B | A) = {{joint_AB}}/{{marginal_A}} = {{prob_B_given_A}}
Comparison: P(B | A) {{comparison_B}} P(B)

Verified: Both inequalities go in the {{direction}} direction

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Use the law of total probability to compute P(B) from P(B | A) and P(B | ¬A):
P(B) = P(B | A) × P(A) + P(B | ¬A) × P(¬A)

Then use this with Bayes' rule to find P(A | B).

**Solution:**
P(B | A) = {{joint_AB}}/{{marginal_A}}, P(A) = {{marginal_A}}/{{total}}
P(B | ¬A) = {{joint_notA_B}}/{{marginal_notA}}, P(¬A) = {{marginal_notA}}/{{total}}

P(B) = ({{joint_AB}}/{{marginal_A}}) × ({{marginal_A}}/{{total}}) + ({{joint_notA_B}}/{{marginal_notA}}) × ({{marginal_notA}}/{{total}})
     = {{joint_AB}}/{{total}} + {{joint_notA_B}}/{{total}}
     = {{marginal_B}}/{{total}} ✓

P(A | B) = P(B | A) × P(A) / P(B) = ({{joint_AB}}/{{marginal_A}}) × ({{marginal_A}}/{{total}}) / ({{marginal_B}}/{{total}}) = {{joint_AB}}/{{marginal_B}} = {{simplified}}

### Question 2

**Prompt:**
Given the contingency table:
{{table}}
A diagnostic test scenario: Let A = "disease present" and B = "test positive".

Compute:
- Sensitivity: P(B | A) (true positive rate)
- Specificity: P(¬B | ¬A) (true negative rate)
- Positive predictive value: P(A | B) (precision)
- Negative predictive value: P(¬A | ¬B)

Relate PPV to sensitivity, specificity, and prevalence using Bayes' theorem.

**Solution:**
Sensitivity (TPR): P(B | A) = {{joint_AB}}/{{marginal_A}} = {{sensitivity}}
Specificity (TNR): P(¬B | ¬A) = {{joint_notA_notB}}/{{marginal_notA}} = {{specificity}}
Prevalence: P(A) = {{marginal_A}}/{{total}} = {{prevalence}}

Positive Predictive Value: P(A | B) = {{joint_AB}}/{{marginal_B}} = {{ppv}}
Negative Predictive Value: P(¬A | ¬B) = {{joint_notA_notB}}/{{marginal_notB}} = {{npv}}

Bayes verification:
P(A | B) = P(B | A) × P(A) / P(B)
         = Sensitivity × Prevalence / [Sensitivity × Prevalence + (1 - Specificity) × (1 - Prevalence)]
         = ({{joint_AB}}/{{marginal_A}}) × ({{marginal_A}}/{{total}}) / ({{marginal_B}}/{{total}})
         = {{joint_AB}}/{{marginal_B}} ✓