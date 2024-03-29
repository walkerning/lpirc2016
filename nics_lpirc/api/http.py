# -*- coding: utf-8 -*-

import os, time
import numpy as np
import cv2

from nics_lpirc.api import client
from nics_lpirc.api import APIAdapter, SubprocessAPIAdapter

class HttpAPI(SubprocessAPIAdapter):
    def __init__(self, cfg):
        super(HttpAPI, self).__init__(cfg)

        self.cfg = cfg.httpapi
        client.set_cfgs(self.cfg)
        if self.cfg.add_suffix:
            username = self.cfg.username + '-' + time.strftime("%m-%d-%H%M%S",time.localtime(time.time()))
        else:
            username = self.cfg.username
        password = username

        [self.token, self.status] = client.get_token(username, password)
        [self.total_num, status] = client.get_no_of_images(self.token)
        self.get_idx = 0
        self.post_idx = 0
        # print "Total num:", self.total_num
        self.total_num = int(self.total_num)
        self.image_id_last = '0.jpg'

    def get_image(self):
        if self.done():
            return None
        status = 0
        try:
            status = client.get_image(self.token, self.get_idx + 1)
            res = os.path.join(self.cfg.image_directory,'%d.jpg'%(self.get_idx + 1))
            im = cv2.imread(res)
            # res = '../images/%d.jpg'%(self.get_idx + 1)
        except Exception as e:
            print "Exception:", e
            res = ''
        self.get_idx += 1
        # print "Image download. Current idx:", self.get_idx
        return str(self.get_idx)+'.jpg', im
    
    def get_images(self):
        if self.done():
            return None
        status = 0
        try:
            status = client.get_image(self.token, self.get_idx + 1)
            res = os.path.join(self.cfg.image_directory,'%d.zip'%(self.get_idx + 1))
            # res = '../images/%d.zip'%(self.get_idx + 1)
        except Exception as e:
            print "Exception:", e
            res = ''
        self.get_idx += 100
        # print "Image batch download. Current idx:", self.get_idx
        return (self.get_idx, res)

    def _commit_result(self,image_id, class_ids, dets):
        # print dets
        confidences = [x[4] for x in dets]
        bboxs = [x[0:4] for x in dets]
        if len(class_ids) != len(confidences) and len(class_ids) != len(bboxs):
            print "Index does not match!"
            return 0

        num_bboxs = len(class_ids)
        if num_bboxs == 0:
            return 1

        data_to_post = {'image_name':[str(image_id)] * num_bboxs,
        'confidence': map(lambda x:str(x), confidences),
        'CLASS_ID': map(lambda x: str(x), class_ids),
        'xmin': map(lambda x: str(x[0]), bboxs),
        'ymin': map(lambda x: str(x[1]), bboxs),
        'xmax': map(lambda x: str(x[2]), bboxs),
        'ymax': map(lambda x: str(x[3]), bboxs)}

        status = 0
        try:
            status = client.post_result(self.token, data_to_post)
        except Exception as e:
            print "Exception:", e
        self.post_idx += 1
        print 'image_id: ', image_id
        if self.cfg.del_img and self.image_id_last != image_id:
            # delete the last image
            for img_idx in range(int(self.image_id_last.split('.')[0]), int(image_id.split('.')[0])):
                
                try:
                    os.remove(os.path.join(self.cfg.image_directory, '%d.jpg'%(img_idx)))
                except:
                    pass
        self.image_id_last = image_id
            
        # print "Result uploaded. Current idx:", image_id
        return 1

    def done(self):
        if self.status != 1:
            return 1
        return self.total_num == self.get_idx

    def catch(self):
        if self.status != 1:
            return 1
        return self.post_idx == self.get_idx


class Clever_HttpAPI(APIAdapter):
    def __init__(self, cfg):
        self.cfg = cfg.httpapi
        client.set_cfgs(self.cfg)
        [self.token, self.status] = client.get_token(self.cfg.username, self.cfg.password)
        [self.total_num, status] = client.get_no_of_images(self.token)
        self.get_idx = 0
        self.post_idx = 0
        self.down_idx = 0
        # print "Total num:", self.total_num
        self.total_num = int(self.total_num)



    def get_image_single(self):
        if self.down_done():
            return None
        status = 0
        try:
            status = client.get_image(self.token, self.down_idx + 1)
            # res = os.path.join(self.cfg.image_directory,'%d.jpg'%(self.get_idx + 1))
            # im = cv2.imread(res)
            # res = '../images/%d.jpg'%(self.get_idx + 1)
        except Exception as e:
            print "Exception:", e
            # res = ''
        self.down_idx += 1
        print "Image download. Current idx:", self.down_idx
        # return str(self.get_idx)+'.jpg', im
    
    def get_images(self):
        #TODO: what if no_of_images is not multiple of 100
        if self.down_done():
            return None
        status = 0
        try:
            print 'down_idx=',str(self.down_idx)
            status = client.get_images(self.token, self.down_idx + 1)
             
            res = os.path.join(self.cfg.image_directory,'%d.zip'%(self.down_idx + 1))
            os.system('unzip -o -d ' + self.cfg.image_directory + ' ' + res)
            # res = '../images/%d.zip'%(self.down_idx + 1)
        except Exception as e:
            print "Exception:", e
            res = ''
        self.down_idx += 100
        if self.down_idx > self.total_num:
            self.down_idx = self.total_num
        print "Image batch download. Current idx:", self.down_idx
        # return (self.get_idx, res)


    def get_image(self):
        if self.done():
            return None

        if self.down_idx < 100:
            self.get_image_single()
        else:
            self.get_images()

        res = os.path.join(self.cfg.image_directory,'%d.jpg'%(self.get_idx + 1))
        im = cv2.imread(res)
        self.get_idx += 1
        return str(self.get_idx) + '.jpg', im


    def commit_result(self,image_id, class_ids, dets):
        # print dets
        confidences = [x[5] for x in dets]
        bboxs = [x[0:4] for x in dets]
        if len(class_ids) != len(confidences) and len(class_ids) != len(bboxs):
            print "Index does not match!"
            return 0

        num_bboxs = len(class_ids)
        if num_bboxs == 0:
            return 1

        data_to_post = {'image_name':[str(image_id)] * num_bboxs,
        'confidence': map(lambda x:str(x), confidences),
        'CLASS_ID': map(lambda x: str(x), class_ids),
        'xmin': map(lambda x: str(x[0]), bboxs),
        'ymin': map(lambda x: str(x[1]), bboxs),
        'xmax': map(lambda x: str(x[2]), bboxs),
        'ymax': map(lambda x: str(x[3]), bboxs)}

        status = 0
        try:
            status = client.post_result(self.token, data_to_post)
        except Exception as e:
            print "Exception:", e
        self.post_idx += 1
        print "Result uploaded. Current idx:", image_id
        return 1

    def down_done(self):
        if self.status != 1:
            return 1
        return self.total_num == self.down_idx

    def done(self):
        if self.status != 1:
            return 1
        return self.total_num == self.get_idx

    def catch(self):
        if self.status != 1:
            return 1
        return self.post_idx == self.read_idx
