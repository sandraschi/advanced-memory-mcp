#!/usr/bin/env python3
"""Phase 3: Mathematics skills with LaTeX formulas."""

from pathlib import Path


def generate_skill_md(name, title, description, topics, formulas):
    """Generate SKILL.md with LaTeX math."""
    topics_list = "\n    - ".join(topics)
    
    return f"""---
name: {title}
description: {description}
version: 1.0.0
category: mathematics
difficulty: advanced
license: MIT
allowed_tools: [web_search, advanced-memory-mcp]
---

# {title}

You are an expert mathematician with deep knowledge of theory, proofs, and practical applications.

## When to Use This Skill

Activate when the user asks about:
    - {topics_list}

{formulas}

## Instructions

1. **Assess** mathematical background and comfort level
2. **Explain** concepts with clear definitions
3. **Provide** step-by-step worked examples
4. **Use** appropriate mathematical notation (LaTeX)
5. **Connect** theory to practical applications
6. **Build** understanding progressively from basics
7. **Offer** practice problems when helpful

## Response Guidelines

- Start with intuitive explanations before formal definitions
- Use LaTeX for all mathematical expressions
- Provide visual descriptions when helpful
- Show worked examples step-by-step
- Highlight common mistakes and misconceptions
- Connect to related mathematical concepts
- Suggest resources for deeper study

## Teaching Philosophy

- **Rigor with clarity:** Precise but accessible
- **Build intuition first:** Why before how
- **Connect concepts:** Show relationships between topics
- **Practice matters:** Theory + examples + problems
- **Visual thinking:** Geometric and graphical insights

---

**Category:** mathematics  
**Difficulty:** Advanced  
**Version:** 1.0.0  
**Created:** 2025-10-21
"""


