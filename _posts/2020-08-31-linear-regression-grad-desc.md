---
title: Gradient Descent for Linear Regression
layout: post
summary: Data extraction from Wikimedia dump
toc: true
comments: true
categories: [Implementation, Machine Learning, Linear Regression]
---

# Implementing Linear Regression with Gradient Descent

This post is my understanding of Linear Regression, Please feel free to comment and point out any errors if seen.

## The Cost Function

The cost function is used to measure the correctness of the current solution(hypothesis), the function
can be mean of squares/square roots of the errors. It is represented as the following

J($\theta_0$, $\theta_1$,..$\theta_n$)

where $\theta_0$ is a constant, $\theta_1$...$\theta_n$ are the parameters of the equation we are trying to solve

    In simple ML terms(I think)
    Each one of the parameter represent the weight of each feature in the dataset, that we are using to build the model

This is the formula for the cost function with mean of square differences.$^0$

$$\frac{1}{2m}\sum_{i=1}^{m}  (h_\theta(x) - y)^2$$

where $h_0(x)$ is the hypothesis or the predicted value for $y$
and $m$ is the number of training examples

A sample pseudocode for the mean of squares of errors would be

- Calculate the sum of square differences / errors between each value $(X*\theta)$ vector and y vector
  - For each training example
    - Multiply the feature values $X_1$, $X_2$,..$X_n$ with it's corresponding weights $\theta_1$, $\theta_2\cdots\theta_n$, and add the constant, $\theta_0$.

    - Subtract the above value from the $y$ target value of that example and square the difference.

  - Sum all the differences / errors

- Take the mean of the differences by the dividing with the number of training examples.

It can be represented like $h_0(x) = \theta_0+\theta_1X_1+\theta_2X_2+\cdots+\theta_nX_n$ where $n$ is the number of features we are using for the problem.

# Gradient Descent

We need to update the parameters $\theta_0,\theta_1, \theta_2\cdots\theta_n$ so that the cost function

$$J(\theta_0, \theta_1,\cdots\theta_n) = \frac{1}{2m}\sum_{i=1}^{m}  (h_\theta(x^i) - y^i)^2$$ can be minimized.

So to find the minimum for the parameters $\theta_0,\theta_1,\theta_2\cdots\theta_n$ the update is performed like below

$$\theta_j := \theta_j *\alpha \frac{\partial}{\partial \theta_j}*J(\theta_0, \theta_1,\cdots\theta_j)$$

Where,

- The `:=` is assignment operator
- The $\theta_j$ is the parameter to update, `j` is the feature index number
- The $\alpha$ is the learning rate
- The $\frac{\partial}{\partial \theta_j} J(\theta_0, \theta_1,\cdots\theta_j)$ is the derivative term of the cost function, it is like `slope`$^2$ of the line `tangent`$^1$ to the curve touching on  where the $\theta$ is present in that curve.

For each feature in the dataset the update has to be done simultaneously for each parameter $\theta$, until the convergence / error given by cost function at its minimum.

## Deriving the derivative term $\frac{\partial}{\partial \theta_j} J(\theta_0, \theta_1,\cdots\theta_j)$

$^3$To simplify the problem I am considering that we have 2 parameters $\theta_0$ and $\theta_1$, our hypothesis $h_0(x)$ function becomes $\theta_0+\theta_1X$

Now let $g(\theta_0, \theta_1)$ be our derivative term

$$g(\theta_0, \theta_1)=J(\theta_0, \theta_1)$$

$$= (\frac{1}{2m}\sum_{i=1}^{m}  (h_\theta(x^i) - y^i)^2)$$

$$=(\frac{1}{2m}\sum_{i=1}^{m}  (\theta_0+\theta_1X^i - y^i)^2)$$

consider $$f(\theta_0, \theta_1) = h_\theta(x^i) - y^i$$

now our equation becomes

$$g(\theta_0, \theta_1)=\frac{1}{2m}\sum_{i=1}^{m} (f(\theta_0, \theta_1)^i)^2$$

subsutituting the value of $f(\theta_0, \theta_1)$ the equation becomes

$$g(f(\theta_0, \theta_1)^i)=\frac{1}{2m}\sum_{i=1}^{m} (\theta_0+\theta_1X^i - y^i)^2 \tag{1}$$

Now let us derive the partial derivative for $(1)$

$$\frac{\partial}{\partial \theta_j}g(f(\theta_0, \theta_1)^i) =\frac{\partial}{\partial \theta_j}\frac{1}{2m}\sum_{i=1}^{m} (f(\theta_0, \theta_1)^i)^2$$

Let `j` be `0`

$$\frac{\partial}{\partial \theta_0}g(f(\theta_0, \theta_1)^i) =\frac{\partial}{\partial \theta_0}\frac{1}{2m}\sum_{i=1}^{m} (f(\theta_0, \theta_1)^i)^2$$

 since we are performing the partial derivative with respect to $\theta_0$ other variables are considered constant, the following is similar to $\frac{\partial}{\partial x}$ of $(x^2+y)$ which is $2x$

