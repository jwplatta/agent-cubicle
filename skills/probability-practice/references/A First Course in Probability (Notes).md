# A First Course in Probability

## Topics

- Combinatorial analysis
- Axioms of probability
- Conditional probability and independence
- Random variables
- Continuous random variables
- Jointly distributed random variables
- Properties of expectation
- Limit theorems

## Ch 1 - Combinatorial Analysis

- The mathematical theory of counting is called **combinatorial analysis**.
- The **basic principle of counting**: for experiments A and B, if A results in m possible outcomes and B results in n possible outcomes, then the total possible outcomes is `m x n`.
	- *counting all possible outcomes*
	- this principle can be generalized where you just keep multiplying the number of possible outcomes together for each experiment
- A **permutation** is an ordered arrangement.
	- *We are counting ordered pairs*
	- For `n` objects there are `n(n - 1)(n - 2)...3 x 2 x 1 = n!` permutations
	- Permutations with alike objects $\frac{n!}{n_1!n_2!...n_r!}$ where the denominator represents those objects that are alike
- **combinations**
	- *So in combinations we are counting groups.*
	- Determining the number of different groups of $r$ objects that could be formed from a total of $n$ object.
	- "n choose r" $\begin{pmatrix} n \\ r \end{pmatrix} = \frac{n!}{(n-r)!r!}$ is the number of possible combinations of $n$ objects of size $r$
	- Useful identity $\begin{pmatrix} n \\ r \end{pmatrix} = \begin{pmatrix} n - 1 \\ r - 1\end{pmatrix} + \begin{pmatrix} n - 1 \\ r \end{pmatrix} \text{ s.t. } 1 \leq r \leq n$
	- $\begin{pmatrix} n \\ r \end{pmatrix}$ are called **binomial coefficients**
	- binomial theorem $(x + y)^n = \sum_{k=0}^n \begin{pmatrix} n \\ k \end{pmatrix} x^k y^{n - k}$
- Multinomial coefficients
	- *Counting groups of different sizes*
	- A set of $n$ distinct items is divided into $r$ distinct groups of varying sizes, $n_1, n_2, ..., n_r$. How many different divisions are possible?
	- $\begin{pmatrix}n \\ n_1, n_2, ..., n_r \end{pmatrix} = \frac{n!}{n_1!n_2!...n_r!}$
		- why is this the same as the permutation one?
	- multinomial theorem $(x_1 + x_2 + ... + x_r)^n = \sum_{n_1,...,n_r} \begin{pmatrix} n \\ n_1,n_2,...,n_r\end{pmatrix} x_1^{n_1}x_2^{n_2}...x_r^{n_r}$

## Ch 2 - Axioms of Probability

- **sample space** set of all possible outcomes of an experiment
- **event** is a set of possible outcomes in the sample space
	- $E^c$ is the **complement** of an event $E$. It consists of all the outcomes in a sample space $S$ that are not in $E$
- defining probability
	- **relative frequency** limiting relative frequency of $E$
	- **axiomatic approach**
- *modern approach* to probability assumes the existence of a set function $P$ defined on the events of the sample space $S$ that follows these axioms:
	- **Axiom 1** states that $0 \leq P(E) \leq 1$
	- **Axiom 2** states that $P(S) = 1$
	- **Axiom 3** states that $P(\cup_{i=1} E) = \sum_{i=1}P(E_i)$


Note that when the sample space is an uncountably infinite set, $P(E)$ is defined only for a class of events called "measurable"

Some important propositions regarding the basic axioms of probability:

The probability that an event occurs is 1 minus the probability that it does not occur: $P(E^c) = 1 - P(E)$

If the probability of event $E$ is contained in the probability of event $F$, i.e. $E \subset F$, then the probability of $E$ is no greater than $F$: $P(E) \leq P(F)$

However, if the events $E$ and $F$ are overlapping, then the probability of $F$ is equal to the joint probability of E and F plus the joint probability of E's complement and F: $P(F) = P(EF) + P(E^cF)$

The probability of $F$ is equal to the probability of E plus the joint probability of the complement of E and F: $P(F) = P(E) + P(E^cF)$

