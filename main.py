import sys  #
import face_recognition  
import os  
from xlutils.copy import copy   
import xlrd    
from os import listdir,getcwd  
import cv2  
import threading 
from PyQt5.QtWidgets import QApplication ,QMainWindow,QMessageBox,QFileDialog,QLabel
from PyQt5.QtCore import QBasicTimer,pyqtSignal,Qt,QSize,QThread
from PyQt5.QtGui import *
from datetime import datetime  
from time import time  
from speech_synthesis_ui import Ui_MainWindow2 
from speech_reco_ui import Ui_MainWindow3
from register import Ui_Dialog2
from setting2_ui import Ui_Dialog 
from new_ui import Ui_MainWindow  
from baiduyuyin import baidu_voice,baidu_speech_reco ,ping  
from PIL import Image, ImageDraw, ImageFont 
import numpy as np
import qtawesome
import pyaudio
import wave
from configparser import ConfigParser

conf=ConfigParser()  #
conf.read('config.conf', encoding='gbk')
CAPTURE_SOURCE=conf.get('image_config','capture_source')
TOLERANCE=float(conf.get('image_config','tolerance'))
SET_SIZE=float(conf.get('image_config','set_size'))
print(CAPTURE_SOURCE,TOLERANCE,SET_SIZE)
t=time()
class MyMainWindow(QMainWindow,Ui_MainWindow):
    signal=pyqtSignal() 
    signal2=pyqtSignal()
    signal3=pyqtSignal() 
    signal4=pyqtSignal()
    def __init__(self,parent=None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)

        # self.timer_camera = QTimer()  # 需要定时器刷新摄像头界面
        self.cap = cv2.VideoCapture()
        self.video_btn=0    # 用去区分打开摄像头和人脸识别 当打开人脸识别按钮的时候 video_btn 就会变成1  这样的话 关闭人脸识别 摄像头还是处于打开的状态
        self.need_record_name1=([])

# 信号槽设置  ------------------------------

        self.left_close.clicked.connect(self.close_window)  
        self.left_mini.clicked.connect(self.showMinimized)
        #self.left_visit.clicked.connect(self.showMaximized)  
        self.pushButton_8.clicked.connect(self.btn_open_cam_click) 
        self.pushButton_4.clicked.connect(self.face_recognition_btn) 
        self.pushButton_5.clicked.connect(self.photo_face)  
        self.pushButton_3.clicked.connect(self.signal_emit) 
        self.left_button_6.clicked.connect(self.signal_speech_reco)  
        self.pushButton.clicked.connect(self.signal_register) 
        self.pushButton_2.clicked.connect(self.open_record)  
        self.pushButton_9.clicked.connect(self.video_announce)  
        self.left_button_9.clicked.connect(self.signal_setting)  
        print('mainwindow  is running')
        self.progressbarr_move()  
        self.show()
