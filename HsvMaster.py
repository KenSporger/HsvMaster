import os
import cv2
import numpy as np
from tkinter import *
from tkinter.messagebox import askquestion
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from PIL import Image, ImageTk

# 单通道范围提取
def Extract(src,min,max):
    if min<max:
        return cv2.inRange(src,min,max)
    else:
        #范围(0,max)+(min,255)
        return cv2.bitwise_not(cv2.inRange(src,max,min))


#存储6个参数值和图片源地址
class HSV():
    def __init__(self,window,path):
        self.window = window
        self.h_min = IntVar(self.window,0)
        self.h_max = IntVar(self.window,180)
        self.s_min = IntVar(self.window,0)
        self.s_max = IntVar(self.window,255)
        self.v_min = IntVar(self.window,0)
        self.v_max = IntVar(self.window,255)

        self.origin_img_path = path
        self.origin_img_cv = cv2.imread(self.origin_img_path)
        self.work_img_cv = self.origin_img_cv
        self.work_img_mask = None
        # 改动标志
        self.change_flag = False

    #更新hsv
    def update(self,hsv,flag=False):
        self.h_min.set(hsv.h_min.get())
        self.h_max.set(hsv.h_max.get())
        self.s_min.set(hsv.s_min.get())
        self.s_max.set(hsv.s_max.get())
        self.v_min.set(hsv.v_min.get())
        self.v_max.set(hsv.v_max.get())
        self.origin_img_path = hsv.origin_img_path
        self.origin_img_cv = hsv.origin_img_cv
        self.work_img_cv = hsv.work_img_cv
        self.work_img_mask = hsv.work_img_mask
        #源hsv得到保存,视作没有新的改动
        self.change_flag = flag
        hsv.change_flag = False


    #更新work
    def updateWork(self):
        h, s, v = cv2.split(cv2.cvtColor(self.origin_img_cv, cv2.COLOR_BGR2HSV))
        #获取当前6个参数值
        h = Extract(h,self.h_min.get(),self.h_max.get())
        s = Extract(s, self.s_min.get(), self.s_max.get())
        v = Extract(v, self.v_min.get(), self.v_max.get())
        #三通道相与
        mask = cv2.bitwise_and(h,s,mask=v)
        #掩码提取
        self.work_img_cv= cv2.bitwise_and(self.origin_img_cv,self.origin_img_cv,mask=mask)
        self.work_img_mask = mask
        self.change_flag = True


    #打印简要
    def toString(self):
        diction = dict()
        diction['new_flag'] = self.change_flag
        diction['h_min']=self.h_min.get()
        diction['h_max'] = self.h_max.get()
        diction['s_min'] = self.s_min.get()
        diction['s_max'] = self.s_max.get()
        diction['v_min'] = self.v_min.get()
        diction['v_max'] = self.v_max.get()
        diction['path'] = self.origin_img_path

        return str(diction)


