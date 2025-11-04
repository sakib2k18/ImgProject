import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self._history = []
        self._redo_stack = []
        
    def load_image(self, image_path):
        """Load image from file path"""
        try:
            self.original_image = cv2.imread(image_path)
            if self.original_image is None:
                raise ValueError("Could not load image")
            self.current_image = self.original_image.copy()
            self._history = []
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def get_image_for_display(self):
        """Get current image converted for display (BGR to RGB)"""
        if self.current_image is not None:
            return cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        return None
    
    def reset_image(self):
        """Reset to original image"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self._history = []

    # ==================== UNDO SUPPORT ====================

    def push_state(self):
        """Push the current image to history for undo."""
        if self.current_image is not None:
            self._history.append(self.current_image.copy())
            # Clear redo stack when a new state is pushed
            self._redo_stack = []

    def undo(self):
        """Undo the last operation if possible."""
        if self._history:
            # Save current state to redo stack
            self._redo_stack.append(self.current_image.copy())
            # Restore previous state
            self.current_image = self._history.pop()
            return True
        return False
        
    def redo(self):
        """Redo the last undone operation if possible."""
        if self._redo_stack:
            # Save current state to history
            self._history.append(self.current_image.copy())
            # Restore next state from redo stack
            self.current_image = self._redo_stack.pop()
            return True
        return False
    
    # ==================== DENOISING & SMOOTHING ====================
    
    def gaussian_denoise(self, kernel_size=5, sigma=1.0):
        """Apply Gaussian blur for denoising"""
        if self.current_image is not None:
            self.current_image = cv2.GaussianBlur(self.current_image, (kernel_size, kernel_size), sigma)
    
    # ==================== SHARPENING ====================
    
    def sharpen(self, strength=1.0):
        """Apply sharpening filter"""
        if self.current_image is not None:
            # Create parameterized Laplacian-style sharpening kernel
            # s controls sharpening amount; s=1 yields classic kernel [[0,-1,0],[-1,5,-1],[0,-1,0]]
            s = float(max(0.0, strength))
            kernel = np.array([[0,    -s,   0],
                               [-s,  1+4*s, -s],
                               [0,    -s,   0]], dtype=np.float32)
            
            # Apply convolution
            self.current_image = cv2.filter2D(self.current_image, -1, kernel)
            # Ensure values are in valid range
            self.current_image = np.clip(self.current_image, 0, 255).astype(np.uint8)

    # ==================== MANUAL CONVOLUTION ====================

    def manual_convolution(self, kernel):
        """
        Apply manual 2D convolution with the given kernel
        
        Args:
            kernel: 2D numpy array representing the convolution kernel
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.current_image is None:
            return False
            
        try:
            # Convert to grayscale if image is color
            if len(self.current_image.shape) == 3:
                img_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            else:
                img_gray = self.current_image
                
            # Get image dimensions
            h, w = img_gray.shape
            
            # Kernel properties
            kernel_h, kernel_w = kernel.shape
            kernel_center_h = kernel_h // 2
            kernel_center_w = kernel_w // 2
            
            # Calculate padding
            padding_top = kernel_h - kernel_center_h - 1
            padding_bottom = kernel_center_h
            padding_left = kernel_w - kernel_center_w - 1
            padding_right = kernel_center_w
            
            # Apply padding
            img_bordered = cv2.copyMakeBorder(
                src=img_gray,
                top=padding_top,
                bottom=padding_bottom,
                left=padding_left,
                right=padding_right,
                borderType=cv2.BORDER_REFLECT
            )
            
            # Initialize output image
            output_image = np.zeros((h, w), np.float32)
            
            # Apply convolution
            for i in range(h):
                for j in range(w):
                    sum_val = 0
                    for m in range(kernel_h):
                        for n in range(kernel_w):
                            sum_val += kernel[m, n] * img_bordered[i + m, j + n]
                    output_image[i, j] = sum_val
            
            # Normalize and convert to uint8
            output_image = np.round(cv2.normalize(output_image, None, 0, 255, cv2.NORM_MINMAX)).astype(np.uint8)
            
            # Update the current image
            self.current_image = output_image
            return True
            
        except Exception as e:
            print(f"Error in manual convolution: {e}")
            return False            
    
    # ==================== EDGE DETECTION ====================
    
    def laplacian_edge_detection(self):
        """Apply Laplacian edge detection"""
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian = np.uint8(np.absolute(laplacian))
            self.current_image = cv2.cvtColor(laplacian, cv2.COLOR_GRAY2BGR)
    
    def canny_edge_detection(self, threshold1=50, threshold2=150):
        """Apply Canny edge detection"""
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, threshold1, threshold2)
            self.current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def sobel_edge_detection(self):
        """Apply Sobel edge detection"""
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            
            # Sobel X and Y
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate magnitude
            magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            magnitude = np.uint8(magnitude / magnitude.max() * 255)
            
            self.current_image = cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)

    def zero_crossing_edge_detection(self, sigma=1.0):
        """Apply Zero-Crossing edge detection using Laplacian of Gaussian."""
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (0, 0), sigma)
            log = cv2.Laplacian(blurred, cv2.CV_64F)
            # Detect zero-crossings: sign change in a 3x3 neighborhood
            sign = np.sign(log)
            shifted = [
                np.roll(sign, 1, axis=0), np.roll(sign, -1, axis=0),
                np.roll(sign, 1, axis=1), np.roll(sign, -1, axis=1),
                np.roll(sign, (1,1), axis=(0,1)), np.roll(sign, (1,-1), axis=(0,1)),
                np.roll(sign, (-1,1), axis=(0,1)), np.roll(sign, (-1,-1), axis=(0,1))
            ]
            zero_cross = np.zeros_like(sign, dtype=np.uint8)
            for s in shifted:
                zero_cross |= (sign * s) < 0
            edges = (zero_cross * 255).astype(np.uint8)
            self.current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # ==================== THRESHOLDING ====================
    
    def global_threshold(self, threshold_value=127, max_value=255, threshold_type=cv2.THRESH_BINARY):
        """Apply global thresholding"""
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, threshold_value, max_value, threshold_type)
            self.current_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    def histogram_equalization(self):
        """Apply histogram equalization on grayscale image."""
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            eq = cv2.equalizeHist(gray)
            self.current_image = cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)


    def frequency_low_pass(self, cutoff_ratio=0.1):
        """Apply simple frequency domain low-pass filtering on grayscale image.
        cutoff_ratio: fraction of the min(image_width, image_height)/2 radius to keep.
        """
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            rows, cols = gray.shape
            crow, ccol = rows // 2, cols // 2
            radius = int(min(crow, ccol) * max(0.0, min(1.0, cutoff_ratio)))
            Y, X = np.ogrid[:rows, :cols]
            mask = (X - ccol) ** 2 + (Y - crow) ** 2 <= radius ** 2
            fshift_filtered = fshift * mask
            f_ishift = np.fft.ifftshift(fshift_filtered)
            img_back = np.fft.ifft2(f_ishift)
            img_back = np.abs(img_back)
            img_back = np.clip(img_back, 0, 255).astype(np.uint8)
            self.current_image = cv2.cvtColor(img_back, cv2.COLOR_GRAY2BGR)
    
    # ==================== COLOR MANIPULATION ====================
    
    def convert_to_grayscale(self):
        """Convert image to grayscale"""
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            self.current_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
    def convert_to_binary(self, threshold=127):
        """
        Convert image to binary (black and white) using a threshold
        
        Args:
            threshold (int): Threshold value (0-255)
        """
        if self.current_image is not None:
            # Convert to grayscale first if needed
            if len(self.current_image.shape) == 3:
                gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.current_image
                
            # Apply threshold
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
            self.current_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    def view_rgb_channel(self, channel='R'):
        """View a single RGB channel as a grayscale image displayed in BGR format."""
        if self.current_image is not None:
            b, g, r = cv2.split(self.current_image)
            if channel.upper() == 'R':
                ch = r
            elif channel.upper() == 'G':
                ch = g
            else:
                ch = b
            self.current_image = cv2.cvtColor(ch, cv2.COLOR_GRAY2BGR)

    def view_hsv_channel(self, channel='H'):
        """View a single HSV channel (H,S,V) as a grayscale image displayed in BGR format."""
        if self.current_image is not None:
            hsv = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            if channel.upper() == 'H':
                ch = h
            elif channel.upper() == 'S':
                ch = s
            else:
                ch = v
            self.current_image = cv2.cvtColor(ch, cv2.COLOR_GRAY2BGR)
    
    
    
    # ==================== GEOMETRIC TRANSFORMATIONS ====================
    
    def rotate_image(self, angle):
        """Rotate image by specified angle"""
        if self.current_image is not None:
            height, width = self.current_image.shape[:2]
            center = (width // 2, height // 2)
            
            # Get rotation matrix
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Calculate new dimensions
            cos = np.abs(rotation_matrix[0, 0])
            sin = np.abs(rotation_matrix[0, 1])
            new_width = int((height * sin) + (width * cos))
            new_height = int((height * cos) + (width * sin))
            
            # Adjust rotation matrix for new center
            rotation_matrix[0, 2] += (new_width / 2) - center[0]
            rotation_matrix[1, 2] += (new_height / 2) - center[1]
            
            # Apply rotation
            self.current_image = cv2.warpAffine(self.current_image, rotation_matrix, (new_width, new_height))
    
    def flip_image(self, direction='horizontal'):
        """Flip image horizontally or vertically"""
        if self.current_image is not None:
            if direction == 'horizontal':
                self.current_image = cv2.flip(self.current_image, 1)
            elif direction == 'vertical':
                self.current_image = cv2.flip(self.current_image, 0)
    
    
    def save_image(self, output_path):
        """Save current image to file"""
        if self.current_image is not None:
            cv2.imwrite(output_path, self.current_image)
            return True
        return False
