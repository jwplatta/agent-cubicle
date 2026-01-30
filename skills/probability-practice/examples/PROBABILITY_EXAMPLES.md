# Probability Practice Examples

This document provides complete worked examples for each subcategory of probability problems. Use these as a reference for the expected format and level of detail in your solutions.

---

## Example 1: Marginal Probability

**Category:** Joint Probability → Marginals
**Difficulty:** Easy

### Problem

Given the contingency table:

|        | B      | ¬B     | Total  |
|--------|--------|--------|--------|
| **A**  |     12 |      8 |     20 |
| **¬A** |      6 |     14 |     20 |
| **Total** |     18 |     22 |     40 |

Compute P(A).

<details>
<summary><b>Hint</b></summary>

Sum the row for event A, then divide by the total.

</details>

### Solution

**By hand:**

P(A) = (number in row A) / (total count)
     = 20 / 40
     = 1/2
     = 0.5000

**Explanation:**

The marginal probability P(A) is found by summing all outcomes where A occurs, regardless of B's status:
- Count in row A: 12 + 8 = 20
- Total count: 40
- P(A) = 20/40 = 1/2

We can simplify: GCD(20, 40) = 20, so 20/40 = 1/2.

**Check:** P(A) + P(¬A) = 20/40 + 20/40 = 40/40 = 1 ✓

---

## Example 2: Conditional Probability

**Category:** Joint Probability → Conditional
**Difficulty:** Medium

### Problem

Given the contingency table:

|        | B      | ¬B     | Total  |
|--------|--------|--------|--------|
| **A**  |      9 |      6 |     15 |
| **¬A** |      3 |     12 |     15 |
| **Total** |     12 |     18 |     30 |

Compute P(A | B).

<details>
<summary><b>Hint</b></summary>

P(A|B) = P(A ∩ B) / P(B). Look at column B: what fraction has A?

</details>

### Solution

**Method 1: Using the definition**

P(A | B) = P(A ∩ B) / P(B)

First, find the components:
- P(A ∩ B) = 9/30 (cell count / total)
- P(B) = 12/30 (column B total / total)

Now compute:
P(A | B) = (9/30) / (12/30)
         = 9/30 × 30/12
         = 9/12
         = 3/4
         = 0.7500

**Method 2: Direct counting (restriction to B)**

Given that B occurred, we restrict our attention to column B only:
- Total outcomes in B: 12
- Outcomes with both A and B: 9
- P(A | B) = 9/12 = 3/4

**Explanation:**

When we condition on B, we're asking: "Among the 12 outcomes where B occurred, how many also have A?"

The answer is 9 out of 12, which simplifies to 3/4.

**Note:** P(A | B) ≠ P(A)
- P(A) = 15/30 = 1/2
- P(A | B) = 9/12 = 3/4

Since 3/4 > 1/2, knowing B occurred increases the probability of A. This tells us A and B are **not independent**.

---

## Example 3: Bayes' Theorem

**Category:** Joint Probability → Bayes
**Difficulty:** Medium

### Problem

Given the contingency table:

|        | B      | ¬B     | Total  |
|--------|--------|--------|--------|
| **A**  |      8 |      4 |     12 |
| **¬A** |      2 |     16 |     18 |
| **Total** |     10 |     20 |     30 |

You observe event B. Use Bayes' theorem to find P(A | B) from P(B | A), P(A), and P(B).

<details>
<summary><b>Hint</b></summary>

Bayes' rule: P(A|B) = P(B|A) × P(A) / P(B). Calculate each component from the table.

</details>

### Solution

**Step 1: Identify the components**

We need three pieces for Bayes' theorem:
1. Prior: P(A)
2. Likelihood: P(B | A)
3. Evidence: P(B)

**Step 2: Calculate from the table**

Prior P(A):
- P(A) = 12/30 = 2/5

Likelihood P(B | A):
- Given A occurred (row A has 12 outcomes)
- How many have B? 8
- P(B | A) = 8/12 = 2/3

Evidence P(B):
- P(B) = 10/30 = 1/3

**Step 3: Apply Bayes' theorem**

P(A | B) = P(B | A) × P(A) / P(B)
         = (2/3) × (2/5) / (1/3)
         = (4/15) / (1/3)
         = (4/15) × 3
         = 12/15
         = 4/5
         = 0.8000

**Verification: Direct calculation**

P(A | B) = P(A ∩ B) / P(B)
         = (8/30) / (10/30)
         = 8/10
         = 4/5 ✓

