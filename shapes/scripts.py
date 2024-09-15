import cv2
import numpy as np

def get_color_name(hsv):
    h, s, v = hsv
    if s < 40:
        return "Gray"
    elif h < 10 or h >= 170:
        return "Red"
    elif 10 <= h < 25:
        return "Orange"
    elif 25 <= h < 35:
        return "Yellow"
    elif 35 <= h < 85:
        return "Green"
    elif 85 <= h < 125:
        return "Blue"
    elif 125 <= h < 170:
        return "Purple"
    else:
        return "Undefined"

image_1 = cv2.imread("shape.jpg", 1)
image_1 = cv2.resize(image_1, (1100, 612))

image_1Grey = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)
_, thrash = cv2.threshold(image_1Grey, 220, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thrash, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for contour in contours:
    approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)   # this a method to detect the polygon you pass contour and accuracy and True in either for telling to detect closed shapes
    cv2.drawContours(image_1, [approx], 0, [0, 0, 0], 5)
    
    x = approx.ravel()[0]
    y = approx.ravel()[1]
    
    mask = np.zeros_like(image_1)
    cv2.drawContours(mask, [approx], -1, (255, 255, 255), -1)
    
    mean_val = cv2.mean(image_1, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))[:3]
    mean_hsv = cv2.cvtColor(np.uint8([[mean_val]]), cv2.COLOR_BGR2HSV)[0][0]
    color_name = get_color_name(mean_hsv)
    
    if len(approx) == 3:
        cv2.putText(image_1, f"Triangle,{color_name}", (x, y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
    elif len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspectRatio = float(w) / h
        if 0.8 <= aspectRatio <= 1.05:
            cv2.putText(image_1, f"Square,{color_name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
        else:
            cv2.putText(image_1, f"Rectangle,{color_name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
    elif len(approx) > 11:
        cv2.putText(image_1, f"Circle ,{color_name}", (x, y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

cv2.imshow("Displayed Image", image_1)
cv2.waitKey(0)
cv2.destroyAllWindows()