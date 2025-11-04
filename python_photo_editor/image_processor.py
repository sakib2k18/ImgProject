import cv2
import numpy as np
import math

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
    
    def generate_log_kernel(self, size, sigma):
        """Generate Laplacian of Gaussian kernel"""
        kernel = np.zeros((size, size))
        k = size // 2
        
        for i in range(-k, k+1):
            for j in range(-k, k+1):
                factor = -1 / (math.pi * sigma**4)
                sqval = i**2 + j**2
                kernel[k-j, k+i] = factor * (1 - (sqval/(2*sigma**2))) * np.exp(-sqval/(2*sigma**2))
        
        return kernel
    
    def detect_edges_with_log(self, sigma=1.0, threshold=10):
        """
        Detect edges using Laplacian of Gaussian with zero-crossing
        
        Args:
            sigma: Standard deviation for Gaussian
            threshold: Threshold for edge strength
            
        Returns:
            tuple: (edges, zero_crossings, edge_strength, log_image)
        """
        if self.current_image is None:
            return None, None, None, None
            
        # Convert to grayscale if needed
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY).astype(np.float32)
        else:
            gray = self.current_image.astype(np.float32)
        
        # Generate LoG kernel
        size = int(6 * sigma) | 1  # Ensure odd size
        log_kernel = self.generate_log_kernel(size, sigma)
        
        # Apply LoG filter
        log_image = cv2.filter2D(gray, cv2.CV_32F, log_kernel)
        
        # Find zero crossings and edge strength
        zero_crossings = np.zeros_like(gray, dtype=np.float32)
        edge_strength = np.zeros_like(gray, dtype=np.float32)
        
        for i in range(1, gray.shape[0]-1):
            for j in range(1, gray.shape[1]-1):
                # Check 4-neighborhood for zero-crossing
                if (log_image[i+1, j] * log_image[i-1, j] < 0) or \
                   (log_image[i, j+1] * log_image[i, j-1] < 0):
                    zero_crossings[i, j] = 255
                    # Calculate edge strength
                    edge_strength[i, j] = abs(log_image[i,j]-log_image[i+1,j]) + \
                                         abs(log_image[i,j]-log_image[i-1,j]) + \
                                         abs(log_image[i,j]-log_image[i,j+1]) + \
                                         abs(log_image[i,j]-log_image[i,j-1])
        
        # Apply threshold to get final edges
        edges = np.where(edge_strength > threshold, 255, 0).astype(np.uint8)
        
        # Convert to display format
        zero_crossings = zero_crossings.astype(np.uint8)
        edge_strength = cv2.normalize(edge_strength, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        log_image_disp = cv2.normalize(log_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        return edges, zero_crossings, edge_strength, log_image_disp
    
    def apply_log_edge_detection(self, sigma=1.0, threshold=10):
        """Apply LoG edge detection and update current image"""
        edges, _, _, _ = self.detect_edges_with_log(sigma, threshold)
        if edges is not None:
            self.current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
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

    def apply_histogram_equalization(self, get_intermediate=False):
        """
        Apply histogram equalization to the current image
        
        Args:
            get_intermediate: If True, returns intermediate calculations for visualization
            
        Returns:
            If get_intermediate is True, returns a dictionary with:
            - original: original image
            - equalized: equalized image
            - hist_original: histogram of original image
            - hist_equalized: histogram of equalized image
            - cdf_original: CDF of original image
            - cdf_equalized: CDF of equalized image
            - pdf_original: PDF of original image
            - pdf_equalized: PDF of equalized image
        """
        if self.current_image is None:
            return None if get_intermediate else None
            
        if not get_intermediate:
            if len(self.current_image.shape) == 3:  # Color image
                # Convert to YCrCb and equalize Y channel
                ycrcb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2YCrCb)
                ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
                self.current_image = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
            else:  # Grayscale
                self.current_image = cv2.equalizeHist(self.current_image)
            return None
            
        # If we need intermediate results for visualization
        original = self.current_image.copy()
        
        if len(original.shape) == 3:  # Color image
            # Work with Y channel only for equalization
            ycrcb = cv2.cvtColor(original, cv2.COLOR_BGR2YCrCb)
            y = ycrcb[:,:,0]
            
            # Calculate histograms
            hist_original = cv2.calcHist([y], [0], None, [256], [0, 256])
            
            # Equalize
            equalized_y = cv2.equalizeHist(y)
            hist_equalized = cv2.calcHist([equalized_y], [0], None, [256], [0, 256])
            
            # Calculate CDFs
            cdf_original = hist_original.cumsum()
            cdf_original = 255 * cdf_original / cdf_original[-1]  # Normalize
            
            cdf_equalized = hist_equalized.cumsum()
            cdf_equalized = 255 * cdf_equalized / cdf_equalized[-1]  # Normalize
            
            # Calculate PDFs
            pdf_original = hist_original / (y.shape[0] * y.shape[1])
            pdf_equalized = hist_equalized / (y.shape[0] * y.shape[1])
            
            # Create the equalized color image
            ycrcb[:,:,0] = equalized_y
            equalized = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
            
        else:  # Grayscale
            # Calculate histograms
            hist_original = cv2.calcHist([original], [0], None, [256], [0, 256])
            
            # Equalize
            equalized = cv2.equalizeHist(original)
            hist_equalized = cv2.calcHist([equalized], [0], None, [256], [0, 256])
            
            # Calculate CDFs
            cdf_original = hist_original.cumsum()
            cdf_original = 255 * cdf_original / cdf_original[-1]  # Normalize
            
            cdf_equalized = hist_equalized.cumsum()
            cdf_equalized = 255 * cdf_equalized / cdf_equalized[-1]  # Normalize
            
            # Calculate PDFs
            pdf_original = hist_original / (original.shape[0] * original.shape[1])
            pdf_equalized = hist_equalized / (original.shape[0] * original.shape[1])
        
        return {
            'original': original,
            'equalized': equalized,
            'hist_original': hist_original,
            'hist_equalized': hist_equalized,
            'cdf_original': cdf_original,
            'cdf_equalized': cdf_equalized,
            'pdf_original': pdf_original,
            'pdf_equalized': pdf_equalized
        }

    def frequency_low_pass(self, cutoff_ratio=0.1, get_intermediate=False):
        """Apply simple frequency domain low-pass filtering on grayscale image.
        
        Args:
            cutoff_ratio: fraction of the min(image_width, image_height)/2 radius to keep
            get_intermediate: if True, returns intermediate results for visualization
            
        Returns:
            If get_intermediate is True, returns a dictionary with intermediate results
        """
        if self.current_image is None:
            return None if not get_intermediate else {}
            
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
        
        if get_intermediate:
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
            filtered_spectrum = 20 * np.log(np.abs(fshift_filtered) + 1)
            phase = np.angle(fshift)
            phase_normalized = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            return {
                'original': gray,
                'filtered': img_back,
                'magnitude_spectrum': magnitude_spectrum.astype(np.uint8),
                'filtered_spectrum': filtered_spectrum.astype(np.uint8),
                'phase': phase_normalized,
                'filter_mask': (mask * 255).astype(np.uint8)
            }
        
        self.current_image = cv2.cvtColor(img_back, cv2.COLOR_GRAY2BGR)
        
    def apply_notch_filter(self, notch_centers=None, radius=5, get_intermediate=False):
        """Apply notch reject filter to remove specific frequency components.
        
        Args:
            notch_centers: List of (u,v) tuples for notch centers. If None, will try to detect automatically
            radius: Radius of the notch filter
            get_intermediate: If True, returns intermediate results for visualization
            
        Returns:
            If get_intermediate is True, returns a dictionary with intermediate results
        """
        if self.current_image is None:
            return None if not get_intermediate else {}
            
        # Convert to grayscale if needed
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
            
        # Perform FFT
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        
        # Create notch filter mask
        h, w = gray.shape
        notch_mask = np.ones((h, w), dtype=np.float32)
        center_u, center_v = h // 2, w // 2
        
        if notch_centers is None:
            # Try to detect periodic noise automatically (simple peak detection)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
            magnitude_spectrum = magnitude_spectrum.astype(np.uint8)
            
            # Find bright spots in the magnitude spectrum
            _, thresh = cv2.threshold(magnitude_spectrum, 200, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            notch_centers = []
            for cnt in contours:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    # Only add if it's not too close to the center
                    if (cX - center_v) ** 2 + (cY - center_u) ** 2 > 100:
                        notch_centers.append((cX, cY))
            
            # If no centers found, use default positions
            if not notch_centers:
                notch_centers = [(h//4, w//4), (3*h//4, 3*w//4)]
        
        # Apply notch filter
        u, v = np.meshgrid(np.arange(w), np.arange(h))
        for center in notch_centers:
            x, y = center
            # Create notch pair (symmetric about center)
            D1 = np.sqrt((u - x) ** 2 + (v - y) ** 2)
            D2 = np.sqrt((u - (2*center_v - x)) ** 2 + (v - (2*center_u - y)) ** 2)
            notch_mask = notch_mask * (D1 > radius) * (D2 > radius)
        
        # Apply the filter
        fshift_filtered = fshift * notch_mask
        f_ishift = np.fft.ifftshift(fshift_filtered)
        img_filtered = np.fft.ifft2(f_ishift)
        img_filtered = np.abs(img_filtered).clip(0, 255).astype(np.uint8)
        
        if get_intermediate:
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
            filtered_spectrum = 20 * np.log(np.abs(fshift_filtered) + 1)
            phase = np.angle(fshift)
            phase_normalized = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            return {
                'original': gray,
                'filtered': img_filtered,
                'magnitude_spectrum': magnitude_spectrum.astype(np.uint8),
                'filtered_spectrum': filtered_spectrum.astype(np.uint8),
                'phase': phase_normalized,
                'filter_mask': (notch_mask * 255).astype(np.uint8),
                'notch_centers': notch_centers,
                'radius': radius
            }
        
        # Update the current image
        if len(self.current_image.shape) == 3:
            self.current_image = cv2.cvtColor(img_filtered, cv2.COLOR_GRAY2BGR)
        else:
            self.current_image = img_filtered
    
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

    # ==================== COLOR CHANNEL OPERATIONS ====================
    
    def view_rgb_channel(self, channel='R'):
        """View a specific RGB channel as grayscale
        
        Args:
            channel: 'R', 'G', or 'B' for the channel to view
        """
        if self.current_image is None:
            return False
            
        try:
            # Convert to BGR if grayscale
            if len(self.current_image.shape) == 2:
                self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_GRAY2BGR)
                
            # Split channels (OpenCV uses BGR order)
            b, g, r = cv2.split(self.current_image)
            
            # Select the requested channel and convert to 3-channel grayscale
            if channel.upper() == 'R':
                self.current_image = cv2.merge([r, r, r])
            elif channel.upper() == 'G':
                self.current_image = cv2.merge([g, g, g])
            else:  # Default to Blue channel
                self.current_image = cv2.merge([b, b, b])
                
            return True
            
        except Exception as e:
            print(f"Error viewing RGB channel {channel}: {e}")
            return False
    
    def view_hsv_channel(self, channel='H'):
        """View a specific HSV channel as grayscale
        
        Args:
            channel: 'H', 'S', or 'V' for the channel to view
        """
        if self.current_image is None:
            return False
            
        try:
            # Convert to BGR if grayscale
            if len(self.current_image.shape) == 2:
                self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_GRAY2BGR)
                
            # Convert to HSV and split channels
            hsv = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            # Select the requested channel and convert to 3-channel grayscale
            if channel.upper() == 'H':
                # For Hue, we need to normalize to 0-255 for display
                h_normalized = cv2.normalize(h, None, 0, 255, cv2.NORM_MINMAX)
                self.current_image = cv2.merge([h_normalized, h_normalized, h_normalized])
            elif channel.upper() == 'S':
                self.current_image = cv2.merge([s, s, s])
            else:  # Default to Value channel
                self.current_image = cv2.merge([v, v, v])
                
            return True
            
        except Exception as e:
            print(f"Error viewing HSV channel {channel}: {e}")
            return False
       
    
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