$P(E \cup F) = P(E) + P(F) - P(EF)$, the probability that either _E or F occurs_. We subtract $P(EF)$ because it is already accounted for in $P(E) + P(F)$. $P(EF)$ is the probability of events E and F both occurring and $P(E \cup F)$ is the probability of events E or F occurring. Note that the complement of $P(E \cup F)$, i.e. at least E or F occurs, is $P(E^cF^c)$, i.e. neither E nor F occurs.

The **inclusion-exclusion identity** $P(E_1 \cup E_2 \cup ... \cup E_n) = \sum_{i=1}^nP(E_i) - \sum P(E_{i1}E_{i2}) + ... + (-1)^{r+1} \sum P(E_{i1}E_{i2}...E_{i_r}) + ... + (-1)^{n+1}P(E_1E_2...E_n)$. In words, the probability of the union of $n$ events *equals* the sum of the probabilities of these events taken one at a time *minus* the sum of the probabilities of these events taken two at a time *plus* the sum of the probabilities of these events taken three at a time, and so on. More succinct: $P(\cup E_i) = \sum_{r=1}^n (-1)^{r+1} \sum P(E_{i_1}...E_{i_r})$ 
$$
P(\cup E_i) = \sum P(E_i) - \sum P(E_i \cap E_j) + \sum P(E_i \cap E_j \cap E_k) - ... + (-1)^{n+1} P(E_1 \cap ... \cap E_n)
$$

$$
P(A \cap B \cap C) = P(A) + P(B) + P(C) - P(A \cap B) - P(B \cap C) - P(C \cap A) + P(A \cap B \cap C)
$$


For any **event** $E$, $P(E) = \frac{\text{number of outcomes in }E}{\text{number of outcomes in }S}$. This assumes that all outcomes are equally likely to occur. So the probability of $E$ equals the proportion of outcomes in the sample space $S$ that are contained in $E$.
 
The **union of events** $E_1, E_2, ...$ is denoted by $\overset{\infty}\cup_{n=1}E_n$ and is the event consisting of all outcomes that are in $E_n$ for at least one value of $n=1,2,...$

The **intersection of events** $E_1, E_2, ...$ is denoted by $\overset{\infty}\cap_{n=1}E_n$ and is the event consisting of those outcomes that are in all events $E_n$, $n=1,2,...$

- Probability as a continuous set function
	- Increasing sequence of events 
	- Decreasing sequence of events


## Ch 3 - Conditional Probability and Independence

The conditional probability of an event E given that F occurred is defined as
$$
P(E \vert F) = \frac{P(EF)}{P(F)}
$$
To compute the intersection of events
$$
P(EF) = P(F)P(E \vert F)
$$
which can be generalized to the **multiplication rule**
$$
P(E_1E_2E_3...E_n) = P(E_1) P(E_2 \vert E_1) P(E_3 \vert E_1 E_2) ... P(E_n \vert E_1 ... E_{n-1})
$$
It can be helpful when finding the probability of an event E to first condition upon some second event F. The probability of event E is a a weighted average of the conditional probability of E given F has occurred and the conditional probability of E given that F has not occurred
$$
E = EF \cup EF^c
$$
or 
$$
\begin{align}
P(E) = P(EF) + P(EF^c) \\
= P(E \vert F)P(F) + P(E \vert F^c)P(F^c) \\
= P(E \vert F)P(F) + P(E \vert F^c)[1 - P(F)]
\end{align}
$$

The **odds** of an event A tell how much more likely it is that the event A occurs than it is that it does not occur
$$
\frac{P(A)}{P(A^c)} = \frac{P(A)}{1 - P(A)}
$$
or for a hypothesis H and evidence E
$$
\frac{P(H \vert E)}{P(H^c \vert E)} = \frac{P(H)P(E \vert H)}{P(H^c)P(E \vert H^c)}
$$
The **law of total probability**
$$
P(E)= \sum_{i=1}^n P(EF_i) = \sum_{i=1}^n P(E \vert F_i)P(F_i)
$$

And Bayes' rule
$$
P(F_j \vert E) = \frac{P(EF_j)}{P(E)} = \frac{P(E \vert F_j)P(F_j)}{\sum_{i=1}^n P(E \vert F_i)P(F_i)}
$$
Two events E and F are said to be **independent** if $P(EF) = P(E)P(F)$. In general, an infinite set of events is independent if every finite subset of those events is independent.
$$
\begin{align}
P(EFG) = P(E)P(F)P(G) \\
P(EF) = P(E)P(F) \\
P(EG) = P(E)P(G) \\
P(FG) = P(F)P(G)
\end{align}
$$

## Ch 4 - Random Variables

A **random variable** is a real valued function defined on the sample space, i.e. some function of the outcome. We assign probabilities to the possible values of the random variable.
- Shorter: a random variable is a function mapping outcomes to numbers.
- Events, on the other hand, are sets of outcomes.
- Every statement about random variables can be translated to events

The **cumulative distribution function** or **distribution function** of $X$ specifies for all real values of $x$ the probability that the random variable is less than or equal to $x$:
$$
F(x) = P \{X \leq x\} \ \ \text{ where } -\infty < x < \infty
$$
A **discrete random variable** can only take on a countable number of possible values. The **probability mass function** $p(a)$ of $X$ is positive for at most a countable number of values $a$:
$$
\begin{flalign}
p(a) = P \{X=a\} \text{ is the pmf} \\
p(x_i) \geq 0 \text{ for } i = 1,2,... \\
p(x) = 0 \text{ for all other values of }x \\
\sum_{i=1}^{\infty} p(x_i) = 1
\end{flalign}
$$
The **expectation**, or expected value, of a random variable $X$ is just the weighted average of the possible values that $X$ can take on. If $X$ has a probability mass function $p(x)$, then its expectation is
$$
E[X]= \sum x \cdot p(x)
$$
We can find the expectation of a function of a discrete random variable $X$, call it $g(X)$, by computing $E[g(X)]$
$$
E[g(X)] = \sum_i g(x_i)p(x_i)
$$
In words, $E[g(X)]$ is a weight average of $g(x)$ which is weighted by the probability that $X$ is equal to $x$.

If $a$ and $b$ are constants, then
$$
E[aX + b] = aE[X] + b
$$

The expected value of a discrete random variable $X$ is also called the *mean* or *first moment* of $X$. The $n-th$ moment of $X$ is
$$
E[X^n] = \sum x^nP(x)
$$
We can describe the distribution function $F$ of a random variable $X$ in terms of its expectation, variance, and standard deviation.

The **variance** of $X$ tells us about the spread of the values $X$ can take on. Intuitively we'd expect to measure the variance of the values of $X$ as a measure of the distance of $x$ from the mean of $X$, i.e. $\mu = E[X]$. The value $E[X]$ is often difficult to use. Instead we rely on the square of the difference between $X$ and its mean $\mu$:
$$
Var(X) = E[(X - \mu)^2]
$$
Often the easiest way to compute the variance is
$$
Var(X) = E[X^2] - (E[X])^2
$$
The **standard deviation** is the square root of the variance:
$$
SD(X) = \sqrt{Var(X)}
$$

A **Bernoulli discrete random variable** is characterized by a binary outcome, e.g. heads or tails, where the probability of success is $p$ and the probability of failure is $1- p$:
$$
\begin{align}
p(0) = P\{X=0\} = 1 - p \\
p(1) = P\{X=1\} = p
\end{align}
$$
A **binomial random variable** is characterized by the number of repeated success or failures in $n$ trials. A Bernoulli random variable is a binomial random variable with parameters $(1, p)$.

The probability mass function of a binomial random variable with parameters $(n,p)$ is
$$
p(i) = \begin{pmatrix}
n \\ 
i
\end{pmatrix} p^i(1-p)^{n-i}
$$
And by the binomial theorem, the probabilities sum to 1:
$$
\sum_{i=0}^{\infty} = \sum_{i=0}^n \begin{pmatrix}
n \\ 
i
\end{pmatrix} p^i(1-p)^{n-i} = [p + (1 - p)]^n = 1
$$
## Ch 5 - Continuous Random Variables

$X$ is a **continuous random variables** if and only if its set of possible values are uncountable.
$$
P\{X \in B\} = \int_B f(x) dx
$$
where $B$ is any set of real numbers. The function $f$ is called the **probability density function** of the random variable $X$.

