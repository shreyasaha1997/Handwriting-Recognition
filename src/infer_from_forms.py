from __future__ import division
from __future__ import print_function

import cv2
import numpy as np

import os
import sys
import argparse
import cv2
import editdistance
from DataLoader import DataLoader, Batch
from Model import Model
from SamplePreprocessor import preprocess


class FilePaths:
	"filenames and paths to data"
	fnCharList = '../model/charList.txt'
	fnAccuracy = '../model/accuracy.txt'
	fnTrain = '../data/'
	fnInfer = '../data/test.png'
	fnCorpus = '../data/corpus.txt'
	
image = cv2.imread('../Input/form.jpg')

def infer(model, fnImg):
	"recognize text in image provided by file path"
	img = preprocess(fnImg, Model.imgSize)
	batch = Batch(None, [img] * Model.batchSize)
	recognized = model.inferBatch(batch)
	return recognized[0]
    
def line_sep(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    image_print = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)

    kernel = np.ones((1,50), np.uint8)
    img_dilation = cv2.dilate(thresh, kernel, iterations=1)
    im2,ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    images = []

    sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
    i = 0
    for ctr in sorted_ctrs:
        if cv2.contourArea(ctr) < 1500:
            continue
        x, y, w, h = cv2.boundingRect(ctr)
        if h<40:
            continue
        roi = image[y:y+h, x:x+w]
        cv2.rectangle(image_print,(x,y),( x + w, y + h ),(90,0,255),2)
        cv2.putText(image_print, str(i), (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (8,8,236), 2)
        indices.append(str(i))
        i = i+1
        images.append(roi)
    cv2.imwrite('../Output/forms/all_lines.png',image_print)
    return images

def word_seperation(image,index):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx = 4, fy = 4, interpolation = cv2.INTER_LINEAR)
    image_print = cv2.resize(image, None, fx = 4, fy = 4, interpolation = cv2.INTER_LINEAR)
    image = cv2.resize(image, None, fx = 4, fy = 4, interpolation = cv2.INTER_LINEAR)
    
    ret, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((10,10), np.uint8)
    img_dilation = cv2.dilate(thresh, kernel, iterations=1)
    im2, ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    images = []

    sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
    
    i = 1
    for ctr in sorted_ctrs:
        if cv2.contourArea(ctr) < 1500:
            continue
        x, y, w, h = cv2.boundingRect(ctr)
        roi = gray[y:y + h, x:x + w]
        cv2.rectangle(image_print,(x,y),( x + w, y + h ),(90,0,255),2)
        
        print("Word detection gonna start")
        inferred = infer(model, roi)
        cv2.putText(image_print, inferred, (x + 10, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (8,8,236), 2)
        i = i+1
        images.append(roi)
    cv2.imwrite('../Output/forms/' + index + '.png', image_print)
    
indices = []
os.system('rm -rf ../Output/forms/*')
image = cv2.imread('../Input/form.jpg')
images = line_sep(image)
print("line seperation done")
model = Model(open(FilePaths.fnCharList).read(), mustRestore=True)
for i in images:
    words = word_seperation(i,indices[images.index(i)])
