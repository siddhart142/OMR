import cv2
import numpy as np
from imutils import contours

def getPerspective(response_sheet,min_area,max_area):
    
    response_sheet_gray = cv2.cvtColor(response_sheet, cv2.COLOR_BGR2GRAY)
    # response_sheet_blur = cv2.GaussianBlur(response_sheet_gray,(5,5),0)
    _, response_sheet_thresh = cv2.threshold(response_sheet_gray, 200, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    # img_erosion = cv2.erode(response_sheet_thresh, kernel, iterations=1)
    # cv2.imshow("th",response_sheet_thresh)
    # cv2.imshow("rs",img_erosion)
    # cv2.waitKey(0)
    contours, hierarchy = cv2.findContours(response_sheet_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print(contours)
    # cv2.drawContours(response_sheet, contours, -1, (0, 255, 0), 3)
    # cv2.imshow("rs",response_sheet)
    # cv2.waitKey(0)
    rects1 = []
    xmin=1000
    xmax=0
    ymin=100
    ymax=0
    idx=1
    counter = 1
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, W, H = cv2.boundingRect(cnt)
        roi=response_sheet_thresh[y:y+H,x:x+W]
        total=cv2.countNonZero(roi)
        if area > min_area and area < max_area and W>=20 and W<=27 and H>=10 and H<=17  and  total>=0.8*area :
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.drawContours(response_sheet,[cnt],-1,255,-1)
            rects1.append((x+y,x, y, w, h))
            # print("hello")

            # cv2.putText(response_sheet, str(counter), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (155, 155, 155), 2)

            counter += 1 
    # print(counter)
    # cv2.imshow("rs",response_sheet)
    # cv2.waitKey(0)
    rects1.sort(key = lambda x: x[0])
    # print(rects1)

    def is_corner(rect, page_width, page_height, threshold_distance=100):
        x, y, w, h = rect[1], rect[2], rect[3], rect[4]

        # Calculate rectangle center
        center_x = x + w // 2
        center_y = y + h // 2

        # Check distance from edges
        distance_to_edges = min(center_x, center_y, page_width - center_x, page_height - center_y)
        # print(distance_to_edges)
        # Customize this threshold based on your specific scenario
        return distance_to_edges < threshold_distance

    # Assuming page_width and page_height are known
    page_width = 595
    page_height = 841

    # Your list of rectangles
    # all_rectangles = [(132, 33, 99, 21, 11), (645, 544, 101, 22, 10), (773, 30, 743, 22, 10), (1199, 477, 722, 20, 12), (1285, 542, 743, 21, 11)]

    # Filter out corner rectangles
    rects = [rect for rect in rects1 if is_corner(rect, page_width, page_height)]

    # Now corner_rectangles should contain only the four corner rectangles
    # print(rects)

    cv2.circle(response_sheet,(rects[-1][1]+rects[-1][3],rects[-1][2]+rects[-1][4]),1,(0,0,255,128),cv2.FILLED)
    cv2.circle(response_sheet,(rects[-2][1],rects[-2][2]+rects[-2][4]),1,(0,0,255,128),cv2.FILLED)
    cv2.circle(response_sheet,(rects[1][1]+rects[1][3],rects[1][2]),1,(0,0,255,128),cv2.FILLED)
    cv2.circle(response_sheet,(rects[0][1],rects[0][2]),1,(0,0,255,128),cv2.FILLED)
    xmax=xmax+w+3
    ymax=ymax+h

    width1=rects[1][1]-rects[0][1]
    width2=rects[-1][1]-rects[-2][1]
    height1=rects[-2][2]-rects[0][2]
    height2=rects[-1][2]-rects[1][2]


    Width=max(width2,width1)
    Height=max(height2,height1)

    input_points=np.array([(rects[0][1],rects[0][2]),(rects[1][1]+rects[1][3],rects[1][2]),(rects[-2][1],rects[-2][2]+rects[2][4]),(rects[-1][1]+rects[-1][3],rects[-1][2]+rects[-1][4])], dtype=np.float32)
    converted_points=np.array([(0,0),(Width,0),(0,Height),(Width,Height)], dtype=np.float32)
    
    matrix=cv2.getPerspectiveTransform(input_points,converted_points)
    img_output=cv2.warpPerspective(response_sheet,matrix,(Width,Height))
    
    # cv2.imshow("rs",response_sheet)
    # cv2.imshow("o",img_output)
    # cv2.waitKey(0)
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