#软件UI与事件控制
class GUI():
    def __init__(self,window):
        self.window = window
        self.icon_path = './image/hsv_icon.ico'
        self.root_img_path = './image/root.png'
        #窗口属性
        self.window.title("HsvMaster")
        self.window.geometry('1000x600+500+200')
        self.window["bg"] = "DimGray"
        # 图标
        self.icon = ImageTk.PhotoImage(file=self.icon_path)
        self.window.call('wm','iconphoto',self.window._w,self.icon)

        #默认hsv,受保护
        self.root_hsv = HSV(self.window,self.root_img_path)
        #建立副本
        self.cur_hsv = HSV(self.window,self.root_img_path)

        #滑动条
        self.hmin_label = Label(self.window,text='色调下限',fg='WhiteSmoke',bg="DimGray")
        self.hmin_scale = Scale(self.window,orient=HORIZONTAL,from_=0,to=180,state=DISABLED,
                                variable=self.cur_hsv.h_min,command=self.refreshCurrentHsv,
                                resolution=1,tickinterval=30,length=200,width=7,fg='WhiteSmoke',bg="DimGray")
        self.hmax_label = Label(self.window,text='色调上限',fg='WhiteSmoke',bg="DimGray")
        self.hmax_scale = Scale(self.window,orient=HORIZONTAL,from_=0,to=180,state=DISABLED,
                                variable=self.cur_hsv.h_max,command=self.refreshCurrentHsv,
                                resolution=1,tickinterval=30,length=200,width=7,fg='WhiteSmoke',bg="DimGray")
        self.smin_label = Label(self.window,text='饱和度下限',fg='WhiteSmoke',bg="DimGray")
        self.smin_scale = Scale(self.window,orient=HORIZONTAL,from_=0,to=255,state=DISABLED,
                                variable=self.cur_hsv.s_min,command=self.refreshCurrentHsv,
                                resolution=1,tickinterval=50,length=200,width=7,fg='WhiteSmoke',bg="DimGray")
        self.smax_label = Label(self.window,text='饱和度上限',fg='WhiteSmoke',bg="DimGray")
        self.smax_scale = Scale(self.window,orient=HORIZONTAL,from_=0,to=255,state=DISABLED,
                                variable=self.cur_hsv.s_max,command=self.refreshCurrentHsv,
                                resolution=1,tickinterval=50,length=200,width=7,fg='WhiteSmoke',bg="DimGray")
        self.vmin_label = Label(self.window,text='明度下限',fg='WhiteSmoke',bg="DimGray")
        self.vmin_scale = Scale(self.window,orient=HORIZONTAL,from_=0,to=255,state=DISABLED,
                                variable=self.cur_hsv.v_min,command=self.refreshCurrentHsv,
                                resolution=1,tickinterval=50,length=200,width=7,fg='WhiteSmoke',bg="DimGray")
        self.vmax_label = Label(self.window,text='明度上限',fg='WhiteSmoke',bg="DimGray")
        self.vmax_scale = Scale(self.window,orient=HORIZONTAL,from_=0,to=255,state=DISABLED,
                                variable=self.cur_hsv.v_max,command=self.refreshCurrentHsv,
                                resolution=1,tickinterval=50,length=200,width=7,fg='WhiteSmoke',bg="DimGray")

        #按钮
        self.import_button = Button(self.window, text='导入图片',font=('隶书',45), height=2, width=9,state=NORMAL,
                                    fg='WhiteSmoke',bg="BurlyWood",command=self.import_img)
        self.clear_button = Button(self.window, text='删除当前',font=('隶书',12), height=2, width=15,state=NORMAL,
                                   fg='WhiteSmoke',bg="BurlyWood",command=self.deleteHsv)
        self.delete_button = Button(self.window, text='保存选区',font=('隶书',12), height=2, width=15,state=NORMAL,
                                    fg='WhiteSmoke',bg="BurlyWood",command=self.saveCurrentHsv)
        self.switch_button = Button(self.window,text='选区切换',font=('隶书',12), height=2, width=15,state=NORMAL,
                                    fg='WhiteSmoke',bg="BurlyWood",command=self.switch_hsv)
        self.save_button = Button(self.window, text='新建选区',font=('隶书',12), height=2, width=15,state=NORMAL,
                                  fg='WhiteSmoke',bg="BurlyWood",command=self.createNewHsv)
        self.merge_button = Button(self.window, text='合并选区',font=('隶书',12), height=2, width=15,state=NORMAL,
                                   fg='WhiteSmoke',bg="BurlyWood",command=self.mergeHsv)
        self.picture_button = Button(self.window, text='生成图片',font=('隶书',12), height=2, width=15,state=NORMAL,
                                     fg='WhiteSmoke',bg="BurlyWood",command=self.saveImageFile)

        #图片
        self.origin = Label(self.window, width=300, height=300)
        self.work = Label(self.window, width=300, height=300)

        #hsv信息
        self.hsv_list = list()
        self.cur_hsv_index = 0

        self.origin_img = None
        self.work_img = None


    #导入图片
    def import_img(self):
        self.ask_save()
        path = askopenfilename(filetypes=[('.JPG','.jpg'),('.BMP','.bmp'),('.JPEG','.jpeg'),('.PNG','.png')])
        #激活滑动条
        self.setScalesState(NORMAL)
        #新建默认work
        self.createNewHsv(HSV(self.window,path))

    #保存图片
    def saveImageFile(self):
        file_path = asksaveasfilename(filetypes=[('.JPG','.jpg'),('.BMP','.bmp'),('.JPEG','.jpeg'),('.PNG','.png')],defaultextension=True)
        cv2.imwrite(file_path,self.cur_hsv.work_img_cv)
    #设置滑动条状态
    def setScalesState(self,state=NORMAL):
        self.hmin_scale['state'] = state
        self.hmax_scale['state'] = state
        self.smin_scale['state'] = state
        self.smax_scale['state'] = state
        self.vmin_scale['state'] = state
        self.vmax_scale['state'] = state

    #hsv复位
    def reset(self):
        self.setScalesState(DISABLED)
        #cur_hsv.change_flag = True
        self.cur_hsv.update(self.root_hsv)
        self.loadImg()


    #保存cur_hsv到列表
    def saveCurrentHsv(self):
        if len(self.hsv_list) <= self.cur_hsv_index:
            self.hsv_list.append(HSV(self.window,None))
        self.hsv_list[self.cur_hsv_index].update(self.cur_hsv)
        self.printHsvList()

    def printHsvList(self):
        for hsv in self.hsv_list:
            print(hsv.toString())
        print('\n')

    #增加hsv到hsv_list，并读取到cur_hsv
    def createNewHsv(self,hsv=None,flag=False):
        self.ask_save()
        if hsv is None:
            hsv = HSV(self.window,self.cur_hsv.origin_img_path)
        self.cur_hsv.update(hsv,flag)
        self.cur_hsv_index = len(self.hsv_list)
        self.loadImg()

    #删除以保存的当前hsv
    def deleteHsv(self):
        self.hsv_list.pop(self.cur_hsv_index)
        if len(self.hsv_list)>0:
            self.cur_hsv_index -= 1
            self.cur_hsv.update(self.hsv_list[self.cur_hsv_index])
        else:
            self.cur_hsv.update(self.root_hsv)
        self.loadImg()

    #弹窗询问是否保存
    def ask_save(self):
        if self.cur_hsv.change_flag and askquestion('提示','是否保存当前选区？')=='yes':
            self.saveCurrentHsv()
        else:
            self.cur_hsv.change_flag = False

    #切换历史选区
    def switch_hsv(self):
        self.ask_save()
        self.cur_hsv_index += 1
        if self.cur_hsv_index > len(self.hsv_list)-1:
            self.cur_hsv_index = 0
        self.cur_hsv.update(self.hsv_list[self.cur_hsv_index])
        self.loadImg()

    #合并
    def mergeHsv(self):
        hsv = HSV(self.window,None)
        hsv.origin_img_path = self.hsv_list[0].origin_img_path
        hsv.origin_img_cv = self.hsv_list[0].origin_img_cv
        hsv.work_img_cv = np.zeros(hsv.origin_img_cv.shape,dtype=np.uint8)
        for each in self.hsv_list:
            hsv.work_img_cv = cv2.add(hsv.work_img_cv,each.work_img_cv)
        self.createNewHsv(hsv,flag=True)



    #显示所有控件
    def create_widgets(self):

        # scale position
        self.hmin_label.grid(row=0, column=0,padx=15)
        self.hmin_scale.grid(row=0,column=1,pady=2)
        self.hmax_label.grid(row=1, column=0)
        self.hmax_scale.grid(row=1,column=1,pady=2)
        self.smin_label.grid(row=2, column=0)
        self.smin_scale.grid(row=2,column=1,pady=2)
        self.smax_label.grid(row=3, column=0)
        self.smax_scale.grid(row=3,column=1,pady=2)
        self.vmin_label.grid(row=4, column=0)
        self.vmin_scale.grid(row=4,column=1,pady=2)
        self.vmax_label.grid(row=5, column=0)
        self.vmax_scale.grid(row=5,column=1,pady=2)

        #button position
        self.import_button.place(x=18,y=400)
        self.clear_button.place(x=370,y=420)
        self.delete_button.place(x=570,y=420)
        self.switch_button.place(x=770,y=420)
        self.save_button.place(x=370,y=500)
        self.merge_button.place(x=570,y=500)
        self.picture_button.place(x=770,y=500)

        self.origin.place(x=320, y=30)
        self.work.place(x=650, y=30)

        self.reset()

    # 图片数据转换np.array->ImageTk
    def cvToImage(self,cv):
        img = cv2.resize(cv,(300,300))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        return ImageTk.PhotoImage(img)

    #融入work背景
    def insertBackground(self,img,mask):
        if mask is None:
            return img
        else:
            root = cv2.resize(self.root_hsv.origin_img_cv,(mask.shape[1],mask.shape[0]))
            mask = mask>0
            root[mask]=0
            return cv2.bitwise_or(img,root)

    #加载origin和work图片
    def loadImg(self):
        self.origin_img = self.cvToImage(self.cur_hsv.origin_img_cv)
        self.work_img = self.cvToImage(self.insertBackground(self.cur_hsv.work_img_cv,self.cur_hsv.work_img_mask))
        self.origin['image'] = self.origin_img
        self.work['image'] = self.work_img

    #更行work区
    def refreshCurrentHsv(self,_=None):
        self.cur_hsv.updateWork()
        self.loadImg()



if __name__ == '__main__':
    my_window = Tk()
    my_gui = GUI(my_window)
    my_gui.create_widgets()
    my_window.mainloop()
