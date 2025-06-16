import serial
import numpy as np
import cv2

# Serial port configuration
baudrate = 115200
port = '/dev/ttyACM0'
ser = serial.Serial(port, baudrate=baudrate, timeout=1)

# Image configuration
width, height = 32, 32  # Sensor resolution
frame_size_bytes = width * height * 2  # 2 bytes per pixel (uint16)
scale_factor = 20  # Resize for display

# Conversion function (adjust if your sensor has a different scale)
def raw_to_celsius(raw_frame):
    print(raw_frame)
    return raw_frame / 10.0

while True:
    # Read one full frame from serial
    data = ser.read(frame_size_bytes)
    if len(data) != frame_size_bytes:
        continue  # Skip incomplete frames

    # Convert to 16-bit and reshape
    frame_raw = np.frombuffer(data, dtype=np.uint16).reshape((height, width))

    # Convert to Celsius
    frame_celsius = raw_to_celsius(frame_raw)

    # Normalize to 8-bit for color display
    frame_8bit = cv2.normalize(frame_raw, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    color_frame = cv2.applyColorMap(frame_8bit, cv2.COLORMAP_JET)

    # Resize the frame
    big_frame = cv2.resize(color_frame,
                           (width * scale_factor, height * scale_factor),
                           interpolation=cv2.INTER_LANCZOS4)

    # Find min and max temps and their positions
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(frame_celsius)

    # Draw text
    cv2.putText(big_frame, f"Min: {min_val:.1f}C", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(big_frame, f"Max: {max_val:.1f}C", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Draw circles at min/max points
    cv2.circle(big_frame, (max_loc[0]*scale_factor, max_loc[1]*scale_factor), 5, (255, 255, 255), -1)
    cv2.circle(big_frame, (min_loc[0]*scale_factor, min_loc[1]*scale_factor), 5, (0, 0, 0), -1)

    # Display
    cv2.imshow("TIOP01 IR Live Feed", big_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
ser.close()
cv2.destroyAllWindows()
