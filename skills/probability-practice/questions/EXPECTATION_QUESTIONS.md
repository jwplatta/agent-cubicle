### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Let X be an indicator variable for event A (X=1 if A occurs, X=0 otherwise). Compute E[X].

**Solution:**
X = 1 with probability P(A) = {{marginal_A}}/{{total}}
X = 0 with probability P(¬A) = {{marginal_notA}}/{{total}}

E[X] = 1 × P(A) + 0 × P(¬A) = P(A) = {{marginal_A}}/{{total}} = {{simplified}}

Key insight: The expected value of an indicator variable equals the probability of the event.

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

Let Y be a random variable that equals 10 if B occurs and 0 otherwise. Compute E[Y].

**Solution:**
Y = 10 with probability P(B) = {{marginal_B}}/{{total}}
Y = 0 with probability P(¬B) = {{marginal_notB}}/{{total}}

E[Y] = 10 × ({{marginal_B}}/{{total}}) + 0 × ({{marginal_notB}}/{{total}}) = 10 × {{marginal_B}}/{{total}} = {{expectation_result}}

### Question 3

**Prompt:**
Given the contingency table:

{{table}}

Let X and Y be indicator variables for events A and B respectively. Compute E[X + Y] using linearity of expectation.

**Solution:**
E[X] = P(A) = {{marginal_A}}/{{total}}
E[Y] = P(B) = {{marginal_B}}/{{total}}

By linearity of expectation:
E[X + Y] = E[X] + E[Y] = {{marginal_A}}/{{total}} + {{marginal_B}}/{{total}} = {{expectation_sum}}/{{total}}

### Question 4

**Prompt:**
Given the contingency table:

{{table}}

Define a random variable Z that takes value 100 if both A and B occur, 50 if exactly one occurs, and 0 if neither occurs. Compute E[Z].

**Solution:**
P(Z = 100) = P(A ∩ B) = {{joint_AB}}/{{total}}
P(Z = 50) = P(A ∩ ¬B) + P(¬A ∩ B) = {{joint_A_notB}}/{{total}} + {{joint_notA_B}}/{{total}} = {{exactly_one}}/{{total}}
P(Z = 0) = P(¬A ∩ ¬B) = {{joint_notA_notB}}/{{total}}

E[Z] = 100 × ({{joint_AB}}/{{total}}) + 50 × ({{exactly_one}}/{{total}}) + 0 × ({{joint_notA_notB}}/{{total}})
     = {{ez_term1}}/{{total}} + {{ez_term2}}/{{total}}
     = {{expectation_z}}/{{total}}