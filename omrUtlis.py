import cv2
import numpy as np


def getPerspective(response_sheet,min_area,max_area):
    
# Parameters (Adjust as needed)

    # Read image (Assuming response_sheet is pre-loaded)
    response_sheet_gray = cv2.cvtColor(response_sheet, cv2.COLOR_BGR2GRAY)
    _, response_sheet_thresh = cv2.threshold(response_sheet_gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(response_sheet_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects1 = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        roi = response_sheet_thresh[y:y+h, x:x+w]
        total = cv2.countNonZero(roi)

        # Filter based on size and filled area
        if min_area < area < max_area and 18 <= w <= 27 and 10 <= h <= 17 and total >= 0.8 * area:
            rects1.append((x, y, w, h))  # Store only needed values

    # Ensure at least 4 points are found
    if len(rects1) < 4:
        raise ValueError("Less than 4 valid boxes found! Adjust filtering parameters.")

    # Sort by x-coordinate (leftmost to rightmost)
    rects1.sort(key=lambda r: r[0])

    # print(rects1)
    # Get two extreme left and two extreme right
    left_boxes = sorted(rects1[:2], key=lambda r: r[1])   # Sort leftmost by y (top, bottom)
    right_boxes = sorted(rects1[-2:], key=lambda r: r[1]) # Sort rightmost by y (top, bottom)

    # print(left_boxes)
    # print(right_boxes)

    # Extract final corner points
    top_left, bottom_left = left_boxes
    top_right, bottom_right = right_boxes

    # Draw detected points for debugging
    for (x, y, w, h) in [top_left, top_right, bottom_left, bottom_right]:
        cv2.circle(response_sheet, (x + w//2, y + h//2), 5, (0, 0, 255), -1)

    # cv2.imshow("Detected Corners", response_sheet)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # ---- Perspective Transformation ----
    Width = top_right[0] + top_right[2] - top_left[0]  # Right-most x - Left-most x
    Height = bottom_left[1] + bottom_left[3] - top_left[1]  # Bottom-most y - Top-most y

    # Define input points (Detected positions)
    input_points = np.array([
        (top_left[0], top_left[1]),  # Top-left
        (top_right[0] + top_right[2], top_right[1]),  # Top-right
        (bottom_left[0], bottom_left[1] + bottom_left[3]),  # Bottom-left
        (bottom_right[0] + bottom_right[2], bottom_right[1] + bottom_right[3])  # Bottom-right
    ], dtype=np.float32)

    # Define output points (Perfectly aligned rectangle)
    converted_points = np.array([
        (0, 0),  # Top-left
        (Width, 0),  # Top-right
        (0, Height),  # Bottom-left
        (Width, Height)  # Bottom-right
    ], dtype=np.float32)

    # Get transformation matrix
    matrix = cv2.getPerspectiveTransform(input_points, converted_points)

    # Apply perspective transformation
    img_output = cv2.warpPerspective(response_sheet, matrix, (Width, Height))

    # Display final transformed image
    # cv2.imshow("Transformed", img_output)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return img_output




def coOrdinates(i,j,row,col,response_sheet_thresh):
    x=row[i][0]
    y=col[j][1]
    w=col[j][2]
    h=col[j][3]
    roi=response_sheet_thresh[y:y+h,x:x+w]
    total=cv2.countNonZero(roi)

    return x,y,w,h,roi,total
def markTheRegion(ansx,ansy,answ,ansh,responseROI,color):
    center_x = ansx + (answ / 2)
    center_y = ansy + (ansh / 2)
    cv2.circle(responseROI, (int(center_x), int(center_y)), 4, (color), -1) # Draw the center point