We can find the probability that $X$ will be in $B$ by integrating the probability density function:
$$
1 = P\{X \in (-\infty,\infty)\} = \int_{-\infty}^{\infty} f(x)dx
$$
All probability statements about $X$ can be answered in terms of the function $f$, e.g. probability that $X$ is in the interval $B = [a,b]$
$$
P(a \leq X \leq b) = \int_a^b f(x)dx
$$
So the cumulative distribution function $P$ represents the probability of $X$ being between $a$ and $b$ and we find this probability by integrating the probability density function $f(x)$. The probability density function does not directly give us a probability.

The *expected value* of a continuous random variable is defined as
$$
f(x)dx \approx P\{x \leq X \leq x + dx\} \text{ for small } dx
$$
or
$$
E[X] = \int_{-\infty}^{\infty} x f(x) dx
$$
The expected value of the function of a continuous random variable is defined as
$$
E[g(X)] = \int_{-\infty}^{\infty} g(x)f(x)dx
$$
As with the discrete random variable, we can remove constants from the expectation calculation:
$$
E[aX + b] = aE[X] + b
$$
Variance is also defined for a continuous random variable the same way it is with a discrete random variable:
$$
Var(X) = E[(X - \mu)^2]
$$
or
$$
Var(X) = E[X^2] - (E[X])^2
$$

A **uniformly distributed** random variable is defined with the probability density function over interval $(0, 1)$:
$$
f(x) = \begin{cases}
1 \text{ when } 0 < x < 1 \\
0 \text{ otherwise}
\end{cases}
$$
Basically, since $f(x)$ is constant, the probability of $P(X)$ is just as likely to be near any value in the interval $(0,1)$. So the probability that $X$ is in any subinterval $(a, b)$ is equal to the length of that subinterval:
$$
P\{a \leq X \leq b\} = \int_{a}^{b} f(x)dx = b - a
$$

A **normally distributed** random variable $X$ with parameters $\mu$ and $\sigma^2$ has a probability density function
$$
f(x) = \frac{1}{\sqrt{2 \pi \sigma}}e^{\frac{-(x-\mu)^2}{2 \sigma^2}} \text{ where } -\infty < x < \infty
$$
This definition forms the familiar bell shaped curved graph around the expected value $\mu$ where the variance is $\sigma^2$.

If we integrate this probability density function we get 1 which shows that $f(x)$ is a probability density function
$$
f(x) = \frac{1}{\sqrt{2 \pi \sigma}} \int_{-\infty}^{\infty} e^{\frac{-(x-\mu)^2}{2 \sigma^2}} dx = 1
$$
Also note that if $X$ is normally distributed, then another random variable $Y$ that is a function of $X$ is also normally distributed. So if $X$ is normally distributed with parameters $\mu$ and $\sigma^2$ and we have $P(Y) = aX + b$, then $Y$ is normally distributed with parameters $a \mu + b$ and $a^2\sigma^2$. This result allows us to define a _standard_ or _unit_ normal random variable $Z$ as $Z = \frac{X - \mu}{\sigma}$ assuming the parameters of $X$ are $\mu$ and $\sigma^2$.

The parameters of a normally distributed random variable $X$ such are its expected value, $\mu = E[X]$, and its variance, $\sigma^2 = Var(X)$. You can demonstrate this by by finding the expectation and variance of the unit random variable $Z$ and plugging it into the expectation and variance of $X$. Integrating $E[Z]$ results in $E[Z] = 0$ and integration $Var(Z)$ results in $Var(Z) = 1$. So then after rearranging $Z = \frac{X - \mu}{\sigma}$ we have
$$
E[X] = \mu + \sigma E[Z] = \mu
$$
and
$$
Var(X) = \sigma^2 Var(Z) = \sigma^2
$$
We denote the cumulative distribution function of a standard normal variable by $\Phi(x)$ so that
$$
\Phi(x) = \frac{1}{\sqrt{2\pi}} \int_{- \infty}^x e^{\frac{-y^2}{2}}dy
$$
So the distribution function of $X$ is
$$
F_X(a) = P \{X \leq a\} = P(\frac{X - \mu}{\sigma} \leq \frac{a - \mu}{\sigma}) = \Phi(\frac{a - \mu}{\sigma})
$$
The **DeMoivre-Laplace limit theorem** states that for large $n$ a binomial random variable with parameters $n$ and $p$ will approximate the distribution of a normal random variable with same mean and variance.
$$
P\{a \leq \frac{S_n - np}{\sqrt{np(1 - p)}} \leq b \} \rightarrow \Phi(b) - \Phi(a)
$$

