# A Theory of How Pretraining Shapes Inductive Bias in Fine-Tuning
# arXiv:2602.20062

## Abstract

Pretraining and fine-tuning are central stages in modern machine learning systems. In practice, feature learning plays an important role across both stages: deep neural networks learn a broad range of useful features during pretraining and further refine those features during fine-tuning. However, an end-to-end theoretical understanding of how choices of initialization impact the ability to reuse and refine features during fine-tuning has remained elusive. Here we develop an analytical theory of the pretraining-fine-tuning pipeline in diagonal linear networks, deriving exact expressions for the generalization error as a function of initialization parameters and task statistics. We find that different initialization choices place the network into four distinct fine-tuning regimes that are distinguished by their ability to support feature learning and reuse, and therefore by the task statistics for which they are beneficial. In particular, a smaller initialization scale in earlier layers enables the network to both reuse and refine its features, leading to superior generalization on fine-tuning tasks that rely on a subset of pretraining features. We demonstrate empirically that the same initialization parameters impact generalization in nonlinear networks trained on CIFAR-100. Overall, our results demonstrate analytically how data and network initialization interact to shape fine-tuning generalization, highlighting an important role for the relative scale of initialization across different layers in enabling continued feature learning during fine-tuning.

## Authors

- Francesco Locatello
- Andrew M. Saxe
- Marco Mondelli
- Flavia Mancini
- Samuel Lippl
- Clémentine Dominé

## Key Contributions

### 1. Analytical Theory of PT+FT in Diagonal Linear Networks

The authors derive exact expressions for generalization error as a function of:
- Weight initialization parameters (c_PT, λ_PT, γ_FT)
- Task parameters (ρ_PT, ρ_FT^shared, ρ_FT^new)
- Data scale (α_FT)

### 2. Four Distinct Fine-Tuning Regimes

The authors identify four regimes based on initialization choices:

**Regime I: Rich, Pretraining-Independent**
- ℓ-order = 1, PD = 0
- Governed by ℓ₁-norm
- Induced when λ_PT → -1, γ_FT → 0
- New dimensions learned, sparse inductive bias

**Regime II: Lazy, Pretraining-Dependent**
- ℓ-order = 2, PD = -1
- Governed by weighted ℓ₂-norm: ∑|β_FT,i|²/|β_PT,i|
- Induced when c_PT → 0, λ_PT → 1
- Reuse with minimal adaptation

**Regime III: Lazy, Pretraining-Independent**
- ℓ-order = 2, PD = 0
- Governed by unweighted ℓ₂-norm
- Induced when c_PT → ∞ or γ_FT → ∞
- Fine-tuning behavior does not depend on pretraining

**Regime IV: Pretraining-Dependent Rich**
- ℓ-order ∈ (1,2), PD ∈ (-1,0)
- Intermediate regime between I and II
- Benefits from both feature reuse and sparsity
- Controlled by relative scale of initialization across layers

### 3. Universal Trade-off

The authors identify a fundamental trade-off:
- ℓ-order ∈ [1,2]
- PD ∈ [-1,0]
- ℓ-order + PD ∈ [1,2]

This means it's impossible to achieve both perfect sparsity bias (ℓ-order=1) and perfect pretraining dependence (PD=-1) simultaneously.

### 4. Key Findings

1. **Relative Scale Matters**: The relative initialization scale between layers (λ_PT) plays a crucial role in determining the fine-tuning regime

2. **Layer-Wise Scaling**: Smaller initialization in earlier layers (negative λ_PT) enables the network to both reuse and refine features

3. **Optimal Regime Depends on Task**: The best fine-tuning regime depends on task statistics - specifically:
   - How much pretraining and fine-tuning tasks share features (ρ_FT^shared vs ρ_FT^new)
   - Sparsity levels of the tasks

4. **Experimental Validation**: The theory extends to ResNet-18 on CIFAR-100, showing similar patterns

## Theoretical Framework

### Network Architecture

The paper studies diagonal linear networks:
- f_w,v(x) = β(w,v)^T x
- β(w,v) := v^+ ∘ w^+ - v^- ∘ w^- ∈ ℝ^D

This architecture captures:
1. Transition between rich and lazy regimes based on initialization
2. Different generalization behavior in these regimes

### Training Paradigm