# 信号槽对应的函数






    def close_window(self):
        flag2=self.cap.isOpened()
        if flag2==True:
            QMessageBox.information(self,'warning','请先关闭摄像头再退出')
        else:
            self.close()
    def btn_open_cam_click(self):  #打开摄像头 按钮函数
        global CAPTURE_SOURCE
        if CAPTURE_SOURCE=='0':
            CAPTURE_SOURCE=int(CAPTURE_SOURCE)


        self.source = CAPTURE_SOURCE
        self.t3=time()
        flag2=self.cap.isOpened() 
        #print(flag2,' flag')
        if flag2 == False:
             
            self.cap.open(self.source)

            try:
                 self.show_camera()
            except:
                QMessageBox.about(self,'warning','摄像头不能正常被打开')
        else:
            print('关闭摄像头')

            # self.timer_camera.stop()
            self.cap.release()  
            #
            self.pushButton_8.setText(u'打开摄像头')
            #self.label_5 = QLabel('\n\nImage and Speech\n\nProcessing')
            self.label_5.setPixmap(QPixmap(""))
            #
            self.label_5.setText('Image and Speech\n\nProcessing')
            #
        #self.qingping()
    def face_recognition_btn(self):  #
        flag2=self.cap.isOpened()
        if flag2== False:
            QMessageBox.information(self, "Warning",
                                self.tr("请先打开摄像头!"))
        else:
            self.t2=time()
            self.time_step=0
            if self.video_btn==0:
                self.video_btn=1
                self.pushButton_4.setText(u'关闭人脸识别')
                self.show_camera()
                #由于
            elif self.video_btn==1:
                self.video_btn=0
                self.time_step=0 
                self.pushButton_4.setText(u'人脸识别')
                self.qingping()
                self.show_camera()
                self.qingping()
    def progressbarr_move(self): 
        self.timer = QBasicTimer()
        self.step = 0
        self.timer.start(100, self)
    def timerEvent(self, e):  #
                              
        if self.step >= 100:
          #time.sleep(3) 尝试休眠 但起不到效果
            self.progressBar.setValue(0)
            self.step=0
            self.time_step=1
            return
        if self.video_btn==1 and self.time_step==0:
            self.step = self.step+18
        elif self.video_btn==0:
            self.step=0
        else :
            self.step=self.step
        self.progressBar.setValue(self.step)

    def show_camera(self):  
        #print('show_camera is open ')
        if self.video_btn==0:   

            self.pushButton_8.setText(u'关闭摄像头')

            while (self.cap.isOpened()):

                ret, self.image = self.cap.read()
                QApplication.processEvents()  
                show = cv2.resize(self.image, (800, 494))
                show = cv2.cvtColor(show,cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
                # opencv 读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage QImage(uchar * data, int width,
                self.showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                self.label_5.setPixmap(QPixmap.fromImage(self.showImage))

              #  因为他最后会存留一张 图像在lable上需要对 lable_5进行清理
            self.label_5.setPixmap(QPixmap(""))
            print('打开摄像头时间',time()-self.t3

        elif self.video_btn==1:
            #这段代码是 获取photo文件夹中 人的信息
             filepath='photo'
             filename_list=listdir(filepath)
             known_face_names=[]
             known_face_encodings=[]
             a=0
             print('2')
             for filename in filename_list:
                a+=1
                QApplication.processEvents()
                if filename.endswith('jpg'):
                    known_face_names.append(filename[:-4])#把文件名字的后四位.jpg去掉获取人名
                    file_str='photo'+'/'+filename
                    a_images=face_recognition.load_image_file(file_str)
                    print(file_str)
                    a_face_encoding = face_recognition.face_encodings(a_images)[0]
                    known_face_encodings.append(a_face_encoding)
             print(known_face_names,a)
           
             face_locations = []
             face_encodings = []
             face_names =[]
             process_this_frame = True
             while (self.cap.isOpened()):
                 ret, frame = self.cap.read()
                 QApplication.processEvents()
                    # 改变摄像头图像的大小，图像小，所做的计算就少
                 small_frame = cv2.resize(frame, (0, 0), fx=SET_SIZE, fy=SET_SIZE)

                    # opencv的图像是BGR格式的，而我们需要是的RGB格式的，因此需要进行一个转换。
                 rgb_small_frame = small_frame[:, :, ::-1]
                 #print('4 is running')
                 if process_this_frame:
                     QApplication.processEvents()
                        
                     face_locations = face_recognition.face_locations(rgb_small_frame)
                     face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                     face_names = []
                    # print('5 is  running')
                     for face_encoding in face_encodings:
                            # 默认为unknown
                         matches = face_recognition.compare_faces(known_face_encodings, face_encoding,tolerance=TOLERANCE)
                            #阈值太低容易造成无法成功识别人脸，太高容易造成人脸识别混淆 默认阈值tolerance为0.6
                           
                         name = "Unknown"
                         if True in matches:
                             first_match_index = matches.index(True)
                             name = known_face_names[first_match_index]

                         face_names.append(name)
                 process_this_frame = not process_this_frame
                    
                 self.set_name=set(face_names)
                 self.set_names=tuple(self.set_name) # 把名字先设为了一个 集合 把重复的去掉 再设为tuple 以便于下面显示其他信息和记录 调用
                 voice_syn=str()
                 print(self.set_names) 
                 self.write_record() 
                
                 for (top, right, bottom, left), name in zip(face_locations, face_names):
                        
                     top *= int(1/SET_SIZE)
                     right *=int(1/SET_SIZE)
                     bottom *= int(1/SET_SIZE)
                     left *= int(1/SET_SIZE)
                        # 矩形框
                     cv2.rectangle(frame, (left, top), (right, bottom), (60, 20, 220), 3)

                     print('face recognition is running')
                       
                     cv2img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
                     pilimg = Image.fromarray(cv2img)
                     draw = ImageDraw.Draw(pilimg) # 图片上打印
                     font = ImageFont.truetype("msyh.ttf", 27, encoding="utf-8") 
                     draw.text((left+10 , bottom ), name, (220, 20, 60), font=font) 

                    # PIL图片转cv2 图片
                     frame = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)

                 self.show_picture() # 调用显示详细信息的函数

                 show_video = cv2.resize(frame, (800, 494))
                 show_video = cv2.cvtColor(show_video,cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
                # opencv 读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage QImage(uchar * data, int width,
                 self.showImage = QImage(show_video.data, show_video.shape[1], show_video.shape[0], QImage.Format_RGB888)
                 self.label_5.setPixmap(QPixmap.fromImage(self.showImage))
             print('打开人脸识别所需要的时间',time()-self.t2)


    def photo_face(self):  
        photo_save_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                                       'video_screenshot/')
        # self.time_flag.append(datetime.now().strftime("%Y%m%d%H%M%S")
        self.showImage.save(photo_save_path + datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg")


        QMessageBox.information(self, "Information",
                                self.tr("拍照成功!"))

    def show_picture(self):  
         if self.video_btn==1:
             conf = ConfigParser()
             conf.read('information.conf', encoding='gbk')
             inforation={}
             for names in conf.sections():
                more_infor={}
                for detils in conf.items(names):
                    more_infor[detils[0]]=detils[1]

                inforation[names]=more_infor
             #fr = open("information.txt",'rb')  #读取information.txt中的信息  里面是录入信息时写入的
             infor_dic = inforation   
             #fr.close()
             photo_message={0:[self.label_2,self.label_7],1:[self.label,self.label_6],2:[self.label_3,self.label_4]}
            
             if len(self.set_names)>3:
                 show_person=3
             else:
                 show_person=len(self.set_names)
             if show_person!=0:
                 for person in range(show_person):
                     try:
                         person_name=self.set_names[person]   #识别出人物的名字
                         person_infor=photo_message[person][0] #信息所对应的lable
                         person_photo=photo_message[person][1] #照片所对对应的lable
                         infor_names=infor_dic[person_name] 
                         name_str='photo//'+person_name+'.jpg'
                         picture=QPixmap(name_str)

                         infor_str='姓名：'+person_name+'                '+'年龄：'+infor_names['年龄']+'                 '+'性别：'+infor_names['性别']+'                 '+'更多信息： '+infor_names['更多信息']

                         person_infor.setText(infor_str)
                         person_infor.setStyleSheet("color:white;font-size:20px;font-family:Microsoft YaHei;")
                         person_infor.setWordWrap(True) 
                         person_photo.setPixmap(picture)  
                         person_photo.setScaledContents(True)  
                     except :
                         QMessageBox.about(self,'warning','请检查'+person_name+'的信息')


             if show_person!=3:
                 for empty in range(3)[show_person:]:
                     person_infor=photo_message[empty][0]
                     person_photo=photo_message[empty][1] 
                     person_infor.setText("")
                     person_photo.setPixmap(QPixmap(""))

    def qingping(self):  
          self.label_7.setPixmap(QPixmap(""))  # 照片1
          self.label_2.setText("")  # 信息1
          self.label.setPixmap(QPixmap(""))
          self.label_6.setText("")
          self.label_3.setPixmap(QPixmap(""))
          self.label_4.setText("")


    def signal_emit(self):
        self.signal.emit()#  信号发出
        
    def signal_speech_reco(self):
        self.signal2.emit()
    def signal_setting(self):  #发出信号 打开新的界面
        self.signal3.emit()
    def signal_register(self):
        self.signal4.emit()
    def open_file(self): #下面这个路径是绝对路径 无法更改
        file_rute=getcwd()+'\\'+'photo'
        file_name = QFileDialog.getOpenFileName(self,"录入信息",file_rute)#  打开这个文件夹 选择打开的文件 phot里面的照片是打不开的 因为.py文件在外面
        print(file_name)   
        try:
            file_name2=list(file_name)[0] # 想要的是information，text 所以需要需要对file_name进行处理 需要注意的是打开的是 photo文件夹是向里面传照片的再返回出来 填写information
            t_file=0
            for i in file_name2:
                if i=='/':
                    num=t_file
                t_file=t_file+1
            open_file3=file_name2[(num+1):]
            os.popen(open_file3)
        except:
            QMessageBox.about(self,'warning','无法打开文件')

    def write_record(self):
        #self.need_record_name=set(self.need_record_name)
        print('need_record_names1 is',self.need_record_name1)

        if self.set_name.issubset(self.need_record_name1):  # 如果self.set_names是self.need_record_names 的子集返回ture
            pass                                             # need_record_name1是要写进excel中的名字信息 set_name是从摄像头中读出人脸的tuple形式
        else :
            print('ready to write')
            self.different_name1=self.set_name.difference(self.need_record_name1) # 获取到self.set_name有 而self.need_record_name 无的名字
            self.need_record_name1=self.set_name.union(self.need_record_name1)  # 把self.need_record_name  变成两个集合的并集
                                       

            filename='data.xls'            
            book = xlrd.open_workbook(filename)  # 打开excel
            new_book = copy(book)  # 复制excel
            sheet2 = new_book.get_sheet(0)  # 获取第一个表格的数据
            sheet0 = book.sheet_by_index(0)
            nrows = sheet0.nrows    # 获取行总数
            print("行数",nrows)
            ncols = sheet0.ncols    #获取列总数
            print("列数",ncols)
            write_in_data=tuple(self.different_name1)  
            names_length=len(write_in_data)      
            for i in range(names_length):
                #baidu_voice(write_in_data[i])  对进入的人脸进行播报
                str_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet2.write(nrows+i,0,str_time)
                sheet2.write(nrows+i,2,write_in_data[i])
                sheet2.write(nrows+i,1,'摄像头')
                sheet2.write(nrows+i,3,'使用摄像头进行测试')

            new_book.save('secondsheet.xls')  # 保存新的excel
            os.remove(filename)  # 删除旧的excel
            os.rename('secondsheet.xls', filename)  # 将新excel重命名

    def video_announce(self): 
        try:
            need_voice_name=list(self.need_record_name1)
        except:
            need_voice_name=[]
        if need_voice_name!=[]:
            print(need_voice_name)
            if 'Unknown' in need_voice_name :# 把unknown去掉 不进行播报
                need_voice_name.remove('Unknown')
            tuple_voice_name=tuple(need_voice_name)
            if tuple_voice_name==():
                QMessageBox.about(self,'warning','还未识别出人脸')
            else:
                voice_str='欢迎'
                for i in tuple_voice_name:
                    voice_str=voice_str+i+' '
                voice_str=voice_str+'的到来'
                baidu_voice(voice_str)  # 欢迎 某 某某 的到来

        else :
            QMessageBox.about(self,'warning',"没有看到人无法进行播报")


    def open_record(self):
        os.popen('data.xls')# 使用popen会新开一个进程  而使用os.system会占用原来的进程


class MineWindow(QMainWindow,Ui_MainWindow2): 
    def __init__(self,parent=None):
        #super(MineWindow, self).__init__(None, Qt.FramelessWindowHint)  # 这句和普通的不一样 因为可以实现无边框
        super(MineWindow,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.baidu_voice2)  
        self.pushButton_2.clicked.connect(self.close_voice) #退出按钮 执行退出窗口
        self.pushbutton_close.clicked.connect(self.close)  #关闭窗口
        self.pushbutton_mini.clicked.connect(self.showMinimized)#最小化窗口

    def baidu_voice2(self):
        check_net=ping()
        if check_net==True:
            print ('ping ok')
    #def baidu_voice2(self):
            self.text_Edit = self.textEdit.text()  #获取 输入到 textEdit上的字体  并传递给语音合成函数
            print(self.text_Edit)
            baidu_voice(self.text_Edit)#  调用百度语音合成的模块
        else:
            QMessageBox.information(self,'warning',"请检查您的网络，没有网络无法使用语音功能")
    def close_voice(self):
        os.system('taskkill /f /im PotPlayerMini64.exe')  #关闭播放音频的软件
        self.close()  #关闭界面
class MineWindow2(QMainWindow,Ui_MainWindow3): # ui_mainwindow2 是baiduyuyin这个ui里面的 为了实现双重界面 使用信号

    def __init__(self,parent=None):
        #super(MineWindow, self).__init__(None, Qt.FramelessWindowHint)  # 这句和普通的不一样 因为可以实现无边框
        super(MineWindow2,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.main_speech_reco)  #合成按钮 执行合成函数

        self.pushbutton_close.clicked.connect(self.close)  #关闭窗口

        self.pushbutton_mini.clicked.connect(self.showMinimized)#最小化窗口
        self.button_click=0  #第一次点击 是录音第二次点击录音结束开始识别
        #self.text_label.setText("点击下面的按钮开始录制音频\n再次点击停止录音开始识别")  #第二次打开需要再设置不然会出现之前的画面
        self.recode_switch=1



        self.thread = MyThread() # 创建一个线程
        self.thread.sec_changed_signal.connect(self.get_flames) # 线程发过来的信号挂接到槽：updat

    def get_flames(self,flames):  #进行槽函数的连接 能够获取到录音
        self.flames=flames
        #print(self.flames)
    def main_speech_reco(self):

        if self.button_click==0:
            self.text_label.setText('录音中... ')
            spin_icon = qtawesome.icon('fa5s.microphone-alt-slash', color='white')
            self.pushButton.setIcon(spin_icon)#设置图标
            self.pushButton.setIconSize(QSize(50,50))
            #self.pushButton
            self.button_click=1

            self.thread.start()  #开启线程 进行录音


        elif self.button_click==1:

            # stream.stop_stream() #结束录音 进行保存
            # stream.close()
            # p.terminate()
            self.thread.terminate() #结束录音

            spin_icon = qtawesome.icon('fa5s.microphone-alt', color='white')
            self.pushButton.setIcon(spin_icon)#设置图标
            self.pushButton.setIconSize(QSize(50,50))

            p = pyaudio.PyAudio()   #进行保存
            wf = wave.open('recode.wav', 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(self.flames))
            wf.close()


            self.button_click=0
            speech_recogntion='识别结果：'+baidu_speech_reco()
            self.text_label.setText(speech_recogntion)

class MineWindow3(QMainWindow,Ui_Dialog): # ui_mainwindow2 是baiduyuyin这个ui里面的 为了实现双重界面 使用信号

    def __init__(self,parent=None):
        #super(MineWindow, self).__init__(None, Qt.FramelessWindowHint)  
        super(MineWindow3,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)  #关闭窗口
        self.pushButton_15.clicked.connect(self.close)
        self.pushButton_3.clicked.connect(self.showMinimized)#最小化窗口
        self.pushButton_14.clicked.connect(self.change_config)
        self.lineEdit_7.setPlaceholderText(CAPTURE_SOURCE)#摄像头地址
        self.lineEdit_8.setPlaceholderText(str(SET_SIZE)) #处理图像大小
        self.lineEdit_9.setPlaceholderText(str(TOLERANCE)) 
        self.lineEdit_10.setPlaceholderText("**************")  #
        self.lineEdit_11.setPlaceholderText("**************")  #
        self.lineEdit_12.setPlaceholderText("**************")
    def change_config(self):
        conf = ConfigParser()
        conf.read('config.conf', encoding='gbk') #打开配置文件
        button=0
        source_text=self.lineEdit_7.text()
        size_text=self.lineEdit_8.text()
        tolerance_text=self.lineEdit_9.text()
        secretkey_text=self.lineEdit_10.text()
        apiid_text=self.lineEdit_11.text()
        apikey_text=self.lineEdit_12.text()
        if source_text!='':
            conf.set('image_config','capture_source',source_text)
            button=1
        if size_text!='':
            try:
                if float(size_text)>0 and float(size_text)<1:
                    conf.set('image_config','set_size',size_text)
                    button=1
                else:
                    QMessageBox.about(self,'warning','处理图像大小的值应该取值0-1')
            except:
                QMessageBox.about(self,'warning','处理图像大小的值 输入格式有问题')
        if tolerance_text!='':
            try:
                if float(tolerance_text)>0 and float(tolerance_text)<1:
                    conf.set('image_config','tolerance',tolerance_text)
                    button=1
                else:
                    QMessageBox.about(self,'warning','人脸识别阈值应该取值0-1')
            except:
                QMessageBox.about(self,'warning','人脸识别阈值 输入格式有问题')
        if secretkey_text!='':
            conf.set('speech_config','SECRET_KEY',secretkey_text)
            button=1
        if apiid_text!='':
            conf.set('speech_config','APP_ID',apiid_text)
            button=1
        if apikey_text!='':
            conf.set('speech_config','API_KEY',apikey_text)
            button=1
        conf.write(open("config.conf","w"))
        if button ==1:
            QMessageBox.about(self,'news','配置参数已重置，再次打开即可应用')

class MineWindow4(QMainWindow,Ui_Dialog2): # ui_mainwindow2 是baiduyuyin这个ui里面的 为了实现双重界面 使用信号

    def __init__(self,parent=None):
        #super(MineWindow, self).__init__(None, Qt.FramelessWindowHint)  # 这句和普通的不一样 因为可以实现无边框
        super(MineWindow4,self).__init__(parent)
        self.setupUi(self)
        self.pushButton_5.clicked.connect(self.close_clear)
        self.pushButton_25.clicked.connect(self.close_clear)
        self.pushButton_6.clicked.connect(self.showMinimized)
        self.pushButton_3.clicked.connect(self.search_infor)
        self.pushButton_24.clicked.connect(self.new_register)
        self.conf = ConfigParser()
        self.conf.read('information.conf', encoding='gbk')
    def close_clear(self):
        linetext=[self.lineEdit,self.lineEdit_13,self.lineEdit_14,self.lineEdit_15,self.lineEdit_16,self.lineEdit_17,
                  self.lineEdit_18,self.lineEdit_20]
        i=0
        for lineedit in linetext:
            lineedit.setPlaceholderText(str(i))
            if i<5 and i>0 :
                lineedit.setPlaceholderText("请输入信息")
            if i>=5 and i <=7:
                lineedit.setPlaceholderText('***')
            i=i+1
        self.close()

    def search_infor(self):
        search_name=self.lineEdit.text()
        if search_name in self.conf.sections():
            self.lineEdit_17.setPlaceholderText(self.conf.get(search_name,'年龄'))
            self.lineEdit_18.setPlaceholderText(self.conf.get(search_name,'性别'))
            self.lineEdit_20.setPlaceholderText(self.conf.get(search_name,'更多信息'))

        else:
            QMessageBox.about(self,'warning','找不到'+search_name+'的信息')




    def new_register(self):
        button=0  #当都输入正确的时候写入 配置文件
        name=self.lineEdit_15.text()
        age=self.lineEdit_13.text()
        sex=self.lineEdit_14.text()
        more_infor=self.lineEdit_16.text()
        button2=0
        search_name=self.lineEdit.text()
        age2=self.lineEdit_17.text()
        sex2=self.lineEdit_18.text()
        mor_infor2=self.lineEdit_20.text()
        if name not in self.conf.sections():
            if name != '':
                self.conf.add_section(name)
                if age == '':
                    age='未知'
                elif str.isdigit(age)!= True:
                    button=1
                    QMessageBox.about(self,'warning','年龄请输入正确的格式')
                self.conf.set(name,'年龄',str(age))

                if sex == '':
                    sex='未知'
                elif sex!='男' and sex!='女':
                    button=1
                    QMessageBox.about(self,'warning','性别请输入正确')
                    sex='未知'
                self.conf.set(name,'性别',sex)
                if more_infor == '':
                    more_infor='未知'
                self.conf.set(name,'更多信息',more_infor)

                if button==0:
                    self.conf.write(open("information.conf","w"))
                    QMessageBox.about(self,'news','请将以'+name+'.jpg为命名的照片放入'+getcwd()+'\\'+'photo路径下完成注册')
                elif button == 1:
                    self.conf.remove_section(name)

            else:
                QMessageBox.about(self,'warning','注册信息必须要输入姓名')

        else:
            QMessageBox.about(self,'warning',name+'已经注册过了')

        if age2!=''and str.isdigit(age2)== True:
            self.conf.set(search_name,'年龄',age)
            button2=1
        if sex2!='' and (sex2=='男' or sex2=='女'):
            self.conf.set(search_name,'性别',sex2)
            button2=1
        if mor_infor2!='':
            self.conf.set(search_name,'更多信息',mor_infor2)
            button2=1
        if button2==1:
            self.conf.write(open("information.conf","w"))
            QMessageBox.about(self,'news',search_name+'的部分信息已更改')
class MyThread(QThread):  #录音功能需要使用到 多线程

    sec_changed_signal = pyqtSignal(list) # 信号类型：int

    def __init__(self,  parent=None):
        super().__init__(parent)
        #self.sec = sec # 默认1000秒
    def run(self):
        CHUNK = 1024             
        FORMAT = pyaudio.paInt16  #这个参数后面写的pyaudio.paInt16表示我们使用量化位数 16位来进行录音。
        CHANNELS = 1              
        RATE = 16000              # 采样率16k
        #RECORD_SECONDS = Time     #采样时间
        WAVE_OUTPUT_FILENAME = 'recode22.wav'   #输出文件名
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
        frames = []

        while True:
             data = stream.read(CHUNK)
             frames.append(data)  #进行录音
             self.sec_changed_signal.emit(frames)
            # i=i+1
            # print('dd')


if __name__=="__main__" :
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    Mine=MineWindow()
    speech_reco=MineWindow2()
    setting=MineWindow3()
    register=MineWindow4()
    myWin.signal.connect(Mine.show)  #连接信号
    myWin.signal2.connect(speech_reco.show)
    myWin.signal3.connect(setting.show)
    myWin.signal4.connect(register.show)
    print('打开ui界面所需时间',time()-t)
    sys.exit(app.exec_())
