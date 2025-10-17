# Data Analysis Fundamentals

Data analysis transforms raw data into insights through systematic examination.

## Types of Data Analysis

### Descriptive Analysis
Summarize and describe data.

**Techniques**:
- Measures of central tendency (mean, median, mode)
- Measures of dispersion (range, variance, standard deviation)
- Frequency distributions
- Cross-tabulations

**Example**:
```python
import pandas as pd

df = pd.read_csv('data.csv')

# Descriptive statistics
print(df.describe())

# Central tendency
mean_age = df['age'].mean()
median_income = df['income'].median()

# Frequency
print(df['category'].value_counts())
```

### Inferential Analysis
Draw conclusions about populations from samples.

**Techniques**:
- Hypothesis testing
- Confidence intervals
- Statistical significance
- Regression analysis

**Example**: "Does new teaching method improve test scores?"

### Exploratory Analysis
Discover patterns without predetermined hypotheses.

**Techniques**:
- Data visualization
- Correlation matrices
- Clustering
- Dimensionality reduction

**Goal**: Generate hypotheses for further testing.

### Predictive Analysis
Forecast future outcomes.

**Techniques**:
- Regression models
- Machine learning
- Time series analysis

## Data Analysis Process

### 1. Data Collection
Gather relevant data systematically.

### 2. Data Cleaning
Remove errors, handle missing values, standardize formats.

```python
# Check for missing data
print(df.isnull().sum())

# Drop rows with missing critical data
df = df.dropna(subset=['user_id', 'timestamp'])

# Fill missing values
df['category'].fillna('Unknown', inplace=True)

# Remove duplicates
df = df.drop_duplicates()

# Fix data types
df['date'] = pd.to_datetime(df['date'])
df['price'] = pd.to_numeric(df['price'], errors='coerce')
```

### 3. Exploratory Data Analysis

```python
# Univariate analysis
df['age'].hist(bins=20)
df['category'].value_counts().plot(kind='bar')

# Bivariate analysis
df.plot.scatter(x='age', y='income')

# Correlation matrix
print(df.corr())

# Group statistics
print(df.groupby('category')['price'].mean())
```

### 4. Statistical Testing

```python
from scipy import stats

# T-test: Compare two groups
group1 = df[df['group'] == 'A']['score']
group2 = df[df['group'] == 'B']['score']
t_stat, p_value = stats.ttest_ind(group1, group2)

if p_value < 0.05:
    print("Significant difference between groups")

# Chi-square: Test independence
contingency_table = pd.crosstab(df['category'], df['outcome'])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

# Correlation
correlation, p_value = stats.pearsonr(df['x'], df['y'])
```

### 5. Interpretation
What do results mean? What are limitations?

### 6. Communication
Present findings clearly with visualizations.

## Statistical Concepts

### Hypothesis Testing

#### Null Hypothesis (H₀)
"No effect" or "no difference"

#### Alternative Hypothesis (H₁)
"There is an effect" or "there is a difference"

#### P-Value
Probability of observing results if null hypothesis is true.

**Interpretation**:
- p < 0.05: Reject null (traditional threshold)
- p < 0.01: Strong evidence
- p < 0.001: Very strong evidence

**Caution**: p-value is NOT probability that hypothesis is true!

### Effect Size
Magnitude of difference or relationship.

**Cohen's d** (for t-tests):
- 0.2: Small effect
- 0.5: Medium effect
- 0.8: Large effect

**R²** (for regression):
- Proportion of variance explained
- 0.0-1.0 scale

### Confidence Intervals
Range likely to contain true population parameter.

```python
from scipy import stats

# 95% confidence interval for mean
mean = df['age'].mean()
std_error = stats.sem(df['age'])
ci = stats.t.interval(0.95, len(df)-1, mean, std_error)

print(f"95% CI: {ci[0]:.2f} to {ci[1]:.2f}")
```

## Data Visualization

### Choosing Charts

**Distributions**: Histogram, box plot, violin plot
**Comparisons**: Bar chart, grouped bar chart
**Relationships**: Scatter plot, line plot
**Proportions**: Pie chart, stacked bar
**Trends**: Line chart, area chart

### Visualization Best Practices

```python
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ Good visualization
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x='category', y='value')
plt.title('Average Value by Category', fontsize=16)
plt.xlabel('Category', fontsize=12)
plt.ylabel('Average Value', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('chart.png', dpi=300)
```

**Principles**:
- Clear titles and labels
- Appropriate scale
- Readable fonts
- Meaningful colors
- Remove chartjunk

## Common Pitfalls

### Correlation ≠ Causation
```
Ice cream sales correlate with drowning deaths.
❌ Conclusion: Ice cream causes drowning
✅ Conclusion: Both increase in summer (confounding variable)
```

### P-Hacking
Manipulating data or analysis to get p < 0.05.

**Examples**:
- Running many tests, reporting only significant ones
- Stopping data collection when p < 0.05
- Excluding "outliers" to get significance

**Solution**: Pre-register analysis plan, report all tests.

### Small Sample Size
```
n = 5 participants
p = 0.04

❌ Conclusion: Significant effect!
⚠️  Reality: Underpowered study, results unreliable
```

**Solution**: Power analysis before study, adequate sample size.

### Confounding Variables
```
Study: Students who drink coffee get higher grades.
❌ Conclusion: Coffee improves grades
⚠️  Confound: Motivated students drink more coffee AND study more
```

**Solution**: Control for confounds, use experimental design.

## Tools

### Python Libraries
```python
# Data manipulation
import pandas as pd
import numpy as np

# Statistics
from scipy import stats
import statsmodels.api as sm

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Machine learning
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
```

### R (Alternative)
Specialized for statistics.

```R
# Load data
data <- read.csv("data.csv")

# Summary stats
summary(data)

# T-test
t.test(group1, group2)

# Linear regression
model <- lm(y ~ x1 + x2, data=data)
summary(model)
```

## Reporting Results

### Tables
- Clear headers
- Appropriate precision (2-3 decimal places)
- Include sample sizes
- Note statistical significance

### Figures
- High resolution
- Clear legends
- Referenced in text
- Stand-alone (understandable without text)

### Text
```
✅ Good reporting:
"Group A (M = 85.3, SD = 12.4) scored significantly higher than Group B
(M = 78.1, SD = 14.2), t(98) = 2.45, p = 0.016, d = 0.53."

Includes:
- Descriptive statistics (M, SD)
- Test statistic (t)
- Degrees of freedom (98)
- P-value (0.016)
- Effect size (d = 0.53)
```

## Related Concepts
- [[Statistical Methods]]
- [[Research Methods]]
- [[Data Visualization]]
- [[Python for Data Analysis]]
- [[Research Ethics]]

*Data analysis is not just about running tests - it's about understanding what the data tells us.*
