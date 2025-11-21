import win32ui
import win32gui
import win32con
import win32api
from PIL import Image
import io
import base64

def get_icon_base64(exe_path):
    """
    Extracts the icon from an executable and returns it as a base64 encoded PNG string.
    Returns None if extraction fails.
    """
    try:
        # Get the large icon handle
        large, small = win32gui.ExtractIconEx(exe_path, 0)
        
        if not large:
            return None
            
        hIcon = large[0]
        
        # Create a device context
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, 32, 32)
        hdc = hdc.CreateCompatibleDC()
        
        hdc.SelectObject(hbmp)
        
        # Draw the icon
        hdc.DrawIcon((0, 0), hIcon)
        
        # Convert to PIL Image
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGBA',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRA', 0, 1
        )
        
        # Clean up
        win32gui.DestroyIcon(hIcon)
        win32gui.DestroyIcon(small[0]) if small else None
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    except Exception as e:
        # print(f"Error extracting icon from {exe_path}: {e}")
        return None
