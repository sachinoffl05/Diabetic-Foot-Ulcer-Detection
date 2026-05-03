# DFU Detection Model Architecture

## Overview
The DFU (Diabetic Foot Ulcer) Detection system uses a custom Convolutional Neural Network (CNN) implemented in PyTorch, named `SimpleCNN`. This model is designed to classify thermal foot images into 5 distinct stages of diabetic foot ulcers:

1. **Stage 0 - Healthy**: No ulcer detected
2. **Stage 1 - Superficial**: Surface-level skin damage
3. **Stage 2 - Deep**: Tissue involvement
4. **Stage 3 - Infected**: Signs of infection/osteomyelitis
5. **Stage 4 - Gangrene**: Serious tissue damage/gangrene

The model processes RGB images of size 224×224 pixels and outputs class probabilities for each stage.

## Model Architecture

### Input
- **Shape**: `(batch_size, 3, 224, 224)`
- **Type**: RGB image (3 channels)
- **Preprocessing**:
  - Resize to 224×224 pixels
  - Convert to PyTorch tensor
  - Normalize using ImageNet statistics:
    - Mean: `[0.485, 0.456, 0.406]`
    - Std: `[0.229, 0.224, 0.225]`

### Feature Extraction Layers (`self.features`)

The feature extraction backbone consists of two convolutional blocks:

#### Block 1
1. **Conv2D Layer**
   - Input channels: 3
   - Output channels: 16
   - Kernel size: 3×3
   - Padding: 1 (same padding)
   - Output shape: `(batch_size, 16, 224, 224)`

2. **ReLU Activation**
   - In-place: No
   - Output shape: `(batch_size, 16, 224, 224)`

3. **MaxPool2D**
   - Kernel size: 2×2
   - Stride: 2
   - Output shape: `(batch_size, 16, 112, 112)`

#### Block 2
4. **Conv2D Layer**
   - Input channels: 16
   - Output channels: 32
   - Kernel size: 3×3
   - Padding: 1 (same padding)
   - Output shape: `(batch_size, 32, 112, 112)`

5. **ReLU Activation**
   - In-place: No
   - Output shape: `(batch_size, 32, 112, 112)`

6. **MaxPool2D**
   - Kernel size: 2×2
   - Stride: 2
   - Output shape: `(batch_size, 32, 56, 56)`

### Classification Layers (`self.classifier`)

#### Fully Connected Head
7. **Flatten**
   - Input shape: `(batch_size, 32, 56, 56)`
   - Output shape: `(batch_size, 100352)` (32 × 56 × 56 = 100,352)

8. **Linear Layer**
   - Input features: 100,352
   - Output features: 128
   - Output shape: `(batch_size, 128)`

9. **ReLU Activation**
   - In-place: No
   - Output shape: `(batch_size, 128)`

10. **Linear Layer** (Output)
    - Input features: 128
    - Output features: 5
    - Output shape: `(batch_size, 5)`

### Output
- **Shape**: `(batch_size, 5)`
- **Activation**: None (raw logits)
- **Post-processing**: Softmax for probabilities, argmax for predicted class

## Model Parameters

### Trainable Parameters
- **Conv2D (3→16)**: 3×16×3×3 + 16 = 448 parameters
- **Conv2D (16→32)**: 16×32×3×3 + 32 = 4,640 parameters
- **Linear (100352→128)**: 100352×128 + 128 = 12,845,184 parameters
- **Linear (128→5)**: 128×5 + 5 = 645 parameters

**Total trainable parameters**: ~12,850,917

### Non-trainable Parameters
- None (all layers are trainable)

## Explainability Features

### Grad-CAM Integration
The model supports Gradient-weighted Class Activation Mapping (Grad-CAM) for interpretability:
- **Target Layer**: Second Conv2D layer (`model.features[3]`)
- **Output**: Heatmap overlay showing regions of the input image that contributed most to the prediction
- **Resolution**: 224×224 pixels (upsampled from 56×56 feature maps)

## Training Details
- **Framework**: PyTorch
- **Loss Function**: Cross-Entropy Loss (implicit from classification task)
- **Optimizer**: Not specified in code (likely Adam or SGD during training)
- **Batch Size**: Not specified
- **Epochs**: Not specified
- **Data Augmentation**: Not implemented in inference code

## Deployment
- **Model File**: `model.pth` (PyTorch state_dict)
- **Inference Device**: CPU (map_location="cpu")
- **Memory Requirements**: ~50MB for model weights
- **Inference Time**: ~100-500ms per image (depends on hardware)

## Limitations
- **Architecture Simplicity**: Basic CNN without advanced features like batch normalization, dropout, or residual connections
- **Input Constraints**: Fixed 224×224 input size, RGB images only
- **Class Imbalance**: No explicit handling in architecture
- **Domain Specificity**: Trained specifically for thermal foot images

## Future Improvements
- Add batch normalization for training stability
- Implement dropout for regularization
- Use deeper architectures (ResNet, EfficientNet)
- Add attention mechanisms
- Support variable input sizes
- Implement data augmentation during training