An **exponential random variable** is exponentially distributed with parameter $\lambda$. The probability density function of an exponential random variable $x$ is
$$
f(x) = \begin{cases}
\lambda e^{-\lambda x} \text{ if } x \geq 0 \\
0 \text{ if } x < 0
\end{cases}
$$
So the cumulative distribution function of $F(a)$ is
$$
\begin{align}
F(a) = P\{X \leq a\} \\
= \int_0^a \lambda e^{- \lambda x} dx \\
= -e^{- \lambda x} \big|_0^a \\
= 1 - e^{-\lambda a} \text{ where } a \geq 0
\end{align}
$$

The parameter $\lambda$ is just the reciprocal of the expected value, $E[X] = \frac{1}{\lambda}$.

So then the variance of a exponential random variable is
$$
\begin{align}
E[X^2] = \frac{2}{\lambda}E[X] = \frac{2}{\lambda^2} \\
Var(X) = \frac{2}{\lambda^2} - (\frac{1}{\lambda})^2 = \frac{1}{\lambda^2}
\end{align}
$$
Generally, exponential random variables typically model the amount of time until an event happens. So the parameter $\lambda$ is often called the "rate of the distribution".
## Ch 6 - Jointly Distributed Random Variables

Recall that events are sets of outcomes and a random variable is a function that maps an outcome to a number. Statements about random variables can be stated in terms of events. So joint random variables are different way of talking about joint events. Working with random variables allows us to work with numeric functions that allow for:
- Calculating the expectation and variance
- Use calculus (integration) for continuous random variables
- Easier to work with multivariate distributions

A **joint cumulative probability distribution function** for random variables $X$ and $Y$ is defined as 
$$
F(a,b) = P\{X \leq a, Y \leq b \} \text{ where } -\infty < a,b < \infty
$$
We can find the **marginal distributions** of $X$ ($F_X(a)$) and $Y$ ($F_Y(b)$) from the joint distribution $F(a,b)$:
$$
F_X(a) = P\{X \leq a, Y < \infty\} = F(a, \infty)
$$
and
$$
F_Y(b) = P\{X \leq \infty, Y < b\} = F(\infty, b)
$$
In general, all questions about the joint probability of $X$ and $Y$ can be answered by their joint distribution function:
$$
P\{a_1 < X \leq a_2, b_1 < Y \leq b_2 \} = F(a_2, b_2) + F(a_1, b_1) - F(a_1,b_2) - F(a_2, b_1)
$$
If $X$ and $Y$ are _discrete random variables_, then the joint distribution function is a **joint probability mass function**:
$$
p(x,y) = P\{X=x, Y=y\}
$$
We can find the **marginal probability mass functions** of the discrete random variables $X$ and $Y$ by marginalizing out other variable. We do this by summing over all the values where the joint probability mass function is positive
- In the discrete case, we sum over the values of the random variable $Y$. In the continuous case, we integrate out $Y$.
$$
p_X(x) = P\{X=x\} = \sum_{\text{all } y \text{ such that pmf } > 0} p(x,y)
$$
and
$$
p_Y(y) = P\{Y=y\} = \sum_{\text{all } x \text{ such that pmf } > 0} p(x,y)
$$
If $X$ and $Y$ are _continuous random variables_, then the joint distribution function is a **joint probability density function**:
$$
P\{X \in A, Y \in B\} = \int_B \int_A f(x,y) dx \ dy
$$
The joint probability density function $f(x,y)$ is a measure of how likely it is the random vector $(X, Y)$ is near $(x, y)$.