$$=\frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i$$

$$=\frac{1}{m}\sum_{i=1}^{m}  (h_\theta(x) - y)$$

This is because of the **chain rule**, when we take derivative of a function like $(1)$, we need to use this formula below

$$\frac{\partial}{\partial \theta_j}g(f(\theta_0, \theta_1)) = \frac{\partial}{\partial \theta_j}g(\theta_0, \theta_1) * \frac{\partial}{\partial \theta_j} f(\theta_0, \theta_1)\tag{2}$$

In case when `j = 0` the partial derivative of $g$ becomes

$$\frac{\partial}{\partial \theta_0}g(\theta_0, \theta_1) =\frac{1}{\cancel2m}*\cancel2(\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i)^{2-1}=\frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i$$

and the partial derivative of $f$ becomes

$$\frac{\partial}{\partial \theta_0}f(\theta_0, \theta_1) = \frac{\partial}{\partial \theta_0}(h_\theta(x^i) - y^i)\tag{3}$$

$$\frac{\partial}{\partial \theta_0}f(\theta_0, \theta_1) = \frac{\partial}{\partial \theta_0}(\theta_0+\theta_1X^i - y^i) = 1$$

since other variables are considered constants, that gives us

$$\frac{\partial}{\partial \theta_j}g(\theta_0, \theta_1) * \frac{\partial}{\partial \theta_j} f(\theta_0, \theta_1)=\frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i * 1 = \frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i$$

Let's start from Equation $(1)$ to perform the partial derivative when `j = 1`

The partial derivative of $g(\theta_0, \theta_1)$ with respect to $\theta_1$ is same from the last derivation but the partial derivative of $f(\theta_0, \theta_1)$ becomes

Consider $(3)$ when `j = 1`

$$\frac{\partial}{\partial \theta_1}f(\theta_1, \theta_1) = \frac{\partial}{\partial \theta_1}(h_\theta(x^i) - y^i) = \frac{\partial}{\partial \theta_1}(\theta_0+\theta_1X^i - y^i)$$

variables other than $\theta_1$ are considered constants, so they become 0 and $\frac{\partial}{\partial \theta_1}\theta_1$ = 1, so our equation becomes

$$\frac{\partial}{\partial \theta_1}f(\theta_0, \theta_1)= 0+1* X^i-0 =X^i$$

and according to the chain rule $(2)$ and replacing the partials

$$\frac{\partial}{\partial \theta_1}g(f(\theta_0, \theta_1)) = \frac{\partial}{\partial \theta_1}g(\theta_0, \theta_1) * \frac{\partial}{\partial \theta_1} f(\theta_0, \theta_1)$$

$$= \frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i * X^i$$

$$= \frac{1}{m}\sum_{i=1}^{m}  (\theta_0+\theta_1X^i - y^i) * X^i$$

Now we can use the derivatives in the Gradient Descent algorithm

$$\theta_j := \theta_j *\alpha \frac{\partial}{\partial \theta_j}*J(\theta_0, \theta_1,\cdots\theta_j)$$

repeat until convergence {
$$\theta_0 := \theta_0 *\alpha \frac{1}{m}\sum_{i=1}^{m}  (\theta_0+\theta_1X^i - y^i)$$

$$\theta_1 := \theta_1 *\alpha \frac{1}{m}\sum_{i=1}^{m}  (\theta_0+\theta_1X^i - y^i)* X^i$$
}

One disadvantage in Gradient Descent is that depending on the position it is initialized at the start, but in linear regression the cost function (mean of sqaured errors) is a convex function (ie) it is in shape of a `bowl` when plotted on the graph.

I tried to implement this in python which can be found [here](https://github.com/mani2106/Algorithm-Implementations)

# Resources and references

- [How to implement a machine learning algorithm](https://machinelearningmastery.com/how-to-implement-a-machine-learning-algorithm/)
- [Understanding math in Machine learning](https://machinelearningmastery.com/techniques-to-understand-machine-learning-algorithms-without-the-background-in-mathematics/)

- $^0$ Most of the content and explanation is from Coursera's  - Machine Learning class

- $^1$ Tangent is a line which touches exactly at one point of a curve.

- $^2$ Slope of a line given any two points on the line is the ratio number of points we need to *rise/descend* and move *away/towards* the origin to the meet the other point.

![ref image](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.lB1cJDzX1MWkf5DcHqewLAHaFj%26pid%3DApi&f=1)

- *Image from [wikihow](http://www.wikihow.com/Find-the-Slope-of-a-Line-Using-Two-Points)*

- $^3$ Derivation referred from [here](https://math.stackexchange.com/questions/70728/partial-derivative-in-gradient-descent-for-two-variables)
