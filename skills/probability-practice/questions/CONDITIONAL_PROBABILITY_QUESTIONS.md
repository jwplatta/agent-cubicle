# conditional

## easy

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Compute P(A | B).

**Solution:**
P(A | B) = P(A ∩ B) / P(B) = ({{joint_AB}}/{{total}}) / ({{marginal_B}}/{{total}}) = {{joint_AB}}/{{marginal_B}} = {{simplified}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Compute P(B | A).

**Solution:**
P(B | A) = P(A ∩ B) / P(A) = ({{joint_AB}}/{{total}}) / ({{marginal_A}}/{{total}}) = {{joint_AB}}/{{marginal_A}} = {{simplified}}

### Question 3

**Prompt:**
Given the contingency table:

{{table}}

What is the probability of A given that B occurred?

**Solution:**
P(A | B) = {{joint_AB}}/{{marginal_B}} = {{simplified}}

### Question 4

**Prompt:**
Given the contingency table:

{{table}}

Find P(¬A | B).

**Solution:**
P(¬A | B) = P(¬A ∩ B) / P(B) = ({{joint_notA_B}}/{{total}}) / ({{marginal_B}}/{{total}}) = {{joint_notA_B}}/{{marginal_B}} = {{simplified}}

## medium

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Compute both P(A | B) and P(B | A). Are they equal?

**Solution:**
P(A | B) = {{joint_AB}}/{{marginal_B}} = {{prob_A_given_B}}
P(B | A) = {{joint_AB}}/{{marginal_A}} = {{prob_B_given_A}}
{{comparison}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Verify that P(A | B) + P(¬A | B) = 1.

**Solution:**
P(A | B) = {{joint_AB}}/{{marginal_B}}
P(¬A | B) = {{joint_notA_B}}/{{marginal_B}}
Sum = {{joint_AB}}/{{marginal_B}} + {{joint_notA_B}}/{{marginal_B}} = {{marginal_B}}/{{marginal_B}} = 1 ✓

### Question 3

**Prompt:**
Given the contingency table:

{{table}}

Compute P(A | B) and P(A | ¬B). Which conditioning event makes A more likely?

**Solution:**
P(A | B) = {{joint_AB}}/{{marginal_B}} = {{prob_A_given_B}}
P(A | ¬B) = {{joint_A_notB}}/{{marginal_notB}} = {{prob_A_given_notB}}
{{comparison}}

### Question 4

**Prompt:**
Given the contingency table:

{{table}}

Use the definition P(A | B) = P(A ∩ B) / P(B) to find P(A | B), then verify by directly counting in the table.

**Solution:**
Formula: P(A | B) = P(A ∩ B) / P(B) = ({{joint_AB}}/{{total}}) / ({{marginal_B}}/{{total}}) = {{joint_AB}}/{{marginal_B}}
Direct count: In column B ({{marginal_B}} outcomes), {{joint_AB}} have A, so P(A|B) = {{joint_AB}}/{{marginal_B}} ✓

## hard

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Compute all four conditional probabilities: P(A|B), P(¬A|B), P(A|¬B), P(¬A|¬B). Verify that P(A|B) + P(¬A|B) = 1 and P(A|¬B) + P(¬A|¬B) = 1.

**Solution:**
P(A | B) = {{joint_AB}}/{{marginal_B}}
P(¬A | B) = {{joint_notA_B}}/{{marginal_B}}
P(A | ¬B) = {{joint_A_notB}}/{{marginal_notB}}
P(¬A | ¬B) = {{joint_notA_notB}}/{{marginal_notB}}

Verify: P(A|B) + P(¬A|B) = {{joint_AB}}/{{marginal_B}} + {{joint_notA_B}}/{{marginal_B}} = 1 ✓
Verify: P(A|¬B) + P(¬A|¬B) = {{joint_A_notB}}/{{marginal_notB}} + {{joint_notA_notB}}/{{marginal_notB}} = 1 ✓

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Show that P(A ∩ B) = P(A | B) × P(B) using the table data. Then verify the same using P(A ∩ B) = P(B | A) × P(A).

**Solution:**
Method 1: P(A ∩ B) = P(A | B) × P(B) = ({{joint_AB}}/{{marginal_B}}) × ({{marginal_B}}/{{total}}) = {{joint_AB}}/{{total}} ✓

Method 2: P(A ∩ B) = P(B | A) × P(A) = ({{joint_AB}}/{{marginal_A}}) × ({{marginal_A}}/{{total}}) = {{joint_AB}}/{{total}} ✓

