---
title: Gradient Descent for Linear Regression
layout: post
summary: Data extraction from Wikimedia dump
toc: true
comments: true
image: images/demo_grad.gif
categories: [Implementation, Machine Learning, Linear Regression]
---

# Implementing Linear Regression with Gradient Descent

This post is my understanding of Linear Regression, Please feel free to comment and point out any errors if seen.

## The Cost Function

The cost function is used to measure the correctness of the current solution(hypothesis), the function
can be mean of squares/square roots of the errors. It is represented as the following

<code>J($\theta_0$, $\theta_1$,..$\theta_n$)</code>

where $\theta_0$ is a constant, $\theta_1$...$\theta_n$ are the parameters of the equation we are trying to solve

    In simple ML terms(I think)
    Each one of the parameter represent the weight of each feature in the dataset, that we are using to build the model

This is the formula for the cost function with mean of square differences.$^0$

<code>$$\frac{1}{2m}\sum_{i=1}^{m}  (h_\theta(x) - y)^2$$</code>

where $h_0(x)$ is the hypothesis or the predicted value for $y$
and $m$ is the number of training examples

A sample pseudocode for the mean of squares of errors would be

- Calculate the sum of square differences / errors between each value <code>$(X*\theta)$</code> vector and <code>y</code> vector
  - For each training example
    - Multiply the feature values <code>$X_1$, $X_2$,..$X_n$</code> with it's corresponding weights <code>$\theta_1$, $\theta_2$$\cdots$$\theta_n$</code> and add the constant <code>$\theta_0$</code>

    - Subtract the above value from the <code>$y$</code> target value of that example and square the difference.

  - Sum all the differences / errors

- Take the mean of the differences by the dividing with the number of training examples.

It can be represented like <code>$h_0(x) = \theta_0+\theta_1X_1+\theta_2X_2+\cdots+\theta_nX_n$</code> where $n$ is the number of features we are using for the problem.

# Gradient Descent

We need to update the parameters <code>$\theta_0$, $\theta_1$, $\theta_2$$\cdots$$\theta_n$</code> so that the cost function

<code>$$J(\theta_0, \theta_1,\cdots\theta_n) = \frac{1}{2m}\sum_{i=1}^{m}  (h_\theta(x^i) - y^i)^2$$</code> can be minimized.

So to find the minimum for the parameters <code>$\theta_0$, $\theta_1$, $\theta_2$$\cdots$$\theta_n$</code> the update is performed like below

<code>$$\theta_j := \theta_j *\alpha \frac{\partial}{\partial \theta_j}*J(\theta_0, \theta_1,\cdots\theta_j)$$</code>

Where,

- The `:=` is assignment operator
- The <code>$\theta_j$</code> is the parameter to update, `j` is the feature index number
- The <code>$\alpha$</code> is the learning rate
- The <code>$\frac{\partial}{\partial \theta_j} J(\theta_0, \theta_1,\cdots\theta_j)$</code> is the derivative term of the cost function, it is like `slope`$^2$ of the line `tangent`$^1$ to the curve touching on  where the <code>$\theta$</code> is present in that curve.

For each feature in the dataset the update has to be done simultaneously for each parameter <code>$\theta$</code>, until the convergence / error given by cost function at its minimum.

## Deriving the derivative term <code>$\frac{\partial}{\partial \theta_j} J(\theta_0, \theta_1,\cdots\theta_j)$</code>

$^3$To simplify the problem I am considering that we have 2 parameters $\theta_0$ and $\theta_1$, our hypothesis $h_0(x)$ function becomes $\theta_0+\theta_1X$

Now let $g(\theta_0, \theta_1)$ be our derivative term

<code>$$g(\theta_0, \theta_1)=J(\theta_0, \theta_1)$$</code>

<code>$$= (\frac{1}{2m}\sum_{i=1}^{m}  (h_\theta(x^i) - y^i)^2)$$</code>

<code>$$=(\frac{1}{2m}\sum_{i=1}^{m}  (\theta_0+\theta_1X^i - y^i)^2)$$</code>

consider <code>$$f(\theta_0, \theta_1) = h_\theta(x^i) - y^i$$</code>

now our equation becomes

<code>$$g(\theta_0, \theta_1)=\frac{1}{2m}\sum_{i=1}^{m} (f(\theta_0, \theta_1)^i)^2$$</code>

subsutituting the value of $f(\theta_0, \theta_1)$ the equation becomes

<code>$$g(f(\theta_0, \theta_1)^i)=\frac{1}{2m}\sum_{i=1}^{m} (\theta_0+\theta_1X^i - y^i)^2 \tag{1}$$</code>

