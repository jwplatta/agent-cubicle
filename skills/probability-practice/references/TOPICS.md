- probability
	- practice problems on the inclusion-exclusion principle for the union of n events (1, 2, 3)
	- joint probabilities
	- bayesian probability
	- conditional probability
	- marginalizing or summing out
		- finding the marginal probability from a joint probability
	- counting
		- permutations
		- combinations
	- dart throwing examples
	- law of total probability
	- multiplication rule
	- calculate probabilities for 1, 2, 3, 4 random variables
	- expectation (continuous and discrete random variables)
		- 1,2,3, n random variables
	- variance
	- standard deviation
	- covariance and correlation
	- different distributions and their properties
		- given a description of a problem, what distribution to use?
		- binomial distribution
		- multinomial distribution
		- multivariate normal distribution

## Probability (Highest Priority)

You must be fluent in:
* Conditional probability
* Bayes' rule (intuition > formula)
* Expectation, variance, covariance
* Law of large numbers
* Central limit theorem (and when it fails)
* Common distributions:
  * Normal
  * Lognormal
  * Bernoulli / Binomial
  * Multinomial
  * Poisson
  * Exponential

You should be able to:
* Compute expectations quickly
* Reason about tails
	* Reasoning about tails means:
		- Understanding that averages hide ruin
		- Knowing when rare events dominate outcomes
		- Recognizing hidden short-vol exposure
* Explain independence vs correlation
## Statistics

Bare minimum:
* Sample mean / variance
* Bias vs variance
	* In finance, generally you're want lower variance and accept higher bias
* Overfitting
* Hypothesis testing intuition (not formulas)
	* p-values are **not** the probability the hypothesis is true
	* Small samples exaggerate effects
	* Statistical significance ≠ economic significance
	* Markets produce clustered volatility
	* Observations are not independent
	* Standard tests lie more often than people think
* Confidence intervals
* p-values (and why they lie)
* Multiple testing / false discovery
	* If you test enough ideas, **something will look good by chance**.
	* A false discovery is: A strategy that looks statistically significant but has no real edge
	* Look out for:
		* This could just be a false positive
		* I need stronger evidence because I’ve tested many variants
		* I'd adjust my confidence downward due to multiple testing
		* make sure you hold a test dataset

#### Bayesian Reasoning & Conditional Probability

Core skill: Applying Bayes’ theorem, interpreting conditional probabilities, updating beliefs from data.

Problems from document:
- Bayesian coin flipping: probability of heads after observations
- COVID test accuracy (true positive / false positive / base rate)
- Which coin is more likely biased given observed flips
- Conditional probabilities involving dice and coins
- P(X+Y > 0 \mid X > 0) for normal random variables
#### Probability Distributions & Approximations

Core skill: Working with binomial, Gaussian, and normal approximations; sums of random variables.

Problems from document:
- Gaussian approximation to binomial hypothesis testing
- Sum of two normal random variables (same and different variances)
- Coin flipped 400 times, hypothesis test for bias
- Range of variance given bounded distributions

#### Expectation & Linearity of Expectation

Core skill: Computing expectations efficiently, often without full distributions.

Problems from document:
- Expected number of man–woman adjacent pairs in a lineup
- Expected number of different-color adjacent pairs with red/blue balls
- Expected time to cross bridges with reset probability
- Expected value of dice re-rolling strategies
- Fair value of a field with probabilistic payoffs


#### Covariance & Correlation

Core skill: Computing covariance of dependent counts and interpreting correlation.

Problems from document:
- Covariance of number of 2s and 3s in dice rolls
- Correlation between dice roll outcomes
- Covariance of regression coefficients
- Covariance of coefficients in linear regression with correlated predictors