Two-stage training:
1. **Pretraining (PT)**: Train on task with data X_PT, y_PT
2. **Fine-tuning (FT)**: Re-balance pathways and re-initialize readout to scale γ_FT, then train on task X_FT, y_FT

### Initialization Parameters

1. **Absolute Scale (c_PT)**: Overall initial weight magnitude
   c_PT := w_PT±(0)² + v_PT±(0)²

2. **Relative Scale (λ_PT)**: Difference between first and second layer weights
   λ_PT := (w_PT±(0)² - v_PT±(0)²)/c_PT ∈ [-1,1]

3. **Readout Scale (γ_FT)**: Scale of readout re-initialization after pretraining

### Data Generative Model

Teacher-student setup with spike-and-slab distribution:
- Pretraining task: β_PT = (σ/√ρ_PT) ∘ θ_PT, θ_PT ~ Bernoulli(ρ_PT)
- Fine-tuning task: Conditional sampling based on whether dimensions were active in pretraining

Key parameters:
- ρ_PT: Sparsity of pretraining task
- ρ_FT^shared: Probability FT uses same dimensions as PT
- ρ_FT^new: Probability FT uses new dimensions

## Main Theoretical Results

### Theorem 4.1: Implicit Bias

The gradient flow solution is given by:
arg min_βFT Q_k(β_FT) s.t. X_FT^T β_FT = y_FT

Where:
- Q_k(β_FT) = Σ_d q_{k_d}(β_FT,d)
- q_k(z) = (√k/4)(1 - √(1+4z²/k) + (2z/√k)arcsinh(2z/√k))
- k_d = (2c_PT(1+λ_PT)(1+√(1+(β_PT,d/c_PT)²)) + γ²)²

This shows the implicit bias depends on:
- λ_PT, c_PT, γ_FT (initialization parameters)
- β_PT (learned pretraining representation)

### Proposition 4.2: Generalization Error

In the high-dimensional limit, the estimation problem decouples into scalar problems. The generalization error can be computed through fixed-point equations involving:
- Effective regularization parameter θ
- Effective noise parameter θ₀

## Experimental Validation

### Theoretical Predictions

The authors validate their theory through:
1. Analytical calculations using replica theory
2. Empirical simulations of diagonal linear networks
3. Large-scale vision experiments with ResNet-18 on CIFAR-100

### CIFAR-100 Results

Key findings:
1. **Relative Scaling (λ_PT)**: κ < 1 (negative relative scaling) improves fine-tuning generalization
2. **Absolute Scale (c_PT)**: Increasing c_PT degrades fine-tuning performance
3. **Readout Scale (γ_FT)**: Decreasing γ_FT improves performance for intermediate sample sizes

## Significance

### Novel Insights

1. **End-to-End Theory**: First comprehensive theory connecting initialization to fine-tuning generalization

2. **Relative Scale Importance**: Highlights that the relative initialization scale across layers is crucial, not just absolute scale

3. **Task-Dependent Optimal Regimes**: Shows that the optimal fine-tuning regime depends on task statistics

4. **Practical Implications**: Provides actionable guidance for weight initialization in pretraining-fine-tuning pipelines

### Limitations

1. **Simplified Model**: Analysis is on diagonal linear networks; extension to nonlinear networks is an open question

2. **Specific Assumptions**: Spike-and-slab distribution and specific network architecture

3. **Replica Method**: Non-rigorous but powerful approach

## Applications and Future Work

### Potential Applications

1. **Improved Transfer Learning**: Principled initialization strategies for better feature transfer

2. **Biological Learning**: Insights into how biological systems might balance feature reuse and learning

3. **Model Compression**: Understanding sparsity biases for efficient models

### Future Directions

1. **Extension to Nonlinear Networks**: Apply theory to deep nonlinear networks

2. **Empirical Measurements**: Using influence functions to measure ℓ-order and PD in complex architectures

3. **Alternative Pretraining Schemes**: How different pretraining objectives affect the inductive bias

## References

The paper draws from and extends work on:
- Rich vs lazy learning regimes (Chizat et al., 2019; Saxe et al., 2013)
- Implicit regularization in neural networks (Soudry et al., 2018)
- Diagonal linear networks (Woodworth et al., 2020; Azulay et al., 2021)
- Pretraining and fine-tuning (Lampinen & Ganguli, 2018; Shachaf et al., 2021)
- Replica theory (Edwards & Anderson, 1975; Mézard et al., 1987)