Now let us derive the partial derivative for $(1)$

<code>$$\frac{\partial}{\partial \theta_j}g(f(\theta_0, \theta_1)^i) =\frac{\partial}{\partial \theta_j}\frac{1}{2m}\sum_{i=1}^{m} (f(\theta_0, \theta_1)^i)^2$$</code>

Let `j` be `0`

<code>$$\frac{\partial}{\partial \theta_0}g(f(\theta_0, \theta_1)^i) =\frac{\partial}{\partial \theta_0}\frac{1}{2m}\sum_{i=1}^{m} (f(\theta_0, \theta_1)^i)^2$$</code>

 since we are performing the partial derivative with respect to $\theta_0$ other variables are considered constant, the following is similar to $\frac{\partial}{\partial x}$ of $(x^2+y)$ which is $2x$

<code>$$=\frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i$$</code>

<code>$$=\frac{1}{m}\sum_{i=1}^{m}  (h_\theta(x) - y)$$</code>

This is because of the **chain rule**, when we take derivative of a function like $(1)$, we need to use this formula below

<code>$$\frac{\partial}{\partial \theta_j}g(f(\theta_0, \theta_1)) = \frac{\partial}{\partial \theta_j}g(\theta_0, \theta_1) * \frac{\partial}{\partial \theta_j} f(\theta_0, \theta_1)\tag{2}$$</code>

In case when `j = 0` the partial derivative of $g$ becomes

<code>$$\frac{\partial}{\partial \theta_0}g(\theta_0, \theta_1) =\frac{1}{\cancel2m}*\cancel2(\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i)^{2-1}=\frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i$$</code>

and the partial derivative of $f$ becomes

<code>$$\frac{\partial}{\partial \theta_0}f(\theta_0, \theta_1) = \frac{\partial}{\partial \theta_0}(h_\theta(x^i) - y^i)\tag{3}$$</code>

<code>$$\frac{\partial}{\partial \theta_0}f(\theta_0, \theta_1) = \frac{\partial}{\partial \theta_0}(\theta_0+\theta_1X^i - y^i) = 1$$</code>

since other variables are considered constants, that gives us

<code>$$\frac{\partial}{\partial \theta_j}g(\theta_0, \theta_1) * \frac{\partial}{\partial \theta_j} f(\theta_0, \theta_1)=\frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i * 1 = \frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i$$</code>

Let's start from Equation $(1)$ to perform the partial derivative when `j = 1`

The partial derivative of $g(\theta_0, \theta_1)$ with respect to $\theta_1$ is same from the last derivation but the partial derivative of $f(\theta_0, \theta_1)$ becomes

Consider $(3)$ when `j = 1`

<code>$$\frac{\partial}{\partial \theta_1}f(\theta_1, \theta_1) = \frac{\partial}{\partial \theta_1}(h_\theta(x^i) - y^i) = \frac{\partial}{\partial \theta_1}(\theta_0+\theta_1X^i - y^i)$$</code>

variables other than $\theta_1$ are considered constants, so they become 0 and $\frac{\partial}{\partial \theta_1}\theta_1$ = 1, so our equation becomes

<code>$$\frac{\partial}{\partial \theta_1}f(\theta_0, \theta_1)= 0+1* X^i-0 =X^i$$</code>

and according to the chain rule $(2)$ and replacing the partials

<code>$$\frac{\partial}{\partial \theta_1}g(f(\theta_0, \theta_1)) = \frac{\partial}{\partial \theta_1}g(\theta_0, \theta_1) * \frac{\partial}{\partial \theta_1} f(\theta_0, \theta_1)$$</code>

<code>$$= \frac{1}{m}\sum_{i=1}^{m}  f(\theta_0, \theta_1)^i * X^i$$</code>

<code>$$= \frac{1}{m}\sum_{i=1}^{m}  (\theta_0+\theta_1X^i - y^i) * X^i$$</code>

Now we can use the derivatives in the Gradient Descent algorithm

<code>$$\theta_j := \theta_j *\alpha \frac{\partial}{\partial \theta_j}*J(\theta_0, \theta_1,\cdots\theta_j)$$</code>

repeat until convergence {
<code>$$\theta_0 := \theta_0 *\alpha \frac{1}{m}\sum_{i=1}^{m}  (\theta_0+\theta_1X^i - y^i)$$</code>

<code>$$\theta_1 := \theta_1 *\alpha \frac{1}{m}\sum_{i=1}^{m}  (\theta_0+\theta_1X^i - y^i)* X^i$$</code>
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
