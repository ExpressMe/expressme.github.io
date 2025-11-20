# uv sync && uv run src/optimize.py

import os
from pathlib import Path
from PIL import Image
import sys

def optimize_images():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    images_dir = script_dir / "images"
    
    # Optimized directory is one level above the script directory
    optimized_dir = script_dir.parent / "optimized"
    
    # Supported image extensions
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    # Create optimized directory if it doesn't exist
    optimized_dir.mkdir(exist_ok=True)
    
    # Counter for tracking processed images
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"Starting image optimization...")
    print(f"Script directory: {script_dir}")
    print(f"Source: {images_dir}")
    print(f"Destination: {optimized_dir}")
    print("-" * 50)
    
    # Walk through all files in the images directory recursively
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            file_path = Path(root) / file
            file_extension = file_path.suffix.lower()
            
            # Skip non-image files
            if file_extension not in supported_extensions:
                continue
            
            # Calculate relative path from images directory
            relative_path = file_path.relative_to(images_dir)
            
            # Create corresponding path in optimized directory with .webp extension
            optimized_path = optimized_dir / "images" / relative_path.with_suffix('.webp')
            
            # Create parent directories if they don't exist
            optimized_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if optimized version already exists
            if optimized_path.exists():
                print(f"✓ Skipped (already exists): {relative_path}")
                skipped_count += 1
                continue
            
            try:
                # Open and process the image
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary (for PNG with transparency)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create a white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Calculate new dimensions while maintaining aspect ratio
                    max_width = 1000
                    original_width, original_height = img.size
                    
                    if original_width > max_width:
                        # Calculate new height maintaining aspect ratio
                        new_width = max_width
                        new_height = int((original_height / original_width) * max_width)
                        
                        # Resize the image
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        resize_info = f"resized from {original_width}x{original_height} to {new_width}x{new_height}"
                    else:
                        resize_info = f"kept original size {original_width}x{original_height}"
                    
                    # Save as WebP with quality 70
                    img.save(optimized_path, 'WEBP', quality=70)
                    
                    # Get file size info
                    original_size = file_path.stat().st_size
                    optimized_size = optimized_path.stat().st_size
                    size_reduction = ((original_size - optimized_size) / original_size) * 100
                    
                    print(f"✓ Processed: {relative_path} ({resize_info}) - "
                          f"Size: {original_size/1024:.1f}KB → {optimized_size/1024:.1f}KB "
                          f"({size_reduction:.1f}% reduction)")
                    
                    processed_count += 1
                    
            except Exception as e:
                print(f"✗ Error processing {relative_path}: {str(e)}")
                error_count += 1
    
    # Print summary
    print("-" * 50)
    print(f"Optimization complete!")
    print(f"Processed: {processed_count} images")
    print(f"Skipped: {skipped_count} images (already optimized)")
    print(f"Errors: {error_count} images")
    
    if error_count > 0:
        print(f"\nNote: {error_count} images could not be processed. Check the errors above.")

if __name__ == "__main__":
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow library is required but not installed.")
        print("Please install it using: pip install Pillow")
        sys.exit(1)
    
    optimize_images()