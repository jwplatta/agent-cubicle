# Probability Formulas Quick Reference

A concise cheat sheet of essential probability formulas for hand calculations.

---

## Counting

| Formula | Description |
|---------|-------------|
| n! | n factorial = n × (n-1) × (n-2) × ... × 2 × 1 |
| P(n,k) = n!/(n-k)! | Permutations: arrange k items from n (order matters) |
| C(n,k) = n!/(k!(n-k)!) | Combinations: choose k items from n (order doesn't matter) |
| C(n,k) = P(n,k)/k! | Relationship between combinations and permutations |

**Special cases:**
- 0! = 1
- C(n,0) = 1
- C(n,n) = 1
- C(n,1) = n
- C(n,k) = C(n,n-k)

---

## Basic Probability Rules

| Formula | Name | Description |
|---------|------|-------------|
| 0 ≤ P(A) ≤ 1 | Range | All probabilities between 0 and 1 |
| P(S) = 1 | Certainty | Sample space has probability 1 |
| P(¬A) = 1 - P(A) | Complement | Probability of "not A" |
| P(A ∪ B) = P(A) + P(B) - P(A ∩ B) | Inclusion-Exclusion | Union of two events |
| P(A ∪ B) = P(A) + P(B) | Addition (mutually exclusive) | If A and B can't both occur |

---

## Conditional Probability

| Formula | Description |
|---------|-------------|
| P(A \| B) = P(A ∩ B) / P(B) | Conditional probability (definition) |
| P(A ∩ B) = P(A \| B) × P(B) | Multiplication rule |
| P(A ∩ B) = P(B \| A) × P(A) | Multiplication rule (reversed) |
| P(¬A \| B) = 1 - P(A \| B) | Complement within condition |

**Chain rule (3 events):**
```
P(A ∩ B ∩ C) = P(A) × P(B | A) × P(C | A ∩ B)
```

---

## Bayes' Theorem

**Basic form:**
```
P(A | B) = [P(B | A) × P(A)] / P(B)
```

**Expanded form (with complement):**
```
P(A | B) = [P(B | A) × P(A)] / [P(B | A) × P(A) + P(B | ¬A) × P(¬A)]
```

**Terms:**
- P(A): prior
- P(A | B): posterior
- P(B | A): likelihood
- P(B): evidence/marginal likelihood

---

## Law of Total Probability

If B₁, B₂, ..., Bₙ partition the sample space:
```
P(A) = P(A | B₁)P(B₁) + P(A | B₂)P(B₂) + ... + P(A | Bₙ)P(Bₙ)
```

**Two-event case:**
```
P(A) = P(A | B)P(B) + P(A | ¬B)P(¬B)
```

---

## Independence

**Definition (any of these equivalent):**
1. P(A ∩ B) = P(A) × P(B)
2. P(A | B) = P(A)
3. P(B | A) = P(B)

**Testing independence from 2×2 table:**

```
         B      ¬B    Total
A        a      b     a+b
¬A       c      d     c+d
Total   a+c    b+d     N
```

Test: **a × d = b × c** (if equal, A and B are independent)

Or equivalently: **a/N = [(a+b)/N] × [(a+c)/N]**

**Expected count under independence:**
```
E[cell] = (row total × column total) / N
```

---

## 2×2 Contingency Table Formulas

Given table:
```
         B      ¬B    Total
A        a      b     a+b
¬A       c      d     c+d
Total   a+c    b+d     N
```

### Joint Probabilities
| Event | Formula |
|-------|---------|
| P(A ∩ B) | a/N |
| P(A ∩ ¬B) | b/N |
| P(¬A ∩ B) | c/N |
| P(¬A ∩ ¬B) | d/N |

### Marginal Probabilities
| Event | Formula |
|-------|---------|
| P(A) | (a+b)/N |
| P(¬A) | (c+d)/N |
| P(B) | (a+c)/N |
| P(¬B) | (b+d)/N |

### Conditional Probabilities
| Event | Formula (definition) | Formula (direct count) |
|-------|---------------------|------------------------|
| P(A \| B) | [a/N] / [(a+c)/N] | a/(a+c) |
| P(¬A \| B) | [c/N] / [(a+c)/N] | c/(a+c) |
| P(A \| ¬B) | [b/N] / [(b+d)/N] | b/(b+d) |
| P(¬A \| ¬B) | [d/N] / [(b+d)/N] | d/(b+d) |
| P(B \| A) | [a/N] / [(a+b)/N] | a/(a+b) |
| P(¬B \| A) | [b/N] / [(a+b)/N] | b/(a+b) |
| P(B \| ¬A) | [c/N] / [(c+d)/N] | c/(c+d) |
| P(¬B \| ¬A) | [d/N] / [(c+d)/N] | d/(c+d) |

**Direct count method for P(A | B):**
1. Restrict to column B (outcomes where B occurred)
2. Count how many have A: numerator = a
3. Count total in B: denominator = a+c
4. P(A | B) = a/(a+c)

---

## Expectation

### Discrete Random Variables

| Formula | Description |
|---------|-------------|
| E[X] = Σ xᵢpᵢ | Expected value (definition) |
| E[aX + b] = aE[X] + b | Linearity with constants |
| E[X + Y] = E[X] + E[Y] | Linearity (always true, even if dependent) |
| E[XY] = E[X] × E[Y] | Product (only if X, Y independent) |
| E[indicator of A] = P(A) | Indicator variables |

### Law of Total Expectation

If B₁, B₂, ..., Bₙ partition the sample space:
```
E[X] = E[X | B₁]P(B₁) + E[X | B₂]P(B₂) + ... + E[X | Bₙ]P(Bₙ)
```

---

## Common Distributions

| Distribution | E[X] | Var(X) | Notes |
|-------------|------|--------|-------|
| Bernoulli(p) | p | p(1-p) | Single trial: 1 with prob p, 0 with prob 1-p |
| Binomial(n,p) | np | np(1-p) | n independent Bernoulli trials |
| Geometric(p) | 1/p | (1-p)/p² | Trials until first success |
| Poisson(λ) | λ | λ | Rare events, λ = rate |
| Uniform(a,b) | (a+b)/2 | (b-a)²/12 | Continuous, all values equally likely |
| Normal(μ,σ²) | μ | σ² | Bell curve |

---

## Diagnostic Testing Formulas

Given:
- Prevalence: P(D) = probability of disease
- Sensitivity: P(+ | D) = true positive rate
- Specificity: P(- | ¬D) = true negative rate
- False positive rate: P(+ | ¬D) = 1 - specificity

**Positive Predictive Value (PPV):** P(D | +)
```
P(D | +) = [P(+ | D) × P(D)] / [P(+ | D) × P(D) + P(+ | ¬D) × P(¬D)]
```

**Negative Predictive Value (NPV):** P(¬D | -)
```
P(¬D | -) = [P(- | ¬D) × P(¬D)] / [P(- | ¬D) × P(¬D) + P(- | D) × P(D)]
```

---

## Fraction Simplification

To simplify a/b:
1. Find GCD(a, b) — greatest common divisor
2. Divide both a and b by GCD
3. Result: (a/GCD) / (b/GCD)

**Example:** Simplify 12/20
- GCD(12, 20) = 4
- 12/20 = (12÷4)/(20÷4) = 3/5

**Common GCDs to recognize:**
- Even numbers: at least divisible by 2
- Multiples of 5: look for 5, 10, 15, 20
- Recognize patterns: 12/20 = 3/5, 15/25 = 3/5, etc.

---

## Quick Mental Math Tips

**Multiplying fractions:**
```
(a/b) × (c/d) = (a×c) / (b×d)
```

**Dividing fractions:**
```
(a/b) / (c/d) = (a/b) × (d/c) = (a×d) / (b×c)
```

**Adding fractions (same denominator):**
```
(a/b) + (c/b) = (a+c) / b
```

**Adding fractions (different denominators):**
```
(a/b) + (c/d) = (ad + bc) / (bd)
```

**Decimal conversions (common fractions):**
- 1/2 = 0.5
- 1/3 ≈ 0.333
- 1/4 = 0.25
- 1/5 = 0.2
- 1/6 ≈ 0.167
- 1/8 = 0.125
- 1/10 = 0.1
- 2/3 ≈ 0.667
- 3/4 = 0.75
- 3/5 = 0.6
- 4/5 = 0.8

---

## Problem-Solving Checklist

Before starting:
- [ ] Draw a table/tree/diagram
- [ ] Label what you know (given info)
- [ ] Label what you want (target)

When computing:
- [ ] Check: are events independent?
- [ ] Check: are events mutually exclusive?
- [ ] Check: does P(B) > 0 for conditional probabilities?
- [ ] Simplify fractions using GCD
- [ ] Verify answer makes sense (0 ≤ P ≤ 1)

Common formulas to try:
- [ ] Complement rule: P(¬A) = 1 - P(A)
- [ ] Conditional: P(A | B) = P(A ∩ B) / P(B)
- [ ] Multiplication: P(A ∩ B) = P(A | B) × P(B)
- [ ] Bayes: P(A | B) = [P(B | A) × P(A)] / P(B)
- [ ] Law of total probability: P(A) = Σ P(A | Bᵢ)P(Bᵢ)
- [ ] Linearity of expectation: E[X + Y] = E[X] + E[Y]