MATH_SKILLS = [
    {
        "name": "calculus-tutor",
        "title": "Calculus Tutor (Single & Multivariable)",
        "description": "Comprehensive calculus expert covering limits, derivatives, integrals, sequences, series, and multivariable calculus with rigorous proofs and practical applications",
        "topics": [
            "Limits and continuity",
            "Derivatives and differentiation rules",
            "Integration techniques",
            "Fundamental Theorem of Calculus",
            "Sequences and series convergence",
            "Taylor and Maclaurin series",
            "Multivariable calculus and partial derivatives",
            "Vector calculus (gradient, divergence, curl)"
        ],
        "formulas": """## Core Concepts

### Fundamental Theorem of Calculus

$$
\\frac{d}{dx}\\left[\\int_{a}^{x} f(t)\\,dt\\right] = f(x)
$$

$$
\\int_{a}^{b} f(x)\\,dx = F(b) - F(a) \\text{ where } F'(x) = f(x)
$$

### Common Derivatives

- Power rule: $\\frac{d}{dx}[x^n] = nx^{n-1}$
- Product rule: $(fg)' = f'g + fg'$
- Quotient rule: $\\left(\\frac{f}{g}\\right)' = \\frac{f'g - fg'}{g^2}$
- Chain rule: $\\frac{d}{dx}[f(g(x))] = f'(g(x)) \\cdot g'(x)$

### Integration Techniques

**U-substitution:**
$$
\\int f(g(x))g'(x)\\,dx = \\int f(u)\\,du \\text{ where } u=g(x)
$$

**Integration by parts:**
$$
\\int u\\,dv = uv - \\int v\\,du
$$

### Taylor Series

$$
f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n
$$

### Multivariable

Gradient: $\\nabla f = \\left(\\frac{\\partial f}{\\partial x}, \\frac{\\partial f}{\\partial y}, \\frac{\\partial f}{\\partial z}\\right)$
"""
    },
    {
        "name": "linear-algebra-expert",
        "title": "Linear Algebra Expert",
        "description": "Expert in vector spaces, matrices, linear transformations, eigenvalues, and applications to data science and machine learning",
        "topics": [
            "Vector spaces and subspaces",
            "Linear transformations and matrices",
            "Eigenvalues and eigenvectors",
            "Matrix decompositions (LU, QR, SVD)",
            "Inner products and orthogonality",
            "Determinants and inverses",
            "Applications to machine learning",
            "Numerical linear algebra"
        ],
        "formulas": """## Core Concepts

### Matrix Multiplication

For matrices $A_{m \\times n}$ and $B_{n \\times p}$:
$$
(AB)_{ij} = \\sum_{k=1}^{n} a_{ik}b_{kj}
$$

### Eigenvalues and Eigenvectors

For matrix $A$ and vector $\\mathbf{v}$:
$$
A\\mathbf{v} = \\lambda\\mathbf{v}
$$

Characteristic polynomial:
$$
\\det(A - \\lambda I) = 0
$$

### Singular Value Decomposition (SVD)

$$
A = U\\Sigma V^T
$$

Where $U$ and $V$ are orthogonal, $\\Sigma$ is diagonal.

### Inner Product

$$
\\langle \\mathbf{u}, \\mathbf{v} \\rangle = \\sum_{i=1}^{n} u_i v_i = \\mathbf{u}^T\\mathbf{v}
$$

### Determinant Properties

- $\\det(AB) = \\det(A)\\det(B)$
- $\\det(A^T) = \\det(A)$
- $\\det(A^{-1}) = \\frac{1}{\\det(A)}$
"""
    },
    {
        "name": "statistics-probability-guide",
        "title": "Statistics and Probability Guide",
        "description": "Comprehensive statistics expert covering probability theory, distributions, hypothesis testing, regression, and Bayesian methods",
        "topics": [
            "Probability fundamentals and axioms",
            "Random variables and distributions",
            "Expected value and variance",
            "Central Limit Theorem",
            "Hypothesis testing and p-values",
            "Confidence intervals",
            "Regression analysis",
            "Bayesian statistics"
        ],
        "formulas": """## Core Concepts

### Probability Axioms

1. $P(A) \\geq 0$ for all events $A$
2. $P(S) = 1$ where $S$ is sample space
3. $P(A \\cup B) = P(A) + P(B)$ if $A \\cap B = \\emptyset$

### Bayes' Theorem

$$
P(A|B) = \\frac{P(B|A)P(A)}{P(B)}
$$

### Expected Value and Variance

$$
E[X] = \\sum_{i} x_i P(X=x_i) \\quad \\text{or} \\quad \\int_{-\\infty}^{\\infty} x f(x)\\,dx
$$

$$
\\text{Var}(X) = E[(X - \\mu)^2] = E[X^2] - (E[X])^2
$$

### Normal Distribution

$$
f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}
$$

### Central Limit Theorem

$$
\\frac{\\bar{X} - \\mu}{\\sigma/\\sqrt{n}} \\xrightarrow{d} N(0,1)
$$

### Linear Regression

$$
\\hat{y} = \\beta_0 + \\beta_1 x
$$

Where: $\\beta_1 = \\frac{\\text{Cov}(X,Y)}{\\text{Var}(X)}$
"""
    },
    {
        "name": "abstract-algebra-specialist",
        "title": "Abstract Algebra Specialist",
        "description": "Expert in groups, rings, fields, and algebraic structures with applications to cryptography and number theory",
        "topics": [
            "Group theory and symmetry",
            "Rings and ideals",
            "Fields and field extensions",
            "Homomorphisms and isomorphisms",
            "Quotient structures",
            "Galois theory",
            "Applications to cryptography",
            "Representation theory"
        ],
        "formulas": """## Core Definitions

### Group Axioms

A group $(G, *)$ satisfies:
1. **Closure:** $a * b \\in G$ for all $a,b \\in G$
2. **Associativity:** $(a * b) * c = a * (b * c)$
3. **Identity:** $\\exists e \\in G: a * e = e * a = a$
4. **Inverse:** $\\forall a \\in G, \\exists a^{-1}: a * a^{-1} = e$

### Ring Definition

A ring $(R, +, \\cdot)$ has:
- $(R, +)$ is an abelian group
- $(R, \\cdot)$ is associative
- Distributivity: $a(b+c) = ab + ac$

### Lagrange's Theorem

For finite group $G$ and subgroup $H$:
$$
|G| = |H| \\cdot [G:H]
$$

The order of subgroup divides order of group.

### Homomorphism

$$
\\phi(a * b) = \\phi(a) \\circ \\phi(b)
$$

Kernel: $\\ker(\\phi) = \\{g \\in G : \\phi(g) = e\\}$
"""
    },
    {
        "name": "number-theory-explorer",
        "title": "Number Theory Explorer",
        "description": "Number theory expert covering primes, divisibility, modular arithmetic, Diophantine equations, and cryptographic applications",
        "topics": [
            "Prime numbers and primality testing",
            "Divisibility and GCD/LCM",
            "Modular arithmetic",
            "Chinese Remainder Theorem",
            "Fermat's Little Theorem",
            "Euler's totient function",
            "Quadratic reciprocity",
            "Cryptographic applications (RSA)"
        ],
        "formulas": """## Fundamental Theorems

### Fundamental Theorem of Arithmetic

Every integer $n > 1$ has unique prime factorization:
$$
n = p_1^{a_1} p_2^{a_2} \\cdots p_k^{a_k}
$$

### Euclidean Algorithm

$$
\\gcd(a,b) = \\gcd(b, a \\bmod b)
$$

### Fermat's Little Theorem

If $p$ is prime and $\\gcd(a,p) = 1$:
$$
a^{p-1} \\equiv 1 \\pmod{p}
$$

### Euler's Totient Function

$$
\\phi(n) = n \\prod_{p|n}\\left(1 - \\frac{1}{p}\\right)
$$

For coprime $a$ and $n$:
$$
a^{\\phi(n)} \\equiv 1 \\pmod{n}
$$

### Chinese Remainder Theorem

System $x \\equiv a_i \\pmod{n_i}$ has unique solution modulo $N = \\prod n_i$ when $\\gcd(n_i, n_j) = 1$.
"""
    },
    {
        "name": "topology-geometry-guide",
        "title": "Topology and Geometry Guide",
        "description": "Expert in point-set topology, algebraic topology, differential geometry, and geometric intuition for abstract concepts",
        "topics": [
            "Metric spaces and topological spaces",
            "Continuity and homeomorphisms",
            "Compactness and connectedness",
            "Fundamental group and homotopy",
            "Manifolds and differential geometry",
            "Euler characteristic",
            "Knot theory basics",
            "Geometric visualization"
        ],
        "formulas": """## Fundamental Concepts

### Metric Space

A metric $d: X \\times X \\to \\mathbb{R}$ satisfies:
1. $d(x,y) \\geq 0$ with equality iff $x = y$
2. $d(x,y) = d(y,x)$ (symmetry)
3. $d(x,z) \\leq d(x,y) + d(y,z)$ (triangle inequality)

### Open Ball

$$
B_r(x) = \\{y \\in X : d(x,y) < r\\}
$$

### Euler Characteristic

For polyhedron:
$$
V - E + F = 2
$$

For surface: $\\chi = 2 - 2g$ where $g$ is genus.

### Fundamental Group

$$
\\pi_1(X, x_0) = \\{\\text{homotopy classes of loops based at } x_0\\}
$$

### Differential Forms

On manifold $M$, the exterior derivative:
$$
d: \\Omega^k(M) \\to \\Omega^{k+1}(M)
$$

Satisfies $d^2 = 0$.
"""
    },
    {
        "name": "mathematical-proofs-mentor",
        "title": "Mathematical Proofs Mentor",
        "description": "Expert in proof techniques, mathematical reasoning, and rigorous argumentation for students learning to write proofs",
        "topics": [
            "Direct proofs",
            "Proof by contradiction",
            "Proof by induction (weak and strong)",
            "Contrapositive proofs",
            "Existence and uniqueness proofs",
            "Proof writing style and clarity",
            "Common proof patterns",
            "Verification and error checking"
        ],
        "formulas": """## Proof Techniques

### Mathematical Induction

**Base case:** Prove $P(1)$ is true.

**Inductive step:** Assume $P(k)$ true, prove $P(k+1)$ true.

**Conclusion:** $P(n)$ true for all $n \\geq 1$.

**Example:** Prove $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$

### Proof by Contradiction

1. Assume negation of statement
2. Derive logical contradiction
3. Conclude original statement must be true

**Example:** $\\sqrt{2}$ is irrational

Assume $\\sqrt{2} = \\frac{p}{q}$ in lowest terms.
Then $2q^2 = p^2$, so $p$ is even, say $p = 2k$.
Then $2q^2 = 4k^2$, so $q^2 = 2k^2$, thus $q$ is even.
Contradiction: $\\frac{p}{q}$ not in lowest terms! $\\Box$

### Contrapositive

To prove $P \\Rightarrow Q$, prove $\\neg Q \\Rightarrow \\neg P$.

Logically equivalent: $(P \\Rightarrow Q) \\equiv (\\neg Q \\Rightarrow \\neg P)$
"""
    },
    {
        "name": "differential-equations-solver",
        "title": "Differential Equations Solver",
        "description": "Expert in ODEs and PDEs covering solution methods, qualitative analysis, and applications to physics and engineering",
        "topics": [
            "First-order ODEs (separable, linear, exact)",
            "Second-order linear ODEs",
            "Laplace transforms",
            "Systems of differential equations",
            "Partial differential equations",
            "Boundary value problems",
            "Stability analysis",
            "Numerical methods (Euler, Runge-Kutta)"
        ],
        "formulas": """## Ordinary Differential Equations

### First-Order Linear ODE

$$
\\frac{dy}{dx} + P(x)y = Q(x)
$$

**Solution:** $y = e^{-\\int P\\,dx}\\left(\\int Q e^{\\int P\\,dx}\\,dx + C\\right)$

### Second-Order Linear with Constant Coefficients

$$
ay'' + by' + cy = 0
$$

**Characteristic equation:** $ar^2 + br + c = 0$

**Solutions depend on discriminant** $\\Delta = b^2 - 4ac$:
- $\\Delta > 0$: $y = C_1e^{r_1x} + C_2e^{r_2x}$
- $\\Delta = 0$: $y = (C_1 + C_2x)e^{rx}$
- $\\Delta < 0$: $y = e^{\\alpha x}(C_1\\cos(\\beta x) + C_2\\sin(\\beta x))$

### Laplace Transform

$$
\\mathcal{L}\\{f(t)\\} = F(s) = \\int_0^{\\infty} e^{-st}f(t)\\,dt
$$

### Heat Equation (PDE)

$$
\\frac{\\partial u}{\\partial t} = k\\frac{\\partial^2 u}{\\partial x^2}
$$
"""
    },
    {
        "name": "discrete-mathematics-expert",
        "title": "Discrete Mathematics Expert",
        "description": "Expert in combinatorics, graph theory, discrete probability, and algorithms with applications to computer science",
        "topics": [
            "Combinatorics (permutations, combinations)",
            "Graph theory (trees, paths, cycles)",
            "Recurrence relations",
            "Generating functions",
            "Discrete probability",
            "Boolean algebra and logic circuits",
            "Algorithm analysis and complexity",
            "Number theory applications"
        ],
        "formulas": """## Combinatorial Formulas

### Permutations and Combinations

$$
P(n,r) = \\frac{n!}{(n-r)!} \\quad C(n,r) = \\binom{n}{r} = \\frac{n!}{r!(n-r)!}
$$

### Binomial Theorem

$$
(x+y)^n = \\sum_{k=0}^{n} \\binom{n}{k} x^{n-k}y^k
$$

### Recurrence Relations

Fibonacci: $F_n = F_{n-1} + F_{n-2}$ with $F_0=0, F_1=1$

**Closed form:** $F_n = \\frac{\\phi^n - \\psi^n}{\\sqrt{5}}$ where $\\phi = \\frac{1+\\sqrt{5}}{2}$

### Graph Theory

Handshaking lemma:
$$
\\sum_{v \\in V} \\deg(v) = 2|E|
$$

Euler's formula for planar graphs: $V - E + F = 2$

### Generating Functions

For sequence $\\{a_n\\}$:
$$
G(x) = \\sum_{n=0}^{\\infty} a_n x^n
$$
"""
    },
    {
        "name": "real-analysis-fundamentals",
        "title": "Real Analysis Fundamentals",
        "description": "Rigorous analysis expert covering limits, continuity, sequences, series, and measure theory foundations",
        "topics": [
            "Real number completeness",
            "Sequences and convergence",
            "Series convergence tests",
            "Continuous functions",
            "Uniform convergence",
            "Riemann integration",
            "Measure theory basics",
            "Metric space topology"
        ],
        "formulas": """## Rigorous Foundations

### Limit Definition (ε-δ)

$$
\\lim_{x \\to a} f(x) = L \\iff \\forall \\varepsilon > 0, \\exists \\delta > 0: 0 < |x-a| < \\delta \\Rightarrow |f(x)-L| < \\varepsilon
$$

### Sequence Convergence

$$
\\lim_{n\\to\\infty} a_n = L \\iff \\forall \\varepsilon > 0, \\exists N: n > N \\Rightarrow |a_n - L| < \\varepsilon
$$

### Cauchy Sequence

$$
\\forall \\varepsilon > 0, \\exists N: m,n > N \\Rightarrow |a_m - a_n| < \\varepsilon
$$

### Convergence Tests

**Ratio test:** $\\lim_{n\\to\\infty} \\left|\\frac{a_{n+1}}{a_n}\\right| < 1 \\Rightarrow$ series converges

**Root test:** $\\limsup_{n\\to\\infty} \\sqrt[n]{|a_n|} < 1 \\Rightarrow$ series converges

### Uniform Convergence

$$
\\forall \\varepsilon > 0, \\exists N: n > N, x \\in D \\Rightarrow |f_n(x) - f(x)| < \\varepsilon
$$
"""
    },
    {
        "name": "complex-analysis-expert",
        "title": "Complex Analysis Expert",
        "description": "Expert in complex functions, contour integration, residue theory, and conformal mappings",
        "topics": [
            "Complex numbers and functions",
            "Analytic functions and Cauchy-Riemann equations",
            "Contour integration",
            "Cauchy's theorem and integral formula",
            "Residue theorem and applications",
            "Laurent series",
            "Conformal mappings",
            "Applications to physics and engineering"
        ],
        "formulas": """## Complex Analysis

### Cauchy-Riemann Equations

For $f(z) = u(x,y) + iv(x,y)$ to be analytic:
$$
\\frac{\\partial u}{\\partial x} = \\frac{\\partial v}{\\partial y}, \\quad \\frac{\\partial u}{\\partial y} = -\\frac{\\partial v}{\\partial x}
$$

### Cauchy's Integral Formula

For analytic $f$ inside contour $C$:
$$
f(z_0) = \\frac{1}{2\\pi i}\\oint_C \\frac{f(z)}{z-z_0}\\,dz
$$

### Residue Theorem

$$
\\oint_C f(z)\\,dz = 2\\pi i \\sum_{k} \\text{Res}(f, z_k)
$$

### Laurent Series

$$
f(z) = \\sum_{n=-\\infty}^{\\infty} a_n(z-z_0)^n
$$

Residue is $a_{-1}$ coefficient.
"""
    },
    {
        "name": "numerical-methods-expert",
        "title": "Numerical Methods Expert",
        "description": "Computational mathematics expert for numerical solutions, approximations, error analysis, and scientific computing",
        "topics": [
            "Root finding (Newton-Raphson, bisection)",
            "Numerical integration (Simpson's, Gaussian quadrature)",
            "Numerical differentiation",
            "Linear system solvers",
            "Interpolation and approximation",
            "ODE solvers (Euler, Runge-Kutta)",
            "Error analysis and stability",
            "Optimization algorithms"
        ],
        "formulas": """## Numerical Algorithms

### Newton-Raphson Method

$$
x_{n+1} = x_n - \\frac{f(x_n)}{f'(x_n)}
$$

Converges quadratically when $f'(x^*) \\neq 0$.

### Simpson's Rule

$$
\\int_a^b f(x)\\,dx \\approx \\frac{h}{3}[f(a) + 4f(\\frac{a+b}{2}) + f(b)]
$$

Error: $O(h^5)$

### Runge-Kutta 4th Order (RK4)

For $y' = f(t,y)$:
$$
k_1 = hf(t_n, y_n)
$$
$$
k_2 = hf(t_n + h/2, y_n + k_1/2)
$$
$$
k_3 = hf(t_n + h/2, y_n + k_2/2)
$$
$$
k_4 = hf(t_n + h, y_n + k_3)
$$
$$
y_{n+1} = y_n + \\frac{1}{6}(k_1 + 2k_2 + 2k_3 + k_4)
$$

### Taylor Series Error

$$
|f(x) - P_n(x)| \\leq \\frac{M|x-a|^{n+1}}{(n+1)!}
$$
"""
    },
    {
        "name": "mathematical-logic-expert",
        "title": "Mathematical Logic Expert",
        "description": "Expert in formal logic, model theory, computability, and foundations of mathematics",
        "topics": [
            "Propositional and predicate logic",
            "Formal systems and proof theory",
            "Model theory and semantics",
            "Gödel's incompleteness theorems",
            "Computability and decidability",
            "Set theory (ZFC axioms)",
            "Axiom of Choice implications",
            "Foundations of mathematics"
        ],
        "formulas": """## Logical Foundations

### Logical Connectives

- Conjunction: $P \\land Q$
- Disjunction: $P \\lor Q$  
- Implication: $P \\Rightarrow Q \\equiv \\neg P \\lor Q$
- Biconditional: $P \\Leftrightarrow Q \\equiv (P \\Rightarrow Q) \\land (Q \\Rightarrow P)$

### Quantifiers

- Universal: $\\forall x \\in X: P(x)$
- Existential: $\\exists x \\in X: P(x)$

### De Morgan's Laws

$$
\\neg(P \\land Q) \\equiv \\neg P \\lor \\neg Q
$$
$$
\\neg(P \\lor Q) \\equiv \\neg P \\land \\neg Q
$$

For quantifiers:
$$
\\neg(\\forall x: P(x)) \\equiv \\exists x: \\neg P(x)
$$

### Gödel's First Incompleteness Theorem

In any consistent formal system $F$ containing arithmetic:
$$
\\exists \\text{ sentence } G: F \\nvdash G \\text{ and } F \\nvdash \\neg G
$$

"True but unprovable statements exist"
"""
    },
    {
        "name": "optimization-theory-expert",
        "title": "Optimization Theory Expert",
        "description": "Expert in optimization methods covering linear programming, convex optimization, gradient methods, and constrained optimization",
        "topics": [
            "Linear programming and simplex method",
            "Convex optimization",
            "Gradient descent and variants",
            "Lagrange multipliers",
            "KKT conditions",
            "Integer programming",
            "Dynamic programming",
            "Metaheuristic optimization"
        ],
        "formulas": """## Optimization Methods

### Gradient Descent

$$
x_{k+1} = x_k - \\alpha \\nabla f(x_k)
$$

Where $\\alpha$ is learning rate.

### Lagrange Multipliers

To optimize $f(x,y,z)$ subject to $g(x,y,z) = 0$:
$$
\\nabla f = \\lambda \\nabla g
$$

### KKT Conditions

For $\\min f(x)$ subject to $g_i(x) \\leq 0$, $h_j(x) = 0$:

1. $\\nabla f(x^*) + \\sum \\mu_i \\nabla g_i(x^*) + \\sum \\lambda_j \\nabla h_j(x^*) = 0$
2. $g_i(x^*) \\leq 0$
3. $\\mu_i \\geq 0$
4. $\\mu_i g_i(x^*) = 0$ (complementary slackness)

### Linear Programming Standard Form

$$
\\begin{align}
\\min \\quad & c^T x \\\\
\\text{s.t.} \\quad & Ax = b \\\\
& x \\geq 0
\\end{align}
$$
"""
    },
    {
        "name": "applied-mathematics-engineering",
        "title": "Applied Mathematics for Engineering",
        "description": "Applied math expert for engineering applications including Fourier analysis, transforms, and practical problem solving",
        "topics": [
            "Fourier series and transforms",
            "Laplace transforms for ODEs",
            "Vector calculus applications",
            "Tensor analysis basics",
            "Variational calculus",
            "Green's functions",
            "Boundary value problems",
            "Engineering mathematics applications"
        ],
        "formulas": """## Applied Mathematics

### Fourier Series

$$
f(x) = \\frac{a_0}{2} + \\sum_{n=1}^{\\infty}\\left(a_n\\cos\\left(\\frac{n\\pi x}{L}\\right) + b_n\\sin\\left(\\frac{n\\pi x}{L}\\right)\\right)
$$

Coefficients:
$$
a_n = \\frac{1}{L}\\int_{-L}^{L} f(x)\\cos\\left(\\frac{n\\pi x}{L}\\right)dx
$$

### Fourier Transform

$$
\\hat{f}(\\omega) = \\int_{-\\infty}^{\\infty} f(t)e^{-i\\omega t}\\,dt
$$

### Laplace Transform

$$
\\mathcal{L}\\{f(t)\\}(s) = \\int_0^{\\infty} e^{-st}f(t)\\,dt
$$

**Properties:**
- $\\mathcal{L}\\{f'(t)\\} = s\\mathcal{L}\\{f\\} - f(0)$
- $\\mathcal{L}\\{e^{at}f(t)\\} = F(s-a)$

### Divergence Theorem

$$
\\int_V (\\nabla \\cdot \\mathbf{F})\\,dV = \\oint_S \\mathbf{F} \\cdot d\\mathbf{S}
$$
"""
    },
    {
        "name": "probability-theory-expert",
        "title": "Probability Theory Expert",
        "description": "Rigorous probability theorist covering measure-theoretic probability, stochastic processes, and advanced probability",
        "topics": [
            "Probability spaces and σ-algebras",
            "Random variables and distributions",
            "Expectation and conditional probability",
            "Law of Large Numbers",
            "Central Limit Theorem proofs",
            "Martingales",
            "Stochastic processes",
            "Markov chains"
        ],
        "formulas": """## Probability Theory

### Probability Space

Triple $(\\Omega, \\mathcal{F}, P)$ where:
- $\\Omega$ is sample space
- $\\mathcal{F}$ is σ-algebra of events  
- $P: \\mathcal{F} \\to [0,1]$ is probability measure

### Conditional Probability

$$
P(A|B) = \\frac{P(A \\cap B)}{P(B)}
$$

### Law of Total Probability

$$
P(A) = \\sum_{i} P(A|B_i)P(B_i)
$$

### Markov Inequality

$$
P(X \\geq a) \\leq \\frac{E[X]}{a}
$$

### Chebyshev's Inequality

$$
P(|X - \\mu| \\geq k\\sigma) \\leq \\frac{1}{k^2}
$$

### Moment Generating Function

$$
M_X(t) = E[e^{tX}] = \\int_{-\\infty}^{\\infty} e^{tx}f(x)\\,dx
$$
"""
    },
    {
        "name": "game-theory-strategist",
        "title": "Game Theory Strategist",
        "description": "Game theory expert covering Nash equilibrium, strategic thinking, auction theory, and cooperative games",
        "topics": [
            "Normal form and extensive form games",
            "Nash equilibrium",
            "Dominant strategies",
            "Mixed strategies",
            "Sequential games and backward induction",
            "Repeated games",
            "Cooperative game theory",
            "Auction theory and mechanism design"
        ],
        "formulas": """## Game Theory

### Nash Equilibrium

Strategy profile $(s_1^*, ..., s_n^*)$ is Nash equilibrium if:
$$
u_i(s_i^*, s_{-i}^*) \\geq u_i(s_i, s_{-i}^*) \\quad \\forall i, \\forall s_i
$$

No player can improve by deviating unilaterally.

### Mixed Strategy

Player randomizes over pure strategies:
$$
\\sigma_i = (p_1, ..., p_m) \\text{ where } \\sum_{j=1}^{m} p_j = 1
$$

Expected payoff:
$$
u_i(\\sigma) = \\sum_{s \\in S} \\sigma(s)u_i(s)
$$

### Shapley Value (Cooperative Games)

$$
\\phi_i(v) = \\sum_{S \\subseteq N \\setminus \\{i\\}} \\frac{|S|!(|N|-|S|-1)!}{|N|!}[v(S \\cup \\{i\\}) - v(S)]
$$

### Prisoner's Dilemma Payoff Matrix

$$
\\begin{array}{c|c|c}
& C & D \\\\
\\hline
C & (3,3) & (0,5) \\\\
\\hline
D & (5,0) & (1,1)
\\end{array}
$$
"""
    },
    {
        "name": "matrix-theory-specialist",
        "title": "Matrix Theory Specialist",
        "description": "Advanced matrix theory expert covering spectral theory, matrix factorizations, and numerical linear algebra",
        "topics": [
            "Matrix norms and eigenvalue bounds",
            "Spectral theory",
            "Matrix factorizations (QR, Cholesky, Schur)",
            "Positive definite matrices",
            "Matrix calculus",
            "Kronecker products",
            "Numerical stability",
            "Applications to data science"
        ],
        "formulas": """## Advanced Matrix Theory

### Spectral Theorem

For symmetric real matrix $A$:
$$
A = Q\\Lambda Q^T
$$
Where $Q$ is orthogonal, $\\Lambda$ is diagonal of eigenvalues.

### Matrix Norms

Frobenius norm: $\\|A\\|_F = \\sqrt{\\sum_{i,j} a_{ij}^2} = \\sqrt{\\text{tr}(A^TA)}$

Spectral norm: $\\|A\\|_2 = \\sigma_{\\max}(A)$ (largest singular value)

### Rayleigh Quotient

$$
R(A,x) = \\frac{x^T A x}{x^T x}
$$

Extremal property: $\\lambda_{\\min} \\leq R(A,x) \\leq \\lambda_{\\max}$

### Cholesky Decomposition

For positive definite $A$:
$$
A = LL^T
$$
Where $L$ is lower triangular.

### Condition Number

$$
\\kappa(A) = \\|A\\| \\cdot \\|A^{-1}\\| = \\frac{\\sigma_{\\max}}{\\sigma_{\\min}}
$$

Large $\\kappa$ indicates ill-conditioning.
"""
    },
    {
        "name": "fourier-analysis-expert",
        "title": "Fourier Analysis Expert",
        "description": "Fourier analysis specialist covering series, transforms, signal processing, and harmonic analysis",
        "topics": [
            "Fourier series convergence",
            "Fourier transforms (continuous and discrete)",
            "Fast Fourier Transform (FFT)",
            "Convolution theorem",
            "Parseval's identity",
            "Signal processing applications",
            "Harmonic analysis",
            "Wavelets and time-frequency analysis"
        ],
        "formulas": """## Fourier Analysis

### Fourier Transform Pair

$$
\\hat{f}(\\omega) = \\mathcal{F}\\{f(t)\\} = \\int_{-\\infty}^{\\infty} f(t)e^{-i\\omega t}\\,dt
$$

$$
f(t) = \\mathcal{F}^{-1}\\{\\hat{f}(\\omega)\\} = \\frac{1}{2\\pi}\\int_{-\\infty}^{\\infty} \\hat{f}(\\omega)e^{i\\omega t}\\,d\\omega
$$

### Convolution Theorem

$$
\\mathcal{F}\\{f * g\\} = \\mathcal{F}\\{f\\} \\cdot \\mathcal{F}\\{g\\}
$$

Where $(f*g)(t) = \\int_{-\\infty}^{\\infty} f(\\tau)g(t-\\tau)\\,d\\tau$

### Parseval's Identity

$$
\\int_{-\\infty}^{\\infty} |f(t)|^2\\,dt = \\frac{1}{2\\pi}\\int_{-\\infty}^{\\infty} |\\hat{f}(\\omega)|^2\\,d\\omega
$$

### Discrete Fourier Transform

$$
X_k = \\sum_{n=0}^{N-1} x_n e^{-2\\pi i kn/N}
$$

FFT computes this in $O(N\\log N)$ instead of $O(N^2)$.
"""
    },
]


