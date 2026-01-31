# Question 1

**Prompt:**
Given the contingency table:

{{table}}

Use the law of total probability to compute P(B) from P(B | A) and P(B | ¬A):

P(B) = P(B | A) × P(A) + P(B | ¬A) × P(¬A)

**Solution:**
P(B | A) = {{joint_AB}}/{{marginal_A}}
P(A) = {{marginal_A}}/{{total}}
P(B | ¬A) = {{joint_notA_B}}/{{marginal_notA}}
P(¬A) = {{marginal_notA}}/{{total}}

P(B) = ({{joint_AB}}/{{marginal_A}}) × ({{marginal_A}}/{{total}}) + ({{joint_notA_B}}/{{marginal_notA}}) × ({{marginal_notA}}/{{total}})
     = {{joint_AB}}/{{total}} + {{joint_notA_B}}/{{total}}
     = {{marginal_B}}/{{total}}

Verify: From the table, P(B) = {{marginal_B}}/{{total}} ✓

# Question 2

**Prompt:**
Given the contingency table:

{{table}}

Express P(A) using the law of total probability by partitioning on B:

P(A) = P(A | B) × P(B) + P(A | ¬B) × P(¬B)

**Solution:**
P(A | B) = {{joint_AB}}/{{marginal_B}}
P(B) = {{marginal_B}}/{{total}}
P(A | ¬B) = {{joint_A_notB}}/{{marginal_notB}}
P(¬B) = {{marginal_notB}}/{{total}}

P(A) = ({{joint_AB}}/{{marginal_B}}) × ({{marginal_B}}/{{total}}) + ({{joint_A_notB}}/{{marginal_notB}}) × ({{marginal_notB}}/{{total}})
     = {{joint_AB}}/{{total}} + {{joint_A_notB}}/{{total}}
     = {{marginal_A}}/{{total}}

Verify: From the table, P(A) = {{marginal_A}}/{{total}} ✓

