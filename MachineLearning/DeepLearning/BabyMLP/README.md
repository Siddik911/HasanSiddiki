# BabyMLP: Neural Network from Scratch

A complete implementation of a multi-layer perceptron (MLP) neural network built from scratch using only NumPy. This project demonstrates building, training, and optimizing a neural network for 2x2 parity classification.

## Project Overview

This notebook implements a complete neural network pipeline including:
- Forward and backward propagation
- Multiple activation functions (ReLU, Softmax)
- Loss computation (KL Divergence)
- Multiple optimizers (Gradient Descent, Momentum, Adam)
- Training loop with early stopping
- Comprehensive evaluation metrics

## Problem Statement

The network classifies 2x2 black-and-white images by the parity (even/odd) of the number of black pixels. This is an XOR-like problem requiring non-linear decision boundaries.

## Architecture

**Baseline Model**: 4 → 4 → 4 → 2 (56 parameters)
- Achieved ~70-80% validation accuracy

**Improved Model**: 4 → 16 → 16 → 2 (338 parameters)
- Achieved >90% validation accuracy

## Files

- **BabyMLP.ipynb** - Complete implementation with theory and code
- **BabyMLP.html** - HTML export for easy viewing

## Key Features

- Pure NumPy implementation (no deep learning frameworks)
- Rigorous mathematical notation with overdot gradients
- Column-based mini-batch processing
- He initialization for ReLU networks
- Comprehensive evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix)
- Learning curves and visualization

## Notebook Structure

1. **Introduction & Problem Statement**
2. **Mathematical Theory & Foundations**
3. **Implementation**
4. **Training the Network**
5. **Performance Analysis & Improvements**

## Requirements

- NumPy
- Matplotlib

## Results

The improved architecture (4→16→16→2) with optimized hyperparameters achieves:
- Training Accuracy: >95%
- Validation Accuracy: >90%
- Successfully learns XOR-like parity patterns

## License

MIT

## Author

Implementation demonstrates building neural networks from first principles for educational purposes.