We can find the **marginal probability density functions** of the continuous random variables $X$ and $Y$ by integrating out the other variable. So the marginal density of $X$ is
$$
P\{X \in A\} = P\{X \in A, Y \in (-\infty, \infty)\} = \int_A \int_{-\infty}^{\infty} f(x,y)dy \ dx = \int_A f_X(x)dx
$$
So that
$$
f_X(x) = \int_{-\infty}^{\infty} f(x,y)dy
$$
Similarly, the same is true for $f_Y(y) = \int_{-\infty}^{\infty} f(x,y) dx$.

Note that we can define a joint probability distribution of $n$ random variables similarly to how its defined when $n=2$:
$$
F(a_1,...,a_n) = P\{X_1 \leq a_1, ..., X_n \leq a_n\}
$$
The **multinomial distribution** is a join distributions where $n$ independent and identical experiments are performed:
$$
P\{X_1 = n_1, ..., X_r = n_r\} = \frac{n!}{n_1!n_2!...n_r!}p_1^{n_1}p_2^{n_2} ... p_r^{n_r}
$$

The random variables $X$ and $Y$ are **independent** if knowing the value of $X$ does not change the distribution of $Y$ and vice verse. More formally, $X$ and $Y$ are independent for any two sets of real numbers $A$ and $B$:
$$
P\{X \in A, Y \in B\} = P\{ X \in A \}P\{ Y \in B\}
$$
So for a pair of discrete random variables $A$ and $B$, $P\{X \in A, Y \in B\}$ is equal to the following where $p(x, y)$ is the probability mass function:
$$
P\{X \in A, Y \in B\} = \sum_{y \in B} \sum_{x \in A} p(x,y) = \sum_{y \in B} p_Y(y) \sum_{x \in A} p_X(x)
$$
Note that the independence of $X$ and $Y$ implies that the joint probability is the product of the marginal probabilities of $X$ and $Y$.

An infinite collection of random variables $X_1, X_2, ..., X_n$ is independent if every finite sub-collection of them is independent (for sets of real numbers $A_1, A_2, ..., A_n$):
$$
P\{X_1 \in A_1, ..., X_n \in A_n\} = \prod_{i=1}^n P\{X_i \leq a_i\}
$$
Sometimes we want to sum independent random variables $X$ and $Y$. The cumulative distribution function $F_{X+Y}$ is the **convolution** of the distribution functions $F_X$ and $F_Y$. It is equal to:
$$
F_{X+Y}(a) = P\{X + Y \leq a\} = \int_{-\infty}^{\infty} \int_{-\infty}^{a-y} f_X(x) f_Y(y) \ dx \ dy = \int_{-\infty}^{\infty} F_X(a-y)f_Y(y)dy
$$

The definition of conditional probability of two discrete random variables $X$ and $Y$ is exactly the same as the independent definition except that we condition on one of the random variables:
$$
F_{X \vert Y}(x \vert y) = P\{X \leq x \vert Y = y\} = \sum_{a \leq x}p_{X \vert Y}(a \vert y)
$$
This also implies that if $X$ is independent of $Y$ then
$$
p_{X \vert Y}(x \vert y) = P\{X = x\}
$$

The conditional probability of two continuous random variables $X$ and $Y$ can be described as the conditional probability that $X$ is between $x$ and $x + dx$ given that $Y$ is between $y$ and $y + dy$:
$$
P\{x \leq X \leq x + dx \vert y \leq Y \leq y + dy\}
$$
So we can define the conditional probability of $X$ when given a value of $Y=y$:

$$
P\{X \in A \vert Y=y\} = \int_A f_{X \vert Y}(x \vert y) dx
$$
Similar to the discrete case, if $X$ is independent of $Y$, then
$$
f_{X \vert Y}(x \vert y) = \frac{f(x,y)}{f_Y(y)} = \frac{f_X(x)f_Y(y)}{f_Y(y)} = f_X(x)
$$
## Ch 7 - Properties of Expectation

Recall that $E[X]$ is a weighted average of all the values that the random variable $X$ can take.

