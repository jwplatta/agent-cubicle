### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Compute P(A).

**Solution:**
P(A) = {{marginal_A}}/{{total}} = {{simplified}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Compute P(B).

**Solution:**
P(B) = {{marginal_B}}/{{total}} = {{simplified}}

### Question 3

**Prompt:**
Given the contingency table:

{{table}}

What is the probability of event A?

**Solution:**
P(A) = {{marginal_A}}/{{total}} = {{simplified}}

### Question 4

**Prompt:**
Given the contingency table:

{{table}}

Find P(¬A).

**Solution:**
P(¬A) = {{marginal_notA}}/{{total}} = {{simplified}}

## medium

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Compute both P(A) and P(B). Are they equal?

**Solution:**
P(A) = {{marginal_A}}/{{total}} = {{prob_A}}
P(B) = {{marginal_B}}/{{total}} = {{prob_B}}
{{comparison}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Verify that P(A) + P(¬A) = 1.

**Solution:**
P(A) = {{marginal_A}}/{{total}}
P(¬A) = {{marginal_notA}}/{{total}}
Sum = {{marginal_A}}/{{total}} + {{marginal_notA}}/{{total}} = {{total}}/{{total}} = 1 ✓

### Question 3

**Prompt:**
Given the contingency table:

{{table}}

Compute P(A ∪ B) using the formula P(A ∪ B) = P(A) + P(B) - P(A ∩ B).

**Solution:**
P(A) = {{marginal_A}}/{{total}}
P(B) = {{marginal_B}}/{{total}}
P(A ∩ B) = {{joint_AB}}/{{total}}
P(A ∪ B) = {{marginal_A}}/{{total}} + {{marginal_B}}/{{total}} - {{joint_AB}}/{{total}} = {{union_count}}/{{total}} = {{simplified}}

### Question 4

**Prompt:**
Given the contingency table:

{{table}}

What fraction of all outcomes are in the cell (A ∩ B)?

**Solution:**
P(A ∩ B) = {{joint_AB}}/{{total}} = {{simplified}}

## hard

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Compute all four joint probabilities: P(A ∩ B), P(A ∩ ¬B), P(¬A ∩ B), P(¬A ∩ ¬B). Verify they sum to 1.

**Solution:**
P(A ∩ B) = {{joint_AB}}/{{total}}
P(A ∩ ¬B) = {{joint_A_notB}}/{{total}}
P(¬A ∩ B) = {{joint_notA_B}}/{{total}}
P(¬A ∩ ¬B) = {{joint_notA_notB}}/{{total}}
Sum = ({{joint_AB}} + {{joint_A_notB}} + {{joint_notA_B}} + {{joint_notA_notB}})/{{total}} = {{total}}/{{total}} = 1 ✓

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Show that P(A ∪ B) = (number of outcomes with A or B or both) / total. Then verify using the inclusion-exclusion formula.

**Solution:**
Count method: Outcomes with A or B = {{union_count}}, so P(A ∪ B) = {{union_count}}/{{total}}

Formula method: P(A ∪ B) = P(A) + P(B) - P(A ∩ B) = {{marginal_A}}/{{total}} + {{marginal_B}}/{{total}} - {{joint_AB}}/{{total}} = {{union_count}}/{{total}} ✓

### Question 3

**Prompt:**
Given the contingency table:

{{table}}

Express each marginal probability P(A), P(¬A), P(B), P(¬B) as a sum of joint probabilities. Verify the law of total probability holds.

**Solution:**
P(A) = P(A ∩ B) + P(A ∩ ¬B) = {{joint_AB}}/{{total}} + {{joint_A_notB}}/{{total}} = {{marginal_A}}/{{total}} ✓
P(¬A) = P(¬A ∩ B) + P(¬A ∩ ¬B) = {{joint_notA_B}}/{{total}} + {{joint_notA_notB}}/{{total}} = {{marginal_notA}}/{{total}} ✓
P(B) = P(A ∩ B) + P(¬A ∩ B) = {{joint_AB}}/{{total}} + {{joint_notA_B}}/{{total}} = {{marginal_B}}/{{total}} ✓
P(¬B) = P(A ∩ ¬B) + P(¬A ∩ ¬B) = {{joint_A_notB}}/{{total}} + {{joint_notA_notB}}/{{total}} = {{marginal_notB}}/{{total}} ✓