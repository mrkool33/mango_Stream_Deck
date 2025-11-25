"""
Icon Creator for Mango Stream Deck
Creates a multi-resolution .ico file from transparent PNG logos
"""

from PIL import Image
import os

def create_icon():
    """Create .ico file with multiple resolutions"""
    
    # Define logo paths
    logo_256 = "logos/mango_256_transparent.png"
    logo_32 = "logos/mango_32_transparent.png"
    
    # Check if files exist
    if not os.path.exists(logo_256):
        print(f"Error: {logo_256} not found!")
        return
    
    try:
        # Load the 256x256 image as the base
        img_256 = Image.open(logo_256)
        
        # Create additional sizes from 256x256 for better quality
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        images = []
        
        for size in sizes:
            if size == (256, 256):
                images.append(img_256)
            elif size == (32, 32) and os.path.exists(logo_32):
                # Use the dedicated 32x32 if available
                images.append(Image.open(logo_32))
            else:
                # Resize from 256x256 with high-quality resampling
                resized = img_256.resize(size, Image.Resampling.LANCZOS)
                images.append(resized)
        
        # Save as multi-resolution .ico file
        output_path = "icon.ico"
        img_256.save(
            output_path,
            format='ICO',
            sizes=sizes
        )
        
        print(f"✓ Icon created successfully: {output_path}")
        print(f"  Resolutions included: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        print(f"\nUsage with PyInstaller:")
        print(f"  pyinstaller --onefile --windowed --icon={output_path} main.py")
        
    except Exception as e:
        print(f"Error creating icon: {e}")

if __name__ == "__main__":
    create_icon()