**Interpretation:**

- **Before** observing B: P(A) = 2/5 = 0.4
- **After** observing B: P(A | B) = 4/5 = 0.8

Observing B doubled our belief in A! This is because B is more likely when A is true:
- P(B | A) = 2/3 ≈ 0.667
- P(B | ¬A) = 2/18 ≈ 0.111

B is about 6 times more likely under A than under ¬A, which strongly suggests A when we see B.

---

## Example 4: Independence Test

**Category:** Joint Probability → Independence
**Difficulty:** Hard

### Problem

Given the contingency table:

|        | B      | ¬B     | Total  |
|--------|--------|--------|--------|
| **A**  |      6 |      9 |     15 |
| **¬A** |      4 |      6 |     10 |
| **Total** |     10 |     15 |     25 |

Check if A and B are independent by verifying all three equivalent definitions:
1. P(A ∩ B) = P(A) × P(B)
2. P(A | B) = P(A)
3. P(B | A) = P(B)

<details>
<summary><b>Hint</b></summary>

Test all three conditions. They're equivalent, so they should all give the same answer.

</details>

### Solution

**Test 1: P(A ∩ B) = P(A) × P(B)?**

Calculate left side:
- P(A ∩ B) = 6/25

Calculate right side:
- P(A) = 15/25 = 3/5
- P(B) = 10/25 = 2/5
- P(A) × P(B) = (3/5) × (2/5) = 6/25

**Comparison:**
6/25 = 6/25 ✓

**Test 2: P(A | B) = P(A)?**

Calculate left side:
- P(A | B) = P(A ∩ B) / P(B) = (6/25) / (10/25) = 6/10 = 3/5

Calculate right side:
- P(A) = 15/25 = 3/5

**Comparison:**
3/5 = 3/5 ✓

**Test 3: P(B | A) = P(B)?**

Calculate left side:
- P(B | A) = P(A ∩ B) / P(A) = (6/25) / (15/25) = 6/15 = 2/5

Calculate right side:
- P(B) = 10/25 = 2/5

**Comparison:**
2/5 = 2/5 ✓

**Conclusion:**

All three tests pass, so **A and B are independent**.

**Interpretation:**

Independence means:
- Knowing B occurred doesn't change the probability of A
- Knowing A occurred doesn't change the probability of B
- The joint probability equals the product of the marginals

In this table, the events are perfectly independent. This is relatively rare in real-world data.

**Verification using expected counts:**

Under independence, expected counts are:
- E(A ∩ B) = 15 × 10 / 25 = 6 ✓ (matches observed: 6)
- E(A ∩ ¬B) = 15 × 15 / 25 = 9 ✓ (matches observed: 9)
- E(¬A ∩ B) = 10 × 10 / 25 = 4 ✓ (matches observed: 4)
- E(¬A ∩ ¬B) = 10 × 15 / 25 = 6 ✓ (matches observed: 6)

All observed counts equal expected counts, confirming perfect independence.

Chi-squared statistic: χ² = 0 (perfect fit)

---

## Example 5: Union and Inclusion-Exclusion

**Category:** Joint Probability → Marginals
**Difficulty:** Medium

### Problem

Given the contingency table:

|        | B      | ¬B     | Total  |
|--------|--------|--------|--------|
| **A**  |      5 |     10 |     15 |
| **¬A** |      8 |      7 |     15 |
| **Total** |     13 |     17 |     30 |

Compute P(A ∪ B) using the inclusion-exclusion formula:
P(A ∪ B) = P(A) + P(B) - P(A ∩ B)

<details>
<summary><b>Hint</b></summary>

First find the three component probabilities, then apply the formula.

</details>

### Solution

**Step 1: Find the components**

P(A) = 15/30 = 1/2

P(B) = 13/30

P(A ∩ B) = 5/30 = 1/6

**Step 2: Apply inclusion-exclusion**

P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
         = 15/30 + 13/30 - 5/30
         = (15 + 13 - 5)/30
         = 23/30
         ≈ 0.7667

**Step 3: Verify by direct counting**

Count outcomes with A or B or both:
- Cell (A, B): 5
- Cell (A, ¬B): 10
- Cell (¬A, B): 8
- Total: 5 + 10 + 8 = 23

P(A ∪ B) = 23/30 ✓

**Explanation:**

