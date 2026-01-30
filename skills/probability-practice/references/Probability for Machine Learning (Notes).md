---
tags:
  - machine-learning
  - textbook
description:
cssclass: default
created_at: 2025-11-29
---
## Ch 4 - 5

The **product rule** or fundamental rule of probability
$$
P(A, B) = P(A \vert B) P(B)
$$

The **sum rule** of probability states that the probability of a random variable $X$ having a value $A$ is equal to the sum of the joint probabilities of $X$ and another random variable $Y$:
$$
P(X = A) = \sum_{y \in Y} P(X = A, Y=y)
$$

The **joint probability** of independent events is found by multiplying probabilities
$$
P(A,B) = P(A)P(B)
$$

The **joint probability** expresses the probability of simultaneous events. The marginal probability describes the probability of a single random variable regardless of other variables. And the conditional probability describes the probability of a random variable given the value of some other random variable.

When two events are mutually exclusive it guarantees independence, but not vice versa. The probability of two non-mutually exclusive events is computed using the inclusion-exclusion rule
$$
P(A \cup B) = P(A) + P(B) - P(A,B)
$$

## Ch 7-9 

A random variable is a value produced by a random process.

A probability distribution is a summary of probabilities for the possible values of a random variable.

We can measure properties of a probability distribution:
- expected value (first moment of the distribution) - mean value of the random variable
- variance (second moment of the distribution) - the spread of values of a random variable from the mean
	- standard deviation is the square root of the variance and it normalizes the value
	- covariance is the variance between two random variables and describes the linear relationship of how two random variables change together
- skewness (third moment)
- kurtosis (fourth moment)


probability mass function is probability distribution function of a discrete random variable. Note that the sum of probabilities given in the probability mass function sum up to one.

The cumulative distribution function of a discrete probability distribution assigns a probability to a discrete random variable that it will have a value less than or equal to a given discrete value.

probability density function is a probability distribution function of a continuous random variable

binary vs. categorical random variables

Bernoulli and Multinoulli discrete probability distributions

The Binomial and Multinomial distributions generalize the Bernoulli and Multinoulli distributions to multiple independent trials, i.e. a sequence of events.

Some continuous distributions you should know: normal, exponential, pareto

Normal distribution is defined the by the mean $\mu$ and the variance $\sigma^2$ or more commonly the standard deviation $\sigma$ which is the average spread from the mean.
- 68-95-99.7 rule - approximate amount of data covered by the 1, 2, 3, standard deviations

The exponential distribution is the continuous equivalent to the geometric distribution for discrete variables. It's parameterized by the scale $\beta$ which is the mean and standard deviation of the distribution, and the rate of change $\lambda$.

## Ch 10

**Probability density** is the relationship between observations and their probability

The shape of the probability density is called the **probability distribution**.

The calculation of the probabilities for specific outcomes of a random variable is the **probability density function or PDF**.

The probability density is estimated by the process of probability density estimation.

Historgrams
## Ch 11 - Maximum Likelihood Estimate

## Ch 16 - Introduction to Bayes Theorem

- A way to calculate the conditional probability without the joint probability
- Typically we calculate the denominator value, viz. the evidence, using the **law of total probability**
- Bayes' theorem as a binary classifier. Suppose the posterior is $P(A \vert B)$
	- likelihood is the true positive rate (sensitivity or recall)
	- P(A | B) is the precision
	- P(not B | not A) is the true negative rate (specificity)

## Ch 17 - Bayes Theorem and Machine Learning

$$
P(h \vert D) = \frac{P(D \vert h)P(h)}{P(D)}
$$
- Find the hypothesis (model) that best describes the observed data
- Maximum a Posteriori (MAP) probabilistic framework
	- underlies logistic and linear regression
- **Bayes Optimal Classifier** defines the best possible prediction that can be made for a set of models on a dataset
	- BOC makes the most probable prediction for a new example given the training data
	- BOC is different from MAP that finds the most probable hypothesis

$$
P(v_j \vert D) = \sum^{h \in H} P(v_j \vert h_i) P(h_i \vert D)
$$
	- BOC selects the classification with maximum probability
