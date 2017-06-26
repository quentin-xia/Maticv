#!/ust/bin/env python
#-*- coding:utf-8 -*-

import numpy as np
import platform
if platform.system() is "Windows":
    try:
        import maticv.common.opencv.x32.cv2 as cv2
    except:
        import maticv.common.opencv.x64.cv2 as cv2
else:
    import maticv.common.opencv.linux.cv2 as cv2

class Match(object):
    def __init__(self):
        self.MIN_MATCH_COUNT = 10
        self.FLANN_INDEX_KDTREE = 0


    #img1   模版
    #img2   图像
    #similar    相似度
    #num    匹配数量
    def find_all(self,img1,img2,similar=0.7,num=1):
        res = []
        if not img1.any() or not img2.any():
            return res

        similar = float(similar)
        num = int(num)
        if len(img1) == 0 or len(img2) == 0 or num < 1:
            return res
        elif similar > 0.99: similar = 0.99
        elif similar < 0.0: similar = 0.0

        #返回特征描述(较慢)
        #sift = cv2.SIFT()
        #kp1,des1 = sift.detectAndCompute(img1,None)
        #kp2,des2 = sift.detectAndCompute(img2,None)

        #返回特征描述(较快)
        #hessian
        hess = 3000
        surf = cv2.SURF(hess)
        kp1,des1 = surf.detectAndCompute(img1,None)
        kp2,des2 = surf.detectAndCompute(img2,None)
        
        #匹配（较慢）
        #index_params = dict(algorithm = self.FLANN_INDEX_KDTREE,tree = 5)
        #search_params = {}
        #flann = cv2.FlannBasedMatcher(index_params,search_params)
        #matches = flann.knnMatch(des1,des2,k=num+1)


        #匹配（较快）
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1,des2,k=num+1)

        good = []
        for i in range(num):
            max_dist = 0
            for dist in matches:
                if dist[i].distance > max_dist:
                    max_dist = dist[i].distance

            good.append([])
            for x in range(len(matches)):
                if len(matches[x]) >= num+1:
                    if matches[x][i].distance < (1-similar) * max_dist:
                        good[i].append(matches[x][i])

        for i in range(num):
            if len(good[i]) > self.MIN_MATCH_COUNT:
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good[i]]).reshape(-1,1,2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good[i]]).reshape(-1,1,2)
                M,mask = cv2.findHomography(src_pts,dst_pts,cv2.RANSAC,0.1)

                h,w = img1.shape
                pts = np.float32([[0,0],[0,h],[w,h],[w,0]]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)

                x1,y1 = int(round(dst[0][0][0])),int(round(dst[0][0][1]))
                x2,y2 = int(round(dst[1][0][0])),int(round(dst[1][0][1]))
                x3,y3 = int(round(dst[2][0][0])),int(round(dst[2][0][1]))
                x4,y4 = int(round(dst[3][0][0])),int(round(dst[3][0][1]))
                if x1 == x2 and x3 == x4 and y1 == y4 and y2 == y3:
                    if x4 - x1 == w and x3 - x2 == w and y2 - y1 == h and y3 - y4 == h:
                        res.append([x1,y1,x3,y3])
                    else:
                        res.append([x1,y1])
                else:
                    res.append([x1,y1])
        return res


    def find(self,img1,img2,similar=0.7):
        res = self.find_all(img1,img2,similar)
        if res:
            if len(res[0]) == 4:
                return res[0]
            else:
                return []
        else:
            return []

