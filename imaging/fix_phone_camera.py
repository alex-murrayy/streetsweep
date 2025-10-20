#!/usr/bin/env python3
"""
Fix phone camera connection for Continuity Camera.
"""

import subprocess
import cv2
import time

def check_continuity_camera_status():
    """Check if Continuity Camera is available."""
    print("📱 Checking Continuity Camera Status...")
    print("=" * 40)
    
    # Check system cameras
    try:
        result = subprocess.run(['system_profiler', 'SPCameraDataType'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            camera_output = result.stdout.lower()
            if 'continuity' in camera_output or 'iphone' in camera_output:
                print("✅ Continuity Camera detected in system!")
                return True
            else:
                print("❌ Continuity Camera not detected in system")
                print("📋 System cameras found:")
                print(result.stdout)
                return False
        else:
            print("❌ Could not check system cameras")
            return False
    except Exception as e:
        print(f"❌ Error checking cameras: {e}")
        return False

def test_all_camera_indices():
    """Test all camera indices to see if phone appears."""
    print("\n🧪 Testing All Camera Indices...")
    print("=" * 35)
    
    found_cameras = []
    
    for i in range(10):
        print(f"Testing camera {i}...", end=" ")
        
        # Try AVFoundation backend (best for Continuity Camera)
        cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                found_cameras.append({
                    'index': i,
                    'resolution': f"{width}x{height}",
                    'fps': fps,
                    'backend': 'AVFoundation'
                })
                print(f"✅ Working ({width}x{height})")
            else:
                print("⚠️  Opens but no frame")
            cap.release()
        else:
            print("❌ Not available")
    
    return found_cameras

def provide_continuity_camera_solutions():
    """Provide step-by-step solutions for Continuity Camera."""
    print("\n🔧 Continuity Camera Solutions:")
    print("=" * 35)
    
    print("\n1. 📱 On Your iPhone:")
    print("   • Make sure iPhone is unlocked and nearby (within 10 feet)")
    print("   • Go to Settings > General > AirPlay & Handoff")
    print("   • Turn OFF Continuity Camera, wait 5 seconds, turn ON")
    print("   • Try opening the Camera app on your iPhone")
    print("   • Make sure both devices are signed into same Apple ID")
    
    print("\n2. 💻 On Your Mac:")
    print("   • Check System Preferences > Security & Privacy > Camera")
    print("   • Make sure your terminal/IDE has camera permissions")
    print("   • Try restarting your terminal")
    print("   • Check if both devices are on same Wi-Fi network")
    print("   • Make sure Bluetooth is enabled on both devices")
    
    print("\n3. 🔄 Reset Continuity Camera:")
    print("   • On iPhone: Settings > General > AirPlay & Handoff")
    print("   • Turn OFF Continuity Camera")
    print("   • Wait 10 seconds")
    print("   • Turn ON Continuity Camera")
    print("   • On Mac: Restart your terminal")
    
    print("\n4. 🔌 Try USB Connection:")
    print("   • Connect iPhone via USB cable")
    print("   • When prompted, tap 'Trust This Computer'")
    print("   • This sometimes helps establish the connection")
    
    print("\n5. 📶 Check Network:")
    print("   • Make sure both devices are on same Wi-Fi")
    print("   • Try turning Wi-Fi off and on on iPhone")
    print("   • Make sure Bluetooth is enabled on both devices")

def test_manual_steps():
    """Guide user through manual steps to enable Continuity Camera."""
    print("\n📱 Manual Continuity Camera Setup:")
    print("=" * 40)
    
    print("Follow these steps:")
    print("1. Make sure your iPhone is nearby and unlocked")
    print("2. On iPhone: Go to Settings > General > AirPlay & Handoff")
    print("3. Turn OFF Continuity Camera, wait 5 seconds, turn ON")
    print("4. On iPhone: Open the Camera app")
    print("5. On Mac: Wait 10 seconds")
    print("6. Press Enter when ready to test...")
    
    input("Press Enter when you've completed the steps above...")
    
    print("\n🧪 Testing cameras now...")
    cameras = test_all_camera_indices()
    
    if len(cameras) > 1:
        print(f"\n✅ Found {len(cameras)} cameras!")
        for cam in cameras:
            print(f"   Camera {cam['index']}: {cam['resolution']} ({cam['backend']})")
        
        print("\n💡 If you see more than one camera, one might be your iPhone!")
        print("💡 Try testing each camera to see which one is your iPhone")
    else:
        print("\n❌ Still only seeing one camera")
        print("💡 Continuity Camera might not be working yet")

def main():
    """Main troubleshooting function."""
    print("🔧 Phone Camera Troubleshooter")
    print("=" * 40)
    
    # Check current status
    continuity_detected = check_continuity_camera_status()
    
    # Test all camera indices
    cameras = test_all_camera_indices()
    
    print(f"\n📊 Current Status:")
    print(f"   Continuity Camera in system: {'✅' if continuity_detected else '❌'}")
    print(f"   Total cameras found: {len(cameras)}")
    
    if len(cameras) > 1:
        print("✅ Multiple cameras detected! One might be your iPhone")
        for cam in cameras:
            print(f"   Camera {cam['index']}: {cam['resolution']}")
    else:
        print("❌ Only one camera detected (your Mac's built-in camera)")
    
    # Provide solutions
    provide_continuity_camera_solutions()
    
    # Offer manual test
    print("\n" + "="*50)
    response = input("Would you like to try the manual setup steps? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        test_manual_steps()
    
    print("\n🎯 Next Steps:")
    print("1. Try the solutions above")
    print("2. Run: python camera_switcher.py --list")
    print("3. If camera 0 works, it might be your phone camera")
    print("4. Test with: python main.py --source 0")

if __name__ == "__main__":
    main()