$$
\text{max } \sum^{h \in H} P(v_j \vert h_i)P(h_i \vert D)
$$
	- No other method can outperform the BOC for the same hypothesis space and prior data on average
	- BOC's error is referred to as **Bayes Error** which is the minimum possible error that can be made when making predictions
	- BOC is computationally expensive. Two simplifications to the approach:
		- Gibbs sampling - randomly sample the hypotheses biased on their posterior probability
		- Naive Bayes - assume the variables are conditionally independent
- Bayes theorem can be used to describe the proportional relationship between the data and a hypothesis
	- Testing different models on a dataset is estimating the probability of each hypothesis in the hypothesis space being true given the observed data
	- Since $P(D)$ is used to assess each hypothesis, it is constant can be eliminated from the calculation
	- We can also remove $P(h)$ if each hypothesis is equally likely
$$
\text{max } h \in H \text{ where } P(h \vert D) = P(D \vert h)P(h)
$$
- Optimizing $\text{max } h \in H \text{ where } P(h \vert D) = P(D \vert h)$ is referred to as **density estimation**: select the a probability distribution function and the parameters of that distribution that best explains the joint probability of the observed data $X$, i.e. feature set. Techniques for solving this problem:
	- Maximum a Posteriori estimation (Bayesian method), MAP estimation
		- maximize the quantity $P(\theta \vert X) = P(X \vert \theta) P(\theta)$
		- the result conditional probability is the likelihood of observing the data given the model parameters
		- similar to MLE with the addition of the prior probability over the distribution and parameters. MAP and MLE converge to the same solution if we assume that all values of $\theta$ (the parameters) are equally likely (uniform prior)
	- Maximum Likelihood Estimation (MLE) (frequentist method)
		- maximize the probability of observing the data from the joint probability distribution given a specific probability distribution and its parameters $P(X, \theta)$. So MAX finds the parameters $\theta$ that $\text{max } P(X;\theta)$
- MAP provides a Bayesian framework for fitting model parameters to training data
- Use MAP when you have some meaningful prior information. Use MLE when there is no such prior information.
- L2 regularization is equivalent to MAP inference with Gaussian prior on the weights
- 
## Ch 18 - How to Develop a Naive Bayes Classifier

- We can frame the problem of classification as calculating the conditional probability of a class label given the data sample
- In practice Bayes' Theorem an enormous amount of data. Naive Bayes assume the variables are conditionally independent which makes the calculation tractable even though it is unrealistic
- Basically, calculated the conditional probability for each class label and return the label with the highest probability
$$
P(y_i \vert x_1, x_2, ..., x_n) = \frac{P(x_1, x_2, ..., x_n \vert y_i)P(y_i)}{P(x_1, x_2, ..., x_n)}
$$
- where $y_i$ is the label and the $x_1, x_2, ...,x_n$ are the data samples. It's easy to calculate $P(y_i)$, but infeasible to calculate $P(x_1,x_2,...,x_n)$ without a very large dataset.
- Naive Bayes simplifies the calculation to get around this issue. Naive Bayes assumes that all the variables $x_1, x_2, ...,x_n$ are conditionally independent given the label $y_i$.
$$
P(y_i \vert x_1, x_2, ..., x_n) = P(x_1 \vert y_i)P(x_2 \vert y_i)...P(x_n \vert y_i)P(y_i)
$$
- Notice that the denominator of Bayes' Theorem $P(x_1,x_2,...,x_n)$ has also been removed because it is constant for all labels.
- The resulting decision rule is the MAP decision rule
- Calculating $P(y_i)$ is easy
$$
P(y_i) = \frac{\text{examples with }y_i}{\text{total examples}}
$$
- we estimate the conditional probability of a feature value given the class label $P(x_n \vert y_i)$ from the data by estimating the distribution features
	- Binomial distribution for binary features
	- Multinomial distribution for categorical features
	- Gaussian distribution for numeric features
- avoid numerical underflow using log
	- the multiplication of many small values can become numerically unstable
	- so we can change $P(x_1 \vert y_i)P(x_2 \vert y_i)...P(x_n \vert y_i)P(y_i)$ to 
$$
P(y_i \vert x_1,x_2,...,x_n) = \log(P(x_1 \vert y_i)) + \log(P(x_2 \vert y_i)) + ... + \log(P(x_n \vert y_i)) + \log(P(y_i))
$$





## Book

![[probability_for_machine_learning.pdf]]