The inclusion-exclusion principle corrects for double-counting:
- P(A) = 15/30 counts all outcomes with A (including those with B)
- P(B) = 13/30 counts all outcomes with B (including those with A)
- We've counted P(A ∩ B) = 5/30 twice, so subtract it once

**Visual check:**

Draw a Venn diagram:
- Circle A alone: 10 (from A ∩ ¬B)
- Circle B alone: 8 (from ¬A ∩ B)
- Overlap (A ∩ B): 5
- Outside both: 7 (from ¬A ∩ ¬B)

Total with A or B: 10 + 5 + 8 = 23 ✓

**Complement check:**

P(¬A ∩ ¬B) = 7/30
P(A ∪ B) + P(¬A ∩ ¬B) = 23/30 + 7/30 = 30/30 = 1 ✓

This makes sense because (A ∪ B) and (¬A ∩ ¬B) are complements.

---

## Example 6: Law of Total Probability with Bayes

**Category:** Joint Probability → Bayes
**Difficulty:** Hard

### Problem

Given the contingency table:

|        | B      | ¬B     | Total  |
|--------|--------|--------|--------|
| **A**  |     10 |      5 |     15 |
| **¬A** |      4 |     21 |     25 |
| **Total** |     14 |     26 |     40 |

Use the law of total probability to compute P(B) from P(B | A) and P(B | ¬A):

P(B) = P(B | A) × P(A) + P(B | ¬A) × P(¬A)

Then use this with Bayes' rule to find P(A | B).

<details>
<summary><b>Hint</b></summary>

First partition P(B) using the law of total probability, then apply Bayes' rule.

</details>

### Solution

**Step 1: Calculate conditional probabilities**

P(B | A):
- Given A (row A has 15 outcomes), how many have B?
- P(B | A) = 10/15 = 2/3

P(B | ¬A):
- Given ¬A (row ¬A has 25 outcomes), how many have B?
- P(B | ¬A) = 4/25

**Step 2: Calculate marginals**

P(A) = 15/40 = 3/8

P(¬A) = 25/40 = 5/8

**Step 3: Apply law of total probability**

P(B) = P(B | A) × P(A) + P(B | ¬A) × P(¬A)
     = (2/3) × (3/8) + (4/25) × (5/8)
     = 6/24 + 20/200
     = 1/4 + 1/10

Convert to common denominator (20):
     = 5/20 + 2/20
     = 7/20

**Verification:** Direct calculation from table
P(B) = 14/40 = 7/20 ✓

**Step 4: Apply Bayes' theorem**

Now find P(A | B):

P(A | B) = P(B | A) × P(A) / P(B)
         = (2/3) × (3/8) / (7/20)
         = (6/24) / (7/20)
         = (1/4) / (7/20)
         = (1/4) × (20/7)
         = 20/28
         = 5/7
         ≈ 0.7143

**Verification:** Direct calculation
P(A | B) = P(A ∩ B) / P(B)
         = (10/40) / (14/40)
         = 10/14
         = 5/7 ✓

**Interpretation:**

The law of total probability partitions P(B) into two mutually exclusive scenarios:
1. B occurs when A is true: contributes (2/3) × (3/8) = 1/4
2. B occurs when A is false: contributes (4/25) × (5/8) = 1/10
3. Total: 1/4 + 1/10 = 7/20

This partition is useful because:
- It breaks a complex probability into simpler conditional pieces
- It's the denominator in Bayes' theorem
- It shows how different scenarios contribute to the overall probability

**Key insight:**

Most of P(B) comes from the A scenario (1/4) rather than the ¬A scenario (1/10). This means B is much more likely when A is true, which is why observing B strongly suggests A (posterior P(A|B) = 5/7 is much higher than prior P(A) = 3/8).

---

## General Problem-Solving Strategy

1. **Draw or visualize the table**
   - Label rows and columns clearly
   - Fill in all marginals

2. **Identify what you're asked to find**
   - Marginal: sum row or column
   - Joint: look at specific cell
   - Conditional: restrict to one row/column
   - Independence: test equality conditions

3. **Calculate step-by-step**
   - Show numerators and denominators
   - Simplify fractions using GCD
   - Verify results make sense (probabilities between 0 and 1)

4. **Check your answer**
   - Use an alternative method when possible
   - Verify probabilities sum to 1 where expected
   - Compare conditional to marginal for independence

5. **Interpret the result**
   - What does this probability mean?
   - Is it what you expected?
   - What does it tell you about the relationship between events?