$$
E[X] = \sum_x x p(x)
$$
$$
E[X] = \int_{-\infty}^{\infty} x f(x) dx
$$
For two discrete random variables $X$ and $Y$ with a joint probability mass function the expectation is
$$
E[g(X, Y)] = \sum_y \sum_x g(x,y)p(x,y)
$$
For two continuous random variables $X$ and $Y$ with a joint probability density function the expectation is
$$
E[g(X,Y)] = \int_{-\infty}^{\infty} \int_{-\infty}^{\infty} g(x,y)f(x,y) \ dx \ dy
$$
In general, whenever the random variables $X_1,...,X_n$ are finite:
$$
E[X_1 + ... + X_n] = E[X_1] + ... + E[X_n] = \sum_{i=1}^n E[X_i]
$$
Suppose the random variables $X_1,...,X_n$ are i.i.d. and have distribution function $F$ with an expected value of $\mu$. The **sample mean** of the distribution function is
$$
\bar{X} = \sum_{i=1}^n \frac{X_i}{n}
$$
The expectation of the **sample mean** is equal to the expected value of the distribution:
$$
E[\bar{X}] = E[\sum_{i=1}^n \frac{X_i}{n}] = \frac{1}{n} \sum_{i=1}^n E[X_i] = \mu
$$
The sample variance of these random variables is given by
$$
S^2 = \sum_{i=1}^n \frac{(X_i - \bar{X})^2}{n-1}
$$
The covariance of two random variables $X$ and $Y$ is defined as
$$
Cov(X,Y) = E[(X - E[X])(Y - E[Y])] = E[XY - E[X]Y - XE[Y] + E[Y]E[X]] = E[XY] - E[X]E[Y]
$$
If $X$ and $Y$ are independent random variables, then $Cov(X,Y) = 0$

Here are some important propositions of covariance:
$$
\begin{align}
Cov(X,Y) = Cov(Y,X) \\
Cov(X,X) = Var(X) \\
Cov(aX, Y) = a \ Cov(X,Y) \\
Cov(\sum_{i=1}^n X_i, \sum_{j=1}^m Y_j) = \sum_{i=1}^n \sum_{j=1}^m Cov(X_i, Y_j)

\end{align}
$$
We can find the **variance** of $X$ from covariance of the $X$ and $Y$:
$$
Var(\sum_{i=1}^n X_i) = \sum_{i=1}^n Var(X_i) + 2 \sum \sum_{i<j} Cov(X_i, Y_j)
$$

The **variance of a binomial** random variable $X$ with parameters $n$ and $p$ is 
$$
Var(X) = np(1-p)
$$
The **correlation** of two random variables $X$ and $Y$ is a value between $-1$ and $1$, i.e. $-1 \leq \rho(X,Y) \leq 1$:
$$
\rho(X,Y) = \frac{Cov(X,Y)}{\sqrt{Var(X)Var(Y)}}
$$
The **conditional expected value** of a discrete random variable $X$ given the value of another random variable $Y=y$ is defined as
$$
E[X \vert Y=y] = \sum_x xP\{X=x \vert Y=y\} = \sum_x x p_{X \vert Y}(x \vert y)
$$
In the continuous case, the conditional expected value of $X$ is given by
$$
E[X \vert Y = y] = \int_{-\infty}^{\infty}x \ f_{X \vert Y}(x \vert y)dx
$$
Conditional expectations satisfy all the properties that ordinary expectations do:
$$
E[g(X) \vert Y =y]\begin{cases}
\sum_x g(x) p_{X \vert Y}(x \vert y) \\
\int_{-\infty}^{\infty} g(x) f_{X \vert Y}(x \vert y)dx
\end{cases}
$$
and 
$$
E[\sum_{i=1}^n X_i \vert Y=y] = \sum_{i=1}^n E[X_i \vert Y=y]
$$
We can use the conditional probability to find the expectation of a random variable $X$ by conditioning on the other random variable $Y$. In the discrete case:
$$
E[X] = \sum_y E[X \vert Y=y]P\{Y=y\} = \sum_y \sum_x xP\{X=x \vert Y=y\}P\{Y=y\}
$$
And in the continuous case:
$$
E[X] = \int_{-\infty}^{\infty} E[X \vert Y=y]f_Y(y) dy
$$
In general,  what you are doing here is finding the expectation of $X$ by taking the weighted average of the conditional expected value of $X$ given a specific value of $Y=y$

