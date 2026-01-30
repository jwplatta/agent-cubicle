# Probability and Statistics Reference

This document covers core probability concepts needed for quantitative practice, with focus on hand-solvable problems using exact arithmetic.

---

## Table of Contents

1. [Counting Principles](#counting-principles)
2. [Joint Probability](#joint-probability)
3. [Marginal Probability](#marginal-probability)
4. [Conditional Probability](#conditional-probability)
5. [Bayes' Theorem](#bayes-theorem)
6. [Independence](#independence)
7. [Expectation](#expectation)

---

## Counting Principles

Counting is foundational to discrete probability. Two key concepts:

### Permutations

**Definition:** The number of ways to arrange n distinct objects in order.

**Formula:** P(n, k) = n!/(n-k)!

- **n! (n factorial)** = n × (n-1) × (n-2) × ... × 2 × 1
- **P(n, k)**: number of ways to choose and arrange k objects from n objects
- **P(n, n)** = n!: number of ways to arrange all n objects

**Examples:**
- How many ways to arrange 5 books on a shelf? 5! = 120
- How many 3-letter words from 5 letters (no repeats)? P(5,3) = 5×4×3 = 60
- How many ways to assign gold/silver/bronze to 8 runners? P(8,3) = 8×7×6 = 336

**Key insight:** Order matters! ABC ≠ BAC ≠ CAB

### Combinations

**Definition:** The number of ways to choose k objects from n objects (order doesn't matter).

**Formula:** C(n, k) = n! / (k! × (n-k)!)

Also written as (n choose k) or ⁿCₖ.

**Examples:**
- How many ways to choose 3 students from 10? C(10,3) = 120
- How many 5-card poker hands from 52 cards? C(52,5) = 2,598,960
- How many ways to form a committee of 4 from 12 people? C(12,4) = 495

**Key insight:** Order doesn't matter! {A,B,C} = {B,A,C} = {C,A,B}

**Relationship:** C(n,k) = P(n,k) / k!

Why? Permutations count all orderings, but combinations don't care about order, so we divide by k! (the number of ways to arrange k objects).

**Common formulas:**
- C(n, 0) = 1 (one way to choose nothing)
- C(n, 1) = n (n ways to choose one thing)
- C(n, n) = 1 (one way to choose everything)
- C(n, k) = C(n, n-k) (symmetry)

---

## Joint Probability

**Definition:** The probability that two or more events occur simultaneously.

**Notation:** P(A ∩ B) or P(A, B) — "probability of A and B"

### 2×2 Contingency Tables

A powerful tool for computing joint probabilities:

```
         B      ¬B    Total
A        a      b     a+b
¬A       c      d     c+d
Total   a+c    b+d     N
```

**Joint probabilities:**
- P(A ∩ B) = a/N
- P(A ∩ ¬B) = b/N
- P(¬A ∩ B) = c/N
- P(¬A ∩ ¬B) = d/N

**Key property:** All four joint probabilities sum to 1:
```
P(A ∩ B) + P(A ∩ ¬B) + P(¬A ∩ B) + P(¬A ∩ ¬B) = 1
```

### Multiplication Rule

For any two events A and B:
```
P(A ∩ B) = P(A | B) × P(B) = P(B | A) × P(A)
```

This is true whether A and B are independent or not.

**For independent events:**
```
P(A ∩ B) = P(A) × P(B)
```

---

## Marginal Probability

**Definition:** The probability of an event regardless of other events.

**How to compute from joint distribution:**

Sum over all values of the other variable(s).

**From a 2×2 table:**
```
         B      ¬B    Total
A        a      b     a+b
¬A       c      d     c+d
Total   a+c    b+d     N
```

**Marginal probabilities:**
- P(A) = (a + b)/N (sum row A)
- P(¬A) = (c + d)/N (sum row ¬A)
- P(B) = (a + c)/N (sum column B)
- P(¬B) = (b + d)/N (sum column ¬B)

**Complement rule:**
```
P(¬A) = 1 - P(A)
P(¬B) = 1 - P(B)
```

### Law of Total Probability

If B₁, B₂, ..., Bₙ partition the sample space (mutually exclusive and exhaustive):
```
P(A) = P(A | B₁)P(B₁) + P(A | B₂)P(B₂) + ... + P(A | Bₙ)P(Bₙ)
```

**For two events:**
```
P(A) = P(A | B)P(B) + P(A | ¬B)P(¬B)
```

This says: "To get the overall probability of A, weight each conditional probability by how likely that condition is."

**Example use:** Computing P(positive test) when you know:
- P(positive | disease) = 0.95 (sensitivity)
- P(positive | no disease) = 0.05 (false positive rate)
- P(disease) = 0.01 (base rate)

Then:
```
P(positive) = P(positive | disease) × P(disease)
            + P(positive | no disease) × P(no disease)
            = 0.95 × 0.01 + 0.05 × 0.99
            = 0.0095 + 0.0495
            = 0.059
```

---

## Conditional Probability

**Definition:** The probability of event A given that event B has occurred.

**Notation:** P(A | B) — read "probability of A given B"

**Formula:**
```
P(A | B) = P(A ∩ B) / P(B)    (provided P(B) > 0)
```

### Intuition

When you know B occurred, you restrict your sample space to only outcomes where B is true.

**Direct counting method from 2×2 table:**
```
         B      ¬B    Total
A        a      b     a+b
¬A       c      d     c+d
Total   a+c    b+d     N
```

To find P(A | B):
1. Restrict attention to column B only (total: a+c)
2. Count how many of those have A (count: a)
3. P(A | B) = a / (a+c)

### Properties

**Complement:**
```
P(¬A | B) = 1 - P(A | B)
```

**Multiplication rule (rearranged):**
```
P(A ∩ B) = P(A | B) × P(B) = P(B | A) × P(A)
```

**Chain rule (multiple events):**
```
P(A ∩ B ∩ C) = P(A) × P(B | A) × P(C | A ∩ B)
```

### Common Pitfall

⚠️ **P(A | B) ≠ P(B | A)** in general!

Example:
- P(fever | flu) = high (most flu cases have fever)
- P(flu | fever) = low (many conditions cause fever)

The order matters. Bayes' theorem tells us how to reverse the conditioning.

---

## Bayes' Theorem

**Statement:** A formula for reversing conditional probabilities.

**Formula:**
```
P(A | B) = [P(B | A) × P(A)] / P(B)
```

**Expanded form (using law of total probability):**
```
P(A | B) = [P(B | A) × P(A)] / [P(B | A) × P(A) + P(B | ¬A) × P(¬A)]
```

### Components (Bayesian terminology)

- **P(A)**: Prior probability (what we believe before seeing evidence B)
- **P(A | B)**: Posterior probability (updated belief after seeing evidence B)
- **P(B | A)**: Likelihood (how likely B is if A is true)
- **P(B)**: Marginal likelihood or evidence (overall probability of observing B)

### Intuition

Bayes' theorem updates beliefs based on evidence:

```
Posterior = (Likelihood × Prior) / Evidence
```

**What it tells us:**
- Strong evidence (high P(B | A), low P(B | ¬A)) pulls the posterior toward A
- Weak evidence leaves the posterior close to the prior
- The prior matters! Rare events need strong evidence to become probable.

### Diagnostic Testing Example

**Setup:**
- Disease prevalence: P(D) = 0.01 (1% of population has disease)
- Test sensitivity: P(+ | D) = 0.95 (95% of sick people test positive)
- Test specificity: P(- | ¬D) = 0.99 (99% of healthy people test negative)
  - Equivalently: P(+ | ¬D) = 0.01 (1% false positive rate)

**Question:** If someone tests positive, what's the probability they have the disease?

**Solution using Bayes:**
```
P(D | +) = [P(+ | D) × P(D)] / [P(+ | D) × P(D) + P(+ | ¬D) × P(¬D)]
         = [0.95 × 0.01] / [0.95 × 0.01 + 0.01 × 0.99]
         = 0.0095 / [0.0095 + 0.0099]
         = 0.0095 / 0.0194
         = 0.4897 ≈ 49%
```

**Interpretation:** Even with a positive test, there's only about 49% chance of actually having the disease! Why? The disease is rare (1%), so even a 1% false positive rate produces many false alarms.

### Odds Form (Alternative)

Sometimes it's easier to work with odds:

**Odds:** O(A) = P(A) / P(¬A)

**Bayes' theorem in odds form:**
```
O(A | B) = O(A) × [P(B | A) / P(B | ¬A)]
```

The ratio P(B | A) / P(B | ¬A) is called the **likelihood ratio** or **Bayes factor**.

---

## Independence

**Definition:** Events A and B are independent if knowing one doesn't change the probability of the other.

### Three Equivalent Definitions

A and B are independent if and only if ANY of these hold:

1. **P(A | B) = P(A)** (knowing B doesn't change probability of A)
2. **P(B | A) = P(B)** (knowing A doesn't change probability of B)
3. **P(A ∩ B) = P(A) × P(B)** (multiplication rule for independent events)

If any one is true, all three are true. If any one fails, A and B are dependent.

### Testing Independence from a 2×2 Table

```
         B      ¬B    Total
A        a      b     a+b
¬A       c      d     c+d
Total   a+c    b+d     N
```

**Test:** Check if P(A ∩ B) = P(A) × P(B)

```
(a/N) = [(a+b)/N] × [(a+c)/N]
```

Multiply both sides by N²:
```
a × N = (a+b) × (a+c)
```

**Shortcut:** Cross-multiply to check independence:
```
a × d = b × c    (if true, then A and B are independent)
```

Why? Because this is equivalent to checking P(A ∩ B) = P(A) × P(B).

### Expected Counts Under Independence

If A and B were independent, the expected count in cell (A, B) would be:
```
E[a] = N × P(A) × P(B) = N × [(a+b)/N] × [(a+c)/N] = (a+b)(a+c)/N
```

Compare observed counts to expected counts to test independence.

### Common Pitfall

⚠️ **Independence ≠ Mutually Exclusive**

- **Independent:** P(A ∩ B) = P(A) × P(B) — knowing one doesn't tell you about the other
- **Mutually exclusive:** P(A ∩ B) = 0 — can't both happen

If A and B are mutually exclusive with nonzero probabilities, they are NOT independent! Knowing A occurred tells you B definitely didn't occur.

---

## Expectation

**Definition:** The expected value (or mean) of a random variable is the average value you'd get if you repeated the experiment infinitely many times.

**Notation:** E[X] or μ (mu)

### Discrete Random Variables

If X takes values x₁, x₂, ..., xₙ with probabilities p₁, p₂, ..., pₙ:
```
E[X] = x₁p₁ + x₂p₂ + ... + xₙpₙ = Σ xᵢpᵢ
```

**Example:** Roll a fair six-sided die. What's the expected value?
```
E[X] = 1×(1/6) + 2×(1/6) + 3×(1/6) + 4×(1/6) + 5×(1/6) + 6×(1/6)
     = (1+2+3+4+5+6)/6
     = 21/6
     = 3.5
```

### Properties of Expectation

**Linearity (most important property):**
```
E[aX + bY + c] = aE[X] + bE[Y] + c
```

This holds **even if X and Y are dependent**! No independence required.

**Consequences:**
- E[X + Y] = E[X] + E[Y] (expectation of sum = sum of expectations)
- E[cX] = cE[X] (constants factor out)
- E[X + c] = E[X] + c (adding constant shifts expectation)

### Expected Value of Indicator Variables

An **indicator variable** (or Bernoulli variable) is 1 if an event occurs, 0 otherwise.

If I_A is the indicator for event A:
```
E[I_A] = 1 × P(A) + 0 × P(¬A) = P(A)
```

**Key insight:** The expected value of an indicator equals the probability of the event!

### Linearity of Expectation in Action

**Problem:** In a random arrangement of 52 cards, how many cards are in their "correct" position (1st card is an Ace of Spades, 2nd card is 2 of Spades, etc.)?

**Solution using linearity:**

Let Xᵢ = indicator that card i is in position i.

Total cards in correct position: X = X₁ + X₂ + ... + X₅₂

By linearity:
```
E[X] = E[X₁] + E[X₂] + ... + E[X₅₂]
     = P(card 1 correct) + P(card 2 correct) + ... + P(card 52 correct)
     = (1/52) + (1/52) + ... + (1/52)    [52 times]
     = 52 × (1/52)
     = 1
```

On average, exactly 1 card is in its correct position, regardless of the shuffling!

**Why linearity is powerful:** We didn't need to compute the full distribution of X (which is complicated). We just used indicators and linearity.

### Expected Value for Independent Random Variables

If X and Y are **independent**:
```
E[XY] = E[X] × E[Y]
```

⚠️ This does NOT hold for dependent variables in general.

### Expectation and Law of Total Probability

If B₁, B₂, ..., Bₙ partition the sample space:
```
E[X] = E[X | B₁]P(B₁) + E[X | B₂]P(B₂) + ... + E[X | Bₙ]P(Bₙ)
```

This is the "law of total expectation" — weighted average of conditional expectations.

### Common Distributions and Their Expectations

| Distribution | E[X] |
|-------------|------|
| Bernoulli(p) | p |
| Binomial(n, p) | np |
| Geometric(p) | 1/p |
| Poisson(λ) | λ |
| Uniform(a, b) | (a+b)/2 |
| Normal(μ, σ²) | μ |

---

## Summary

### Core Formulas to Memorize

**Counting:**
- Permutations: P(n,k) = n!/(n-k)!
- Combinations: C(n,k) = n!/(k!(n-k)!)

**Probability Laws:**
- P(¬A) = 1 - P(A)
- P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
- P(A | B) = P(A ∩ B) / P(B)
- P(A ∩ B) = P(A | B) × P(B)

**Bayes' Theorem:**
- P(A | B) = [P(B | A) × P(A)] / P(B)

**Independence:**
- P(A ∩ B) = P(A) × P(B)
- Check: a × d = b × c in a 2×2 table

**Expectation:**
- E[X] = Σ xᵢpᵢ
- E[aX + bY + c] = aE[X] + bE[Y] + c
- E[indicator] = probability

### Problem-Solving Strategy

1. **Draw a diagram** (tree, table, Venn diagram)
2. **Write what you know** (given probabilities, counts)
3. **Write what you want** (target probability or expectation)
4. **Connect them** using formulas above
5. **Check your answer** (does it make intuitive sense? Sum to 1?)

### Common Mistakes to Avoid

- ❌ Assuming P(A | B) = P(B | A)
- ❌ Confusing independence with mutual exclusivity
- ❌ Forgetting to check P(B) > 0 before computing P(A | B)
- ❌ Using E[XY] = E[X]E[Y] when X and Y are dependent
- ❌ Forgetting the complement rule: P(¬A) = 1 - P(A)

---

## Additional Topics for Future Study

Beyond the core concepts above, you should eventually learn:

- **Variance:** E[(X - μ)²] — measures spread
- **Covariance:** E[(X - μₓ)(Y - μᵧ)] — measures joint variation
- **Correlation:** Cov(X,Y) / (σₓσᵧ) — standardized covariance
- **Law of Large Numbers:** Sample average → E[X] as n → ∞
- **Central Limit Theorem:** Sum of many random variables → Normal distribution
- **Common distributions:** Binomial, Poisson, Normal, Exponential

These build on the foundation above and are essential for advanced probability and statistics.