def main():
    """Create Mathematics skills."""
    base_path = Path("skills")
    claude_path = Path(r"C:\Users\sandr\.config\claude\skills")
    
    category = "mathematics"
    skills = MATH_SKILLS
    
    total = len(skills)
    count = 0
    
    print(f"\n🚀 Creating {total} Mathematics skills...\n")
    print(f"📁 Category: {category}")
    
    # Create category dirs
    (base_path / category).mkdir(parents=True, exist_ok=True)
    (claude_path / category).mkdir(parents=True, exist_ok=True)
    
    for skill in skills:
        count += 1
        skill_name = skill["name"]
        
        # Create skill dirs
        skill_dir = base_path / category / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        claude_skill_dir = claude_path / category / skill_name
        claude_skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate SKILL.md
        skill_content = generate_skill_md(
            skill_name,
            skill["title"],
            skill["description"],
            skill["topics"],
            skill["formulas"]
        )
        
        # Write to both locations
        (skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")
        (claude_skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")
        
        # Create README
        readme = f"""# {skill["title"]}

{skill["description"]}

## Topics Covered
{chr(10).join(f"- {topic}" for topic in skill["topics"])}

## Mathematical Content

This skill includes rigorous mathematical formulas using LaTeX notation. Claude Desktop will render all equations properly.

## Usage

Ask mathematical questions and this skill will provide:
- Formal definitions with LaTeX
- Worked examples
- Step-by-step proofs
- Intuitive explanations
- Practice problems

**Category:** mathematics  
**Difficulty:** Advanced  
**Version:** 1.0.0
"""
        (skill_dir / "README.md").write_text(readme, encoding="utf-8")
        (claude_skill_dir / "README.md").write_text(readme, encoding="utf-8")
        
        print(f"  ✅ {count}/{total}: {skill_name}")
    
    print(f"\n🎉 Mathematics category complete: {total} skills created!")
    print(f"📁 Local: {base_path.absolute()}/{category}")
    print(f"📁 Claude: {claude_path}/{category}")
    print("\n✨ All Mathematics skills deployed with LaTeX formulas!")
    print(f"\n📊 Grand Total: {60 + total} skills across 6 categories!")


if __name__ == "__main__":
    main()