The **conditional variance** of a random variable $X$ and given another variable $Y$ is equal to the conditional expected square of the difference between $X$ and its conditional mean given the value of $Y$:
$$
Var(X \vert Y) = E[(X - E[X \vert Y])^2 \vert Y]
$$
We can use the conditional variance of $X$ given $Y$ in order to find the variance of $X$:
$$
Var(X) = E[Var(X \vert Y)] + Var(E[X \vert Y])
$$

multivariate normal distribution

## Ch 8 - Limit Theorems

For a non-negative random variable $X$, Markov's inequality is 
$$
P\{X \geq a\} \leq \frac{E[X]}{a}
$$
**Markov's inequality** states that the probability that $X$ is greater than or equal to $a$ is less than or equal to the average value of $X$ divided by a threshold $a$. For example, if the expected value of $X$ is 10 and the threshold is 50, then $frac{E[X]}{a} = \frac{10}{50} = 0.2$.


**Chebyshev's inequality** states that most values of a random variable $X$ stay close to the mean, $E[X]$ or $\mu$. If $X$ has a variance of $\sigma^2$, then for a value $k > 0$, the inequality is
$$
P\{\vert X - \mu \vert \geq k \sigma \} \leq \frac{1}{k^2}
$$
In other words, the probability of being more than $k$ standard deviations away from the mean is at most $\frac{1}{k^2}$.

Markov's and Chebyshev's inequalities enable use to set bounds on probabilities when the mean or both the mean and the variance of the probability distribution are known.

Interestingly, the only random variable with variance equal to zero will have an expected value of 1. So if $Var(X) = 0$, then $P\{X = E[X]\} = 1$.

**Weak law of large numbers** states that as you average more independent random variables, the probability that this average is far from the true mean becomes smaller. For a sequence of independent random variables $X_1, ..., X_n$ that are i.i.d. with a finite mean $E[X_i] = \mu$:
$$
P\{\vert \frac{X_1 +... + X_n}{n} - \mu \vert \geq \epsilon \} \rightarrow 0 \text{ as } n \rightarrow \infty
$$
Here $\epsilon$ is any small positive number that represents how close the sample average is to the true mean.

**Central limit theorems** focus on when the sum of a large number of random variables has a probability distribution close to the normal distribution. For a sequence of independent random variables $X_1, ..., X_n$ that are i.i.d. with a finite mean $E[X_i] = \mu$ and variance $\sigma^2$ tends to the standard normal as $n \rightarrow \infty$. That is, for $-\infty < a < \infty$:
$$
P\{\frac{X_1 + ... + X_n - n \mu}{\sigma \sqrt{n}} \leq a\} \rightarrow \frac{1}{\sqrt{2 \pi}} \int_{- \infty}^a e^{\frac{-x^2}{2}} dx \text{ as } n \rightarrow \infty
$$

**Strong law of large numbers theorems** state conditions under which a average of a sequence of random variables converges to the expected average. In other words, the average of a sequence of independent random variables having a common distribution will with probability 1 converge to the mean, or expectation, of that distribution. For a sequence of independent random variables $X_1, ..., X_n$ that are i.i.d. with a finite mean $E[X_i] = \mu$, with probability 1:
$$
\frac{X_1 + ... + X_n}{n} \rightarrow \mu \text{ as } n \rightarrow \infty
$$

## Review

Focus on:
- Joint distributions (discrete and continuous)
- Marginal distributions (integrating/summing out variables)
- Conditional distributions (foundation of P(Y|X))
- Independence and what it means

directly connect to:
- Naive Bayes (joint → marginal → conditional)
- Regression (conditional expectation)
- Feature correlations (covariance matrices)
- Generative models (joint distributions)

practice questions:
- What's a marginal distribution and why would you need it?
- What does independence mean for joint distributions?
- How do you find P(X|Y) from joint distribution?

topics and practice
- multivariate normal distribution
- random variable that is the combination of a discrete random variable and a continuous random variable

write code for
- implement the functions like permutations, combinations, bayes
- different distributions
- generate some sample distributions or the dart throwing plot and then calculate the probabilities
- calculate probabilities for 1, 2, 3, 4 random variables
## References

- [[Probability Notes]]
- [[Bayesian Learning]]