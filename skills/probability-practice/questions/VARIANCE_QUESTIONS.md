### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Let X be an indicator variable for event A. Compute Var(X) using the formula Var(X) = E[X²] - (E[X])².

**Solution:**
For an indicator variable X:
E[X] = P(A) = {{marginal_A}}/{{total}}
E[X²] = 1² × P(A) + 0² × P(¬A) = P(A) = {{marginal_A}}/{{total}}

Var(X) = E[X²] - (E[X])² = {{marginal_A}}/{{total}} - ({{marginal_A}}/{{total}})² = {{variance_result}}

For Bernoulli(p): Var(X) = p(1-p) = ({{marginal_A}}/{{total}}) × ({{marginal_notA}}/{{total}}) = {{variance_result}}

## medium

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Define X as an indicator for A and Y as an indicator for B. If X and Y were independent, what would Var(X + Y) equal?

**Solution:**
Var(X) = P(A) × P(¬A) = ({{marginal_A}}/{{total}}) × ({{marginal_notA}}/{{total}}) = {{var_x}}
Var(Y) = P(B) × P(¬B) = ({{marginal_B}}/{{total}}) × ({{marginal_notB}}/{{total}}) = {{var_y}}

If X and Y are independent:
Var(X + Y) = Var(X) + Var(Y) = {{var_x}} + {{var_y}} = {{var_sum}}