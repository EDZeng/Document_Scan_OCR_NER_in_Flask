import os
import settings
import cv2
import numpy as np
from imutils.perspective import four_point_transform


def save_upload_image(fileObj):
    filename = fileObj.filename
    
    name, ext = filename.split('.')
    
    save_filename = 'upload.' + ext
    upload_image_path = settings.join_path(settings.SAVE_DIR, save_filename)
    
    fileObj.save(upload_image_path)
    
    return upload_image_path

# 座標用json的格式呈現

def array_to_json_format(numpy_array):
    points=[]
    for pt in numpy_array.tolist():
        points.append({'x':pt[0], 'y':pt[1]})
        
    return points

class DocumentScan():
    def __init__(self):
        pass
    
    @staticmethod
    def resizer(image, width=500) :
        h, w, c = image.shape
        
        height = int((h/w) * width)
        size = (width, height)
        image = cv2.resize(image, (width, height))
        return image, size

    @staticmethod
    def apply_brightness_contrast(input_img, brightness = 0, contrast = 0):
    
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow)/255
            gamma_b = shadow
            
            buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
        else:
            buf = input_img.copy()
        
        if contrast != 0:
            f = 131*(contrast + 127)/(127*(131-contrast))
            alpha_c = f
            gamma_c = 127*(1-f)
            
            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

        return buf

    
    def document_scanner(self, image_path) :
        self.image = cv2.imread(image_path)
        
        img_re, self.size = self.resizer(self.image)
        filename = 'resize_image.jpg'
        RESIZE_IMAGE_PATH = settings.join_path(settings.MEDIA_DIR, filename)
        
        cv2.imwrite(RESIZE_IMAGE_PATH, img_re)
        
        try :
            detail = cv2.detailEnhance(img_re, sigma_s=20, sigma_r= 0.15)

            gray = cv2.cvtColor(detail, cv2.COLOR_BGR2GRAY)    # 轉為灰階
            
            blur = cv2.GaussianBlur(gray, (5, 5), 0)   # 減少圖像中的噪點、平滑細節或降低圖像的高頻細節信息
            
            # 邊緣檢測
            edge_image = cv2.Canny(blur, 75, 200)
            
            # morphological transform
            kernel = np.ones((5, 5), np.uint8)   # 建立 5X5 的核心
            dilate = cv2.dilate(edge_image, kernel, iterations=1)   # 膨脹 , 用意是擴大或加強圖像中的白色區域（也稱為前景），並將它們連接在一起
            closing = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)    # 用於去除二值圖像中的小孔洞，並連接物體的細小間隙
            
            # 檢測輪廓
            contours, hire = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            for contour in contours:
                peri = cv2.arcLength(contour, True)   # 第一個參數是輪廓，第二個參數是布爾值（True 或 False），用於指定輪廓是否封閉。計算周長是為了後續的多邊形近似
                approx = cv2.approxPolyDP(contour, 0.02*peri, True)    # 將輪廓近似為具有較少頂點的多邊形，以簡化輪廓的表示
            
                if len(approx) == 4 :                  # 如果滿足四邊形的輪廓
                    four_points = np.squeeze(approx)
                    break
            return four_points, self.size
        
        except :
            return None, self.size
        

    def calibrate_to_original_size(self, four_points):
        multiplier = self.image.shape[1] / self.size[0]
        four_points_orig = four_points * multiplier
        four_points_orig = four_points_orig.astype(int)

        wrap_img = four_point_transform(self.image, four_points_orig)

        # apply magic color to wrap image
        magic_color = self.apply_brightness_contrast(wrap_img, brightness=40, contrast=40)
        
        return magic_color
        
        
        
        