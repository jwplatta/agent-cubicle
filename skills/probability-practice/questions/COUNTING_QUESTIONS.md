QUESTION: A small community consists of 10 females, each of whom has 3 children. If one female and one of her children are to be chosen as parent and child of the year, how many different choices are possible?

QUESTION: A college planning committee consists of 3 freshmen, 4 sophomores, 5 juniors, and 2 seniors. A subcommittee of 4, consisting of 1 person from each class, is to be chosen. How many different subcommittees are possible?

QUESTION: How many different 7-place license plates are possible if the first 3 places are to be occupied by letters and the final 4 by numbers?

QUESTION: How many functions defined on n points are possible if each functional value is either 0 or 1?

QUESTION: How many license plates would be possible if repetition among letters or numbers were prohibited?

QUESTION: Given the contingency table:
{{table}}
How many outcomes are in the sample space?
SOLUTION: The sample space contains all possible outcomes. From the table, the total count is {{total}}. Therefore, |S| = {{total}} outcomes.

QUESTION: Given the contingency table:
{{table}}
How many outcomes satisfy the condition "A and B both occur"?
SOLUTION: Outcomes where both A and B occur are in the cell (A, B), which has {{joint_AB}} outcomes.

QUESTION: Given the contingency table:
{{table}}
How many outcomes satisfy "A or B (or both)"?
SOLUTION:  Outcomes with A or B are in cells (A,B), (A,¬B), and (¬A,B).
Count = {{joint_AB}} + {{joint_A_notB}} + {{joint_notA_B}} = {{union_count}}

### Question 2

**Prompt:**
Given the contingency table:

{{table}}

If you randomly select 2 outcomes from the sample space without replacement, how many ways can you do this?

**Solution:**
This is a combination problem: choosing 2 items from {{total}} without regard to order.

C({{total}}, 2) = {{total}}! / (2! × {{minus_2}}!) = ({{total}} × {{minus_1}}) / 2 = {{combination_result}}

## hard

### Question 1

**Prompt:**
Given the contingency table:

{{table}}

Suppose you arrange all {{total}} outcomes in a line. How many such arrangements are possible?

**Solution:**
The number of ways to arrange {{total}} distinct outcomes is {{total}}! = {{factorial_result}}