import cv2
import numpy as np
import omrUtlis
from imutils import contours
import csv
import os
import pandas as pd
import math

def element_exists(lst, element1,element2):
    if element1 in lst or element2 in lst:
        return True
    return False
def process_omr_sheet(image_path,filename, Sno, posScore, negScore, unattemptScore, threshold, answerKey,NoOfQues,selected_certificate):
    try:
    # Defining answers
        column_indices = [0,1,2,3,4] 

        # Read the Excel file and store the data in DataFrames for each set
        set_A_df = pd.read_excel(answerKey, sheet_name='setA', engine='openpyxl',usecols=column_indices)
        set_B_df = pd.read_excel(answerKey, sheet_name='setB', engine='openpyxl',usecols=column_indices)
        set_C_df = pd.read_excel(answerKey, sheet_name='setC', engine='openpyxl',usecols=column_indices)
        set_D_df = pd.read_excel(answerKey, sheet_name='setD', engine='openpyxl',usecols=column_indices)

        # Convert the DataFrames to lists of lists for each set
        set_A = set_A_df.values.tolist()
        set_B = set_B_df.values.tolist()
        set_C = set_C_df.values.tolist()
        set_D = set_D_df.values.tolist()

        Answer_key=[set_A, set_B, set_C, set_D]


        Set=0
        schoolCode=""
        regNo="UP2"

        responseImg=cv2.imread(image_path)
        # print(responseImg.shape)
        # cv2.imshow("img",responseImg)
        # cv2.waitKey(0)
        scale_percent = 18  # percent of original size
        # 1052, 744
        # 595 841

        # Calculate the new dimensions
        width = int(595)
        height = int(841)

        # print(width,height)
        # Resize the Image
        responseImg=cv2.resize(responseImg,(width,height),interpolation = cv2.INTER_AREA)
        # cv2.imshow("img",responseImg)
        # cv2.waitKey(0)
        #Get perspective
        responseROI=omrUtlis.getPerspective(responseImg,150,250)
        mainImage = responseROI.copy()
        # cv2.imshow("p",mainImage)
        # Pre-processing
        response_sheet_gray = cv2.cvtColor(responseROI, cv2.COLOR_BGR2GRAY)
        # response_sheet_blur=cv2.GaussianBlur(response_sheet_gray, (5, 5), 0)
        _, response_sheet_thresh = cv2.threshold(response_sheet_gray, 200, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # kernel = np.ones((3, 3), np.uint8)
        # response_sheet_blur = cv2.GaussianBlur(response_sheet_gray,(5,5),0)
        # _, response_sheet_thresh = cv2.threshold(response_sheet_gray, 200, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # img_erosion = cv2.erode(response_sheet_thresh, kernel, iterations=1)
        # img_ero = cv2.erode(response_sheet_gray, kernel, iterations=1)
        # cv2.imshow("th",response_sheet_thresh)
        # cv2.imshow("rs",img_erosion)
        # cv2.imshow("rss",img_ero)
        # cv2.waitKey(0)
        # #Get contours
        contours, hierarchy = cv2.findContours(response_sheet_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # cv2.drawContours(mainImage, contours, -1, (0, 255, 0), 3)
        # cv2.imshow("rs",mainImage)
        # cv2.waitKey(0)

        # #Extract Rectangles
        idx=0
        minX=10000000
        minY=10000000
        rects=[]
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            roi=response_sheet_thresh[y:y+h,x:x+w]
            aspectRatio=max(h,w)/min(h,w)
            if area>=40 and area<=90 and aspectRatio>=0.8:
                cv2.drawContours(mainImage, cnt, -1, (0, 255, 0), 3)
                rects.append((x,y,w,h))
                minX=min(minX,x)
                minY=min(minY,y)
                idx+=1
                # print(area)
        # print(minX,minY)
        # cv2.imshow("rs",mainImage)
        # cv2.waitKey(0)
        col=[]
        row=[]
        for rect in rects:
            if rect[0]>=minX-25 and rect[0]<=minX+25:
                col.append(rect)
                cv2.circle(responseROI,(rect[0],rect[1]),3,(0,0,255),cv2.FILLED)
            elif rect[1]>=minY-5 and rect[1]<=minY+5:
                row.append((rect[0],rect[1]))
                cv2.circle(responseROI,(rect[0],rect[1]),3,(0,0,255),cv2.FILLED)
        
        # cv2.imwrite(imageROI.png,responseROI )
        # cv2.imshow("rs",responseROI)
        # cv2.waitKey(0)
        # Sorting row and col matrix
        row.sort(key = lambda x: x[0])
        col.sort(key = lambda x: x[1])


        midRow=[]
        for rect in rects:
            start=col[9][1]
            end=col[10][1]
            if rect[1]>start+5 and rect[1]<end-5:
                midRow.append((rect[0],rect[1]))
                cv2.circle(responseROI,(rect[0],rect[1]),3,(0,0,255),cv2.FILLED)   
        midRow.sort(key = lambda x: x[0])
        # cv2.imshow("rs",responseROI)
        # cv2.waitKey(0)
        # print(row)
        # print(col)
        # print(midRow)


        # Determining the set 
        x=row[13][0]
        Gtotal=35
        errorS=1
        color=(0,255,255)
        for i in range(0,4):
            y=col[i][1]
            w=col[i][2]
            h=col[i][3]
            roi=response_sheet_thresh[y:y+h,x:x+w]
            total=cv2.countNonZero(roi)
            if total>Gtotal:
                Set=i
                ansx=x
                ansy=y
                answ=w
                ansh=h
                Gtotal=total
                errorS=0
        if(errorS==1):
            print("Set not entered")
            print("Sending",filename,"to non-evaluated\n")
            # Return an empty array in case of an error
            return [], [], mainImage, None

        
        color=(51,255,51)
        omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)

        # determining category 
        # category = ''  # Initialize category as an empty string
        # x = row[7][0]
        # Gtotal = 35
        # errorS = 1
        # color = (0, 255, 255)

        # for i in range(0, 5):
        #     y = col[i][1]
        #     w = col[i][2]
        #     h = col[i][3]
        #     roi = response_sheet_thresh[y:y+h, x:x+w]
        #     total = cv2.countNonZero(roi)

        #     if total > Gtotal:
        #         cat = i  # Store the category index
        #         ansx = x
        #         ansy = y
        #         answ = w
        #         ansh = h
        #         Gtotal = total
        #         errorS = 0

        # if errorS == 1:
        #     print("Category not entered")
        #     print("Sending", filename, "to non-evaluated\n")
        #     # Return an empty array in case of an error
        #     return [], [], mainImage, None

        # # Map the 'cat' value to the corresponding category
        # if cat == 0:
        #     category = 'SC'
        # elif cat == 1:
        #     category = 'ST'
        # elif cat == 2:
        #     category = 'OBC-NCL'
        # elif cat == 3:
        #     category = 'GEN-EWS'
        # elif cat == 4:
        #     category = 'Unreserved'

        # # Mark the region with the appropriate color
        # color = (51, 255, 51)
        # omrUtlis.markTheRegion(ansx, ansy, answ, ansh, responseROI, color)

        # # Return the category and other details (you can adjust as needed)
        # # return category, cat, mainImage, responseROI

        # #determine gender
        # gender = ''  # Initialize gender as an empty string
        # gender_x = row[9][0]  # Assuming gender data is in `row[8][0]`
        # Gtotal_gender = 35
        # errorS_gender = 1

        # # Loop to determine gender (Male or Female)
        # for i in range(0, 2):  # Assuming only 2 categories: Male and Female
        #     y = col[i][1]
        #     w = col[i][2]
        #     h = col[i][3]
        #     roi = response_sheet_thresh[y:y+h, gender_x:gender_x+w]
        #     total = cv2.countNonZero(roi)

        #     if total > Gtotal_gender:
        #         gender_cat = i  # Store the gender category index
        #         ansx_gender = gender_x
        #         ansy_gender = y
        #         answ_gender = w
        #         ansh_gender = h
        #         Gtotal_gender = total
        #         errorS_gender = 0

        # if errorS_gender == 1:
        #     print("Gender not entered")
        #     print("Sending", filename, "to non-evaluated\n")
        #     # Return an empty array in case of an error
        #     return [], [], mainImage, None

        # # Map the 'gender_cat' value to the corresponding gender
        # if gender_cat == 0:
        #     gender = 'Female'
        # elif gender_cat == 1:
        #     gender = 'Male'

        # # Mark the region for gender
        # color_gender = (255, 51, 255)  # You can choose any color
        # omrUtlis.markTheRegion(ansx_gender, ansy_gender, answ_gender, ansh_gender, responseROI, color_gender)

        # Return the gender and other details
        # return gender, gender_cat, mainImage, responseROI


        # Determining Admit Card Number
        # appended=0
        for i in range (14,18):
            Gtotal=30
            errorA=1
            
            for j in range (0,10):
                x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
                if total>Gtotal:
                    Gtotal=total
                    errorA=0
                    ansx=x
                    ansy=y
                    answ=w
                    ansh=h
                    ch=chr(j+48)
            if(errorA==1 and i==14):
                schoolCode+=chr(0+48)
                # appended=1
                continue
            elif(errorA==1):
                print("Admit Card Number not Entered Correctly")
                # ch=chr(0+48)
                print("Sending",filename,"to non-evaluated\n")
                # Return an empty array in case of an error
                return [], [], mainImage, None


            color=(51,255,51)
            omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)
            schoolCode+=ch


        # Set = 0
        # schoolCode=0000
       
        # Determining Registration Number
        for i in range (0,13):
            Gtotal=35
            errorR=1
            color=(51,255,51)
            count=0
            errorM=0
            if i>=0 and i<=2:
                x=row[i][0]
                y=col[0][1]
                w=col[0][2]
                h=col[0][3]
                omrUtlis.markTheRegion(x,y,w,h,responseROI,color)
                continue
            
            if i>=7 or i==3:
                for j in range (0,10):
                    x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
                    # print(total)
                    if total>Gtotal:
                    #     if count==1:
                    #         errorM=1
                        count = 1
                        ansx=x
                        ansy=y
                        answ=w
                        ansh=h
                        Gtotal=total
                        errorR=0
                        ch=chr(j+48)
            #     # print(Gtotal)
            elif i==4:
                # for j in range (0,2):
                #     x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
                #     if total>Gtotal:
                #         # if count==1:
                #         #     errorM=1
                #         count=1
                #         ansx=x
                #         ansy=y
                #         answ=w
                #         ansh=h
                #         Gtotal=total
                #         errorR=0
                #         if(j==0):
                #             ch='S'
                #         else:
                #             ch='J'
                if(selected_certificate=='A'):
                    ch='J'
                else:
                    ch='S'
            elif i==5:
                for j in range (0,2):
                    x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
                    if total>Gtotal:
                        # if count==1:
                        #     errorM=1
                        count=1
                        ansx=x
                        ansy=y
                        answ=w
                        ansh=h
                        Gtotal=total
                        errorR=0
                        if(j==0):
                            ch='D'
                        else:
                            ch='W'
            else:
                for j in range (0,3):
                    x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
                    if total>Gtotal:
                        # if count==1:
                        #     errorM=1
                        count=1
                        ansx=x
                        ansy=y
                        answ=w
                        ansh=h
                        Gtotal=total
                        errorR=0
                        if(j==0):
                            ch='A'
                        elif j==1:
                            ch='F'
                        else:
                            ch='N'
                if(errorR==1):
                    print("Registration Number Incomplete")
                    print("Sending",filename,"to non-evaluated\n")
                    # Return an empty array in case of an error
                    return [], [], mainImage, None
                
                if(errorM==1):
                    print("Multiple Bubbles filled for 1 value in Registration Number")
                    print("Sending",filename,"to non-evaluated\n")
                    # Return an empty array in case of an error
                    return [], [], mainImage, None


            regNo+=ch
            omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)

        # cv2.imshow("rs",responseROI)
        # cv2.waitKey(0)
        # # mapping responses with the answer key
        # posScore=4
        # negScore=-1
        # unattemptScore=0
        # NoOfQues=175
        pos1=0
        pos2=0
        # threshold=30
        correctAns=0
        IncorrectAns=0
        Left=0
        ansx=0
        ansy=0
        answ=0
        ansh=0
        idx=0
        Crpaper1=0
        Inpaper1=0
        Crpaper2=0
        Inpaper2=0
        Crpaper3=0
        Inpaper3=0
        Crpaper4=0
        Inpaper4=0
        response_key=[]

        # print(NoOfQues)
        for idx2 in range(0,NoOfQues):
            count=0
            ans=-1
            flag=0
            check=0
            if(idx2%35==0 and idx2!=0):  # calculating the correct index 35
                pos1+=4
                pos2+=1
                
            for idx1 in range (0,4):
                # print(idx1+pos1)
                x=midRow[idx1+pos1][0]
                y=col[10+(idx2%35)][1]
                w=col[10+(idx2%35)][2]
                h=col[10+(idx2%35)][3]
                
                roi=response_sheet_thresh[y:y+h,x:x+w]
                total=cv2.countNonZero(roi)
                if total>threshold:
                    if count==0:
                        idx=idx2%35+pos2*35
                        ans=idx1
                        ansx=x
                        ansy=y
                        answ=w
                        ansh=h
                        count+=1
                    else:
                        flag=1
                        ansW = idx1
                        if ansW != -1 and element_exists(Answer_key[Set][idx], chr(ansW + 97), chr(ansW + 65)):
                            color = (43,169,255)  # Pink for correct option
                        else:
                            color=(57,41,237)  # Red for incorrect option

                        omrUtlis.markTheRegion(x, y, w, h, responseROI, color)
                        # color=(57,41,237)
                        # omrUtlis.markTheRegion(x,y,w,h,responseROI,color)
            # print(idx2,idx)
            if not(flag):
                if ans!=-1 and element_exists(Answer_key[Set][idx],chr(ans+97),chr(ans+65)):
                    response_key.append(chr(ans+65))
                    correctAns+=1
                    check=1
                    color=(0,255,0)
                    omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)
                elif ans!=-1:
                    response_key.append(chr(ans+65))
                    IncorrectAns+=1
                    color=(57,41,237)
                    omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)
                elif ans==-1:
                    Left+=1
                    response_key.append("-")
                    for ele in Answer_key[Set][idx2][1:]:
                        if isinstance(ele, str) and ele.isalpha() and ord(ele)>=ord('a') and ord(ele)<=ord('d'):
                            element=ord(ele) - ord('a')
                            x=midRow[pos1+element][0]
                            y=col[10+(idx2%35)][1]
                            w=col[10+(idx2%35)][2]
                            h=col[10+(idx2%35)][3]
                            # print(x,y,w,h)
                            color=(255,165,0)
                            omrUtlis.markTheRegion(x,y,w,h,responseROI,color)
                        elif isinstance(ele, str) and ele.isalpha() and ord(ele)>=ord('A') and ord(ele)<=ord('D'):
                            element=ord(ele) - ord('A')
                            x=midRow[pos1+element][0]
                            y=col[10+(idx2%35)][1]
                            w=col[10+(idx2%35)][2]
                            h=col[10+(idx2%35)][3]
                            # print(x,y,w,h)
                            color=(255,165,0)
                            omrUtlis.markTheRegion(x,y,w,h,responseROI,color)
            else:
                response_key.append("M")
                IncorrectAns+=1
                if ans != -1 and element_exists(Answer_key[Set][idx], chr(ans + 97), chr(ans + 65)):
                    color = (43,169,255)  # Pink for correct option
                else:
                    color=(57,41,237)  # Red for incorrect option
                # color=(57,41,237)
                omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)
            
            if(selected_certificate=='A'):
                if(idx2>=0 and idx2<=13):
                    if(check):
                        Crpaper2+=1
                    else:
                        Inpaper2+=1
                elif(idx2>=14 and idx2<=95):
                    if(check):
                        Crpaper3+=1
                    else:
                        Inpaper3+=1
                else:
                    if(check):
                        Crpaper4+=1
                    else:
                        Inpaper4+=1
            elif(selected_certificate=='B'):
                if(idx2>=0 and idx2<=14):
                    if(check):
                        Crpaper2+=1
                    else:
                        Inpaper2+=1
                elif(idx2>=15 and idx2<=119):
                    if(check):
                        Crpaper3+=1
                    else:
                        Inpaper3+=1
                else:
                    if(check):
                        Crpaper4+=1
                    else:
                        Inpaper4+=1
            else:
                if(idx2>=0 and idx2<=4):
                    if(check):
                        Crpaper2+=1
                    else:
                        Inpaper2+=1
                elif(idx2>=5 and idx2<=119):
                    if(check):
                        Crpaper3+=1
                    else:
                        Inpaper3+=1
                else:
                    if(check):
                        Crpaper4+=1
                    else:
                        Inpaper4+=1
        # cv2.imshow("img",responseROI)
        # cv2.waitKey(0)
        result="Pass"
        paper1=Crpaper1*posScore+Inpaper1*negScore

        paper2=Crpaper2*posScore+Inpaper2*negScore

        paper3=Crpaper3*posScore+Inpaper3*negScore

        paper4=Crpaper4*posScore+Inpaper4*negScore

        score=correctAns*posScore+IncorrectAns*negScore+Left*unattemptScore

        # papers=[paper1,paper2,paper3,paper4]
        # print(score)
        if ((selected_certificate == 'A' and (paper2 < 11.55 or paper3 < 67.65 or paper4 < 36.3 or score < 115.5)) or
            (selected_certificate == 'B' and (paper2 < 9.9 or paper3 < 69.3 or paper4 < 36.3 or score < 115.5)) or
            (selected_certificate == 'C' and (paper2 < 3.3 or paper3 < 75.9 or paper4 < 36.3 or score < 115.5))):
            result = "Fail"
        elif score >= 245:
            result = "A"
        elif 192.5 <= score < 245:
            result = "B"
        elif 115.5 <= score < 192.5:
            result = "C"
        else:
            result = "Fail"


        # print(score,NoOfQues,result)
        Set=chr(Set+65)
        def flatten_list(lst):
            flattened = []
            for item in lst:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            return flattened
        flattened_data = flatten_list([Sno,regNo,schoolCode,Set,response_key,score,result])
        # flattened_data = flatten_list([Sno,regNo,Set,gender,category,response_key,score,result])
        print(filename,Sno,regNo,Set,schoolCode,correctAns,IncorrectAns,Left,paper1,paper2,paper3,paper4,score,result,"\n")
        # "S.No","Enrollment No", "Set", "AdmitCard No", "CorrectAns", "IncorrectAns", "Left","paper1","paper2","paper3","paper4", "Score","Grade"
        return [Sno,regNo,Set,schoolCode,correctAns,IncorrectAns,Left,paper1,paper2,paper3,paper4,score,result],flattened_data,mainImage,responseROI
        # return [Sno,regNo,Set,gender,category,correctAns,IncorrectAns,Left,score,result],flattened_data,mainImage,responseROI

    except Exception as e:
        # cv2.imshow("img",responseROI)
        # cv2.waitKey(0)
        print(f"An error occurred: {str(e)}")
        print("Sending",filename,"to non-evaluated\n")
        # Return an empty array in case of an error
        return [], [], None, None