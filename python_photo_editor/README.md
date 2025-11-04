# 🐍 Advanced Photo Editor - Python Edition

A comprehensive photo editor built with Python, OpenCV, NumPy, and Matplotlib featuring advanced image processing capabilities including denoising, smoothing, sharpening, edge detection, thresholding, color manipulation, geometric transformations, and artistic filters.

## 🎯 Features

### 🔬 **Core Image Processing (Your Requirements)**
- **Denoising & Smoothing**: Gaussian, Median, and Bilateral filters
- **Sharpening**: Basic sharpening and Unsharp Mask
- **Edge Detection**: Laplacian, Canny, and Sobel edge detection
- **Thresholding**: Global, Adaptive, and Otsu thresholding

### 🎨 **Color Manipulation**
- **Brightness/Contrast adjustment** with real-time sliders
- **Hue/Saturation/Lightness controls** for complete color control
- **RGB Balance** adjustment for individual color channels
- **Color Temperature** adjustment for warm/cool tones
- **Vibrance Enhancement** for selective saturation boost
- **Grayscale Conversion** with various methods
- **Sepia/Color Tint Filters** for vintage effects
- **Color Channel Mixing** for advanced color manipulation

### 🔄 **Geometric Transformations**
- **Rotation** with custom angles and quick 90° buttons
- **Scaling/Resizing** with aspect ratio options
- **Cropping** with precise coordinate controls
- **Flipping** (horizontal/vertical)
- **Perspective Correction** for distorted images
- **Lens Distortion Correction** for camera artifacts
- **Skew/Shear Transformations** for advanced geometric adjustments

### 🎭 **Filters and Effects**
- **Blur Effects**: Gaussian, Motion, and Radial blur
- **Vignette Effects** with customizable intensity
- **Film Grain Simulation** for vintage texture
- **Pixelation/Mosaic Effects** for artistic pixel effects
- **Oil Painting Filter** for artistic rendering
- **Watercolor Effect** for soft, artistic look
- **Posterization** for reduced color levels
- **Solarization** for inverted color effects

## 🛠️ Technology Stack

- **Python 3.8+** - Core programming language
- **OpenCV** - Advanced image processing and computer vision
- **NumPy** - Numerical computing and array operations
- **Matplotlib** - High-quality image visualization and plotting
- **PIL/Pillow** - Additional image processing capabilities
- **SciPy** - Scientific computing and advanced algorithms
- **scikit-image** - Additional image processing algorithms
- **Tkinter** - Modern GUI framework

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Setup
```bash
# Clone or download the project
cd python_photo_editor

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Manual Installation
```bash
pip install opencv-python numpy matplotlib Pillow scipy scikit-image
```

## 🚀 Usage

### Running the Application
```bash
python main.py
```

### Running the Demo
```bash
python demo.py
```

### Using the GUI

1. **Open Image**: Click "Open Image" to load your photo
2. **Choose Processing**: Select from the tabbed interface:
   - **Denoising**: Remove noise with various filters
   - **Sharpening**: Enhance image details
   - **Edge Detection**: Find and highlight edges
   - **Thresholding**: Convert to binary images
   - **Color**: Adjust colors and apply effects
   - **Transform**: Rotate, scale, crop, flip
   - **Filters**: Apply artistic effects
3. **Adjust Parameters**: Use sliders to fine-tune effects
4. **Apply Changes**: Click "Apply" buttons to process
5. **Save Result**: Click "Save Image" to export

## 📁 Project Structure

```
python_photo_editor/
├── main.py                 # Main application entry point
├── image_processor.py      # Core image processing algorithms
├── gui_components.py       # GUI interface components
├── demo.py                 # Demonstration script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔬 Technical Implementation

### Image Processing Pipeline
1. **Input**: Load image using OpenCV
2. **Processing**: Apply selected algorithms using NumPy/OpenCV
3. **Display**: Show results using Matplotlib
4. **Output**: Save processed image

### Key Algorithms

#### Denoising
- **Gaussian Blur**: `cv2.GaussianBlur()` for Gaussian noise
- **Median Filter**: `cv2.medianBlur()` for salt-and-pepper noise
- **Bilateral Filter**: `cv2.bilateralFilter()` for edge-preserving denoising

#### Sharpening
- **Convolution Kernel**: Custom sharpening kernels
- **Unsharp Mask**: High-pass filtering technique

#### Edge Detection
- **Laplacian**: `cv2.Laplacian()` for second derivative
- **Canny**: `cv2.Canny()` for optimal edge detection
- **Sobel**: `cv2.Sobel()` for gradient-based detection

#### Thresholding
- **Global**: `cv2.threshold()` with fixed threshold
- **Adaptive**: `cv2.adaptiveThreshold()` for varying illumination
- **Otsu**: Automatic threshold selection

## 🎨 Advanced Features

### Color Space Manipulation
- **HSV Conversion**: For intuitive color adjustment
- **LAB Color Space**: For perceptual color changes
- **Channel Separation**: Individual RGB channel control

### Geometric Transformations
- **Affine Transformations**: Rotation, scaling, shearing
- **Perspective Correction**: 4-point transformation
- **Lens Distortion**: Camera calibration correction

### Artistic Filters
- **Convolution Kernels**: Custom filter matrices
- **Color Quantization**: Posterization effects
- **Noise Generation**: Film grain simulation
- **Blend Modes**: Advanced color mixing

## 📊 Performance Optimization

- **NumPy Vectorization**: Fast array operations
- **OpenCV Optimization**: C++ backend for speed
- **Memory Management**: Efficient image handling
- **Real-time Preview**: Fast parameter adjustment

## 🧪 Demo and Testing

### Run the Demo
```bash
python demo.py
```

This will:
1. Create a test image with various elements
2. Apply different processing operations
3. Display results in a comparison grid
4. Save demo results as `demo_results.png`

### Test Image Features
- Gradient backgrounds
- Geometric shapes
- Text elements
- Various colors and contrasts

## 🔧 Customization

### Adding New Filters
1. Add method to `ImageProcessor` class
2. Create GUI controls in `gui_components.py`
3. Connect button to processing method

### Modifying Parameters
- Adjust slider ranges in GUI components
- Modify default values in `__init__` methods
- Add validation for parameter ranges

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --upgrade opencv-python numpy matplotlib
   ```

2. **Display Issues**
   - Ensure matplotlib backend is properly configured
   - Check if GUI framework is available

3. **Memory Issues**
   - Process smaller images for testing
   - Close other applications to free memory

4. **Performance Issues**
   - Use smaller kernel sizes for faster processing
   - Process images in chunks for large files

## 📈 Future Enhancements

- **Batch Processing**: Process multiple images
- **Undo/Redo**: Operation history
- **Layer Support**: Multi-layer editing
- **Plugin System**: Custom filter plugins
- **GPU Acceleration**: CUDA support
- **Cloud Integration**: Online processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - Feel free to use and modify for your projects.

## 🙏 Acknowledgments

- **OpenCV Community** for excellent computer vision library
- **NumPy Team** for powerful numerical computing
- **Matplotlib Team** for beautiful visualization tools
- **Python Community** for amazing ecosystem

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the demo script for examples

---

**Happy Image Processing! 🎨📸**

