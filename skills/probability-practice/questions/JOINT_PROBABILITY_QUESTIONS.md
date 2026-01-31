### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Compute P(A ∩ B).

**Solution:**
P(A ∩ B) = {{joint_AB}}/{{total}} = {{simplified}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

What is P(A ∩ ¬B)?

**Solution:**
P(A ∩ ¬B) = {{joint_A_notB}}/{{total}} = {{simplified}}

## medium

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Verify that P(A ∩ B) = P(A) × P(B | A) using the table data.

**Solution:**
P(A) = {{marginal_A}}/{{total}}
P(B | A) = {{joint_AB}}/{{marginal_A}}

P(A) × P(B | A) = ({{marginal_A}}/{{total}}) × ({{joint_AB}}/{{marginal_A}}) = {{joint_AB}}/{{total}}

P(A ∩ B) = {{joint_AB}}/{{total}} ✓

Both equal {{simplified}}, verifying the multiplication rule.

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Compute P(¬A ∩ ¬B).

**Solution:**
P(¬A ∩ ¬B) = {{joint_notA_notB}}/{{total}} = {{simplified}}