import cv2
import tkinter as tk
import time
import os
import tempfile
import sqlite3
import sys
from datetime import datetime
import glob
import re
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType
from gtts import gTTS
from pygame import mixer
from tkinter import ttk, messagebox

face_client = FaceClient('https://david-wu.cognitiveservices.azure.com/', CognitiveServicesCredentials('3812cb051d0b46dd98bf2993cf014738'))
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
GROUP_ID = 'python-group11'

class database():

    def db_creat(self):
        connect = sqlite3.connect('mydatabase.sqlite')  # 與資料庫連線
        # 新建 mytable 資料表  (如果尚未建立的話)
        sql = 'CREATE TABLE IF NOT EXISTS stuInfo ("姓名" TEXT,"系所" TEXT,"學號" TEXT,"personid" TEXT)'
        connect.execute(sql)
        sql = 'CREATE TABLE IF NOT EXISTS rollCall ("姓名" TEXT,"學號" TEXT,"出席時間" TEXT,"是否遲到" TEXT)'
        connect.execute(sql)

    def db_add_person(self):
        group_photo = 'train1.jpg'
        image = open(group_photo, 'r+b')
        face_ids = []
        faces = face_client.face.detect_with_stream(image)
        for face in faces:
            face_ids.append(face.face_id)
        results = face_client.face.identify(face_ids, GROUP_ID)
        for person in results:
            personid = person.candidates[0].person_id
        depp = {"01": "工葉管理系", "02": "電子工程系", "03": "機械工程系", "04": "材料科學與工程學系",
                "05": "營建工程系", "06": "化學工程系", "07": "電機工程系", "08": "企業管理系", "09": "資管",
                "10": "工商業設計系", "13": "建築系", "15": "資訊工程系", "17": "應用外語系", "30": "全校不分系",
                "31": "工程學士班", "32": "電資學士班", "33": "管理學士班", "34": "創意設計學士班"}
        connect = sqlite3.connect('mydatabase.sqlite')  # 與資料庫連線
        # 取得現在時間
        a = list(stuID)
        dep = depp[''.join(a[4:6])]

        # 新增一筆資料的 SQL 語法
        sql = f'insert into stuInfo values("{name}","{dep}","{stuID}","{personid}")'
        connect.execute(sql)  # 執行 SQL 語法
        connect.commit()  # 更新資料庫
        connect.close()  # 關閉資料庫

    def db_delete(self):
        connect = sqlite3.connect('mydatabase.sqlite')  # 與資料庫連線
        sql = "delete from stuInfo"
        connect.execute(sql)  # 執行 SQL 語法
        sql = "delete from rollCall"
        connect.execute(sql)  # 執行 SQL 語法
        connect.commit()  # 更新資料庫
        connect.close()  # 關閉資料庫

    def db_search_personid(self, personid):
        connect = sqlite3.connect('mydatabase.sqlite')  # 與資料庫連線
        sql = "select * from stuInfo where personid = '{}'".format(personid)
        cursor = connect.execute(sql)  # 執行 SQL 語法得到 cursor 物件
        dataset = cursor.fetchall()  # 取得所有資料
        return dataset[0]

    def db_read_stuInfo(self):
        connect = sqlite3.connect('mydatabase.sqlite')  # 與資料庫連線
        sql = 'select * from stuInfo'  # 選取資料表中所有資料的 SQL 語法
        cursor = connect.execute(sql)  # 執行 SQL 語法得到 cursor 物件
        dataset = cursor.fetchall()  # 取得所有資料
        return dataset

    def stuID_duplicate(self, stuID):
        connect = sqlite3.connect('mydatabase.sqlite')  # 與資料庫連線
        sql = "select * from stuInfo where 學號 = '{}'".format(stuID)
        cursor = connect.execute(sql)  # 執行 SQL 語法得到 cursor 物件
        dataset = cursor.fetchall()  # 取得所有資料
        print(dataset)
        if dataset == []:
            return False
        else:
            return True

    def db_rollCall(self, name, stuID, late):
        global arrtime
        connect = sqlite3.connect('mydatabase.sqlite')  # 與資料庫連線
        sql = f'insert into rollCall values("{name}","{stuID}","{arrtime}","{late}")'
        connect.execute(sql)  # 執行 SQL 語法
        connect.commit()  # 更新資料庫
        connect.close()  # 關閉資料庫

    def db_read_rollCall(self):
        connect = sqlite3.connect('mydatabase.sqlite')  # 與資料庫連線
        sql = 'select * from rollCall'  # 選取資料表中所有資料的 SQL 語法
        cursor = connect.execute(sql)  # 執行 SQL 語法得到 cursor 物件
        dataset = cursor.fetchall()  # 取得所有資料
        return dataset

def face_shot(filename):
    global tempho
    isCnt = False                                   # 用來判斷是否正在進行倒數計時中
    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)    # 開啟編號 0 的攝影機
    restart = True
    while capture.isOpened() and restart:           # 判斷攝影機是否開啟成功
        sucess, img = capture.read()                # 讀取攝影機影像
        if not sucess:
            print('讀取影像失敗')
            continue
        img_copy = img.copy()                       # 複製影像
        faces = face_detector.detectMultiScale(     # 從攝影機影像中偵測人臉
                    img,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(200,200))
        if len(faces) == 1:                         # 如果偵測到一張人臉
            if isCnt == False:
                t1 = time.time()                    # 紀錄現在的時間
                isCnt = True                        # 告訴程式目前進入倒數狀態
            cnter = 3 - int(time.time() - t1)       # 更新倒數計時器
            for (x, y, w, h) in faces:              # 畫出人臉位置
                cv2.rectangle(                      # 繪製矩形
                        img_copy, (x, y), (x+w, y+h),
                        (255, 255, 255), 1)
                cv2.putText(                        # 繪製倒數數字
                        img_copy, str(cnter),
                        (x+int(w/2), y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 1)
            if cnter == 0:                          # 倒數結束
                isCnt = False                       # 告訴程式離開倒數狀態
                if filename=='tem':
                    cv2.imwrite('{}.png'.format(tempho.name), img)
                    face()
                else:
                    cv2.imwrite(filename + '.jpg', img)
                    img=cv2.resize(img, (288,216))
                    cv2.imwrite(filename + '_small.png', img)
                restart = False
        else:                                       # 如果不是一張人臉
            isCnt = False                           # 設定非倒數狀態

        cv2.imshow('Frame', img_copy)               # 顯示影像
        k = cv2.waitKey(1)                          # 讀取按鍵輸入(若無會傳回 -1)
        if not restart:                             # 按下 q 離開迴圈, 結束程式
            cv2.destroyAllWindows()                 # 關閉視窗
            capture.release()                       # 關閉攝影機
            break                                   # 離開無窮迴圈, 結束程式
    else:
        print('開啟攝影機失敗')


def face():
    '''
    人臉辨識
    '''
    global var, arrtime, hour, min
    image = open('{}.png'.format(tempho.name), 'r+b')
    face_ids = []
    faces = face_client.face.detect_with_stream(image)
    print(faces)
    for face in faces:
        face_ids.append(face.face_id)
    results = face_client.face.identify(face_ids, GROUP_ID)
    print('Identifying faces in {}'.format(os.path.basename(image.name)))
    if not results:
        print('No person identified in the person group for faces from {}.'.format(os.path.basename(image.name)))
    for person in results:
        if len(person.candidates)==0:
            var.set('無法辨識您的臉，請至管理帳號中新增學生')
        elif float(person.candidates[0].confidence) < 0.8:
            var.set('無法辨識您的臉，請至管理帳號中新增學生')
        else:
            #print('Person for person ID {} is identified in {} with a confidence of {}.'.format(person.candidates[0].person_id, group_photo,person.candidates[0].confidence))
            identify = db.db_search_personid(person.candidates[0].person_id)
            arrtime = datetime.now().strftime('%H:%M:%S')
            thishour = datetime.now().strftime('%H')
            thismin = datetime.now().strftime('%M')
            if int(hour.get()) > int(thishour) or (int(hour.get()) == int(thishour) or int(min.get()) > int(thismin)):
                late = "準時!!"
            else:
                late = "遲到!!"

            var.set('Hi {}! 出席時間: {} {}'.format(identify[0], arrtime, late))       #person.candidates[0].confidence
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                tts = gTTS(text='hi {}'.format(identify[0]), lang='zh-tw')
                tts.save('{}.mp3'.format(fp.name))
                mixer.init()
                mixer.music.load('{}.mp3'.format(fp.name))
                mixer.music.play()
                time.sleep(3)                                                                                                                                                     #第二個資料庫
                db.db_rollCall(identify[0], identify[2], late)

def train_face():
    train = face_client.person_group_person.create(GROUP_ID, "train")

    '''
    上傳照片
    '''
    david_images = [file for file in glob.glob('*.jpg') if file.startswith("train")]

    for image in david_images:
        w = open(image, 'r+b')
        face_client.person_group_person.add_face_from_stream(GROUP_ID, train.person_id, w)

    '''
    訓練
    '''
    print()
    print('Training the person group...')
    # Train the person group
    face_client.person_group.train(GROUP_ID)

    while (True):
        training_status = face_client.person_group.get_training_status(GROUP_ID)
        print("Training status: {}.".format(training_status.status))
        print()
        if (training_status.status is TrainingStatusType.succeeded):
            db.db_add_person()
            break
        elif (training_status.status is TrainingStatusType.failed):
            sys.exit('Training the person group has failed.')
        time.sleep(5)

def recreatPersonGroup():
    '''
    刪除 group
    '''

    # Delete the main person group.
    face_client.person_group.delete(person_group_id=GROUP_ID, )
    print("Deleted the person group {} from the source location.".format(GROUP_ID))
    print()
    '''
    建立群駔
    '''
    print('Person group:', GROUP_ID)
    face_client.person_group.create(person_group_id=GROUP_ID, name=GROUP_ID)

class basedesk():
    def __init__(self, master):
        global hour,min
        self.root = master
        self.root.config()
        self.root.title('Python 11 組 專題')
        self.root.geometry('500x200')
        self.root.resizable(0, 0)
        self.root.configure(bg='white')
        login(self.root)
        hour = tk.StringVar()
        min = tk.StringVar()
        hour.set('9')
        min.set('10')

class login():
    def __init__(self, master):
        self.master = master
        self.login = tk.Frame(self.master, bg='white')
        self.login.pack()
        l = tk.Label(self.login, text='人臉辨識點名系統', font=('微軟正黑體', 30), bg='white', height=2, width=20)
        l.pack()
        btn1 = tk.Button(self.login, text='學生點名', font=('微軟正黑體', 30), bg='white', command=self.studentLogin, relief=tk.GROOVE)
        btn1.pack(side=tk.RIGHT)
        btn2 = tk.Button(self.login, text='管理帳號', font=('微軟正黑體', 30), bg='white', command=self.teacherLogin, relief=tk.GROOVE)
        btn2.pack(side=tk.LEFT)

    def studentLogin(self):
        self.login.destroy()
        student(self.master)
    def teacherLogin(self):
        self.login.destroy()
        teacher(self.master)

class student():
    def __init__(self, master):
        global var
        var = tk.StringVar()
        var.set('')
        self.master = master
        self.student = tk.Frame(self.master, bg='white', height=200, width=500)
        self.student.pack_propagate(0)
        self.student.pack()
        btn = tk.Button(self.student, text='開始辨識', font=('微軟正黑體', 30), bg='white', command=lambda:face_shot('tem'), relief=tk.GROOVE)
        btn.pack(pady=10)
        label = tk.Label(self.student, textvariable=var, font=('微軟正黑體', 15), bg='white')
        label.pack()
        btn = tk.Button(self.student, text='返回', font=('微軟正黑體', 15), bg='white', command=self.back, relief=tk.GROOVE)
        btn.place(x=0, y=157)

    def back(self):
        self.student.destroy()
        login(self.master)

class teacher():
    def __init__(self, master):
        global hour,min
        self.master = master
        self.teacher = tk.Frame(self.master, bg='white', height=200, width=500)
        self.teacher.pack_propagate(0)
        self.teacher.pack()
        btn1 = tk.Button(self.teacher, text='新增學生', font=('微軟正黑體', 15), width=15, bg='white', command=self.add, relief=tk.GROOVE)
        btn1.pack()
        btn2 = tk.Button(self.teacher, text='查看所有學生資料', font=('微軟正黑體', 15), width=15, bg='white', command=self.examineStuInfo, relief=tk.GROOVE)
        btn2.pack()
        btn3 = tk.Button(self.teacher, text='查看點名紀錄', font=('微軟正黑體', 15), width=15, bg='white', command=self.examineRollCall, relief=tk.GROOVE)
        btn3.pack()
        self.timeset = tk.Frame(self.teacher, bg='white', height=50, width=250)
        self.timeset.pack_propagate(0)
        self.timeset.pack()
        l = tk.Label(self.timeset, text='上課時間', font=('微軟正黑體', 15), bg='white')
        l.pack(side=tk.LEFT)
        inputname = tk.Entry(self.timeset, textvariable=hour, font=('微軟正黑體', 15), width=5, bg='white')
        inputname.pack(side=tk.LEFT)
        l = tk.Label(self.timeset, text='：', font=('微軟正黑體', 15), bg='white', height=2, width=1)
        l.pack(side=tk.LEFT)
        inputname = tk.Entry(self.timeset, textvariable=min, font=('微軟正黑體', 15), width=5, bg='white')
        inputname.pack(side=tk.LEFT)
        btn = tk.Button(self.teacher, text='返回', font=('微軟正黑體', 15), bg='white', command=self.back, relief=tk.GROOVE)
        btn.place(x=0, y=157)

    def back(self):
        self.teacher.destroy()
        login(self.master)

    def add(self):
        self.teacher.destroy()
        add_student(self.master)

    def examineStuInfo(self):
        self.teacher.destroy()
        examineStuInfo(self.master)

    def examineRollCall(self):
        self.teacher.destroy()
        examineRollCall(self.master)

class add_student():
    def __init__(self, master):
        self.name = tk.StringVar()
        self.stuID = tk.StringVar()
        self.master = master
        self.add_student = tk.Frame(self.master, bg='white', height=200, width=500)
        self.add_student.pack_propagate(0)
        self.add_student.pack()
        text = tk.Label(self.add_student, text='請輸入姓名:', font=('微軟正黑體', 15), bg='white')
        text.pack()
        inputname = tk.Entry(self.add_student, textvariable=self.name, font=('微軟正黑體', 15), bg='white')
        inputname.pack(pady=10)
        text = tk.Label(self.add_student, text='請輸入學號:', font=('微軟正黑體', 15), bg='white')
        text.pack()
        inputstuID = tk.Entry(self.add_student, textvariable=self.stuID, font=('微軟正黑體', 15), bg='white')
        inputstuID.pack(pady=10)
        btn = tk.Button(self.add_student, text='確定', font=('微軟正黑體', 20), bg='white', command=self.takephoto, relief=tk.GROOVE)
        btn.pack()
        btn = tk.Button(self.add_student, text='返回', font=('微軟正黑體', 15), bg='white', command=self.stuback, relief=tk.GROOVE)
        btn.place(x=0, y=157)

    def takephoto(self):
        global p1,p2,p3,name,stuID
        name = self.name.get()
        stuID = self.stuID.get()
        match = '^[A-B]{1}[0-9]{8}$'
        IDcheck = re.match(match, stuID)
        if name == '' or name == '名稱為空白!!':
            self.name.set('名稱為空白!!')
        elif stuID == '' or stuID == '學號為空白!!':
            self.stuID.set('學號為空白!!')
        elif not IDcheck or stuID == '學號格式錯誤!!':
            self.stuID.set('學號格式錯誤!!')
        elif db.stuID_duplicate(stuID):
            self.stuID.set('此學號已被註冊過!!')
        else:
            self.add_student.destroy()
            self.master.geometry('1000x500')
            self.takephoto = tk.Frame(self.master, bg='white', width=1000, height=500)
            self.takephoto.pack_propagate(0)
            self.takephoto.pack()

            text = tk.Label(self.takephoto, text='請拍三張不同光線角度的單人照片', font=('微軟正黑體', 20), bg='white')
            text.place(relx=0.5, y=10, anchor=tk.N)
            text = tk.Label(self.takephoto, text='照片一', font=('微軟正黑體', 20), bg='white')
            text.place(relx=0.2, y=60, anchor=tk.N)
            text = tk.Label(self.takephoto, text='照片二', font=('微軟正黑體', 20), bg='white')
            text.place(relx=0.5, y=60, anchor=tk.N)
            text = tk.Label(self.takephoto, text='照片三', font=('微軟正黑體', 20), bg='white')
            text.place(relx=0.8, y=60, anchor=tk.N)

            p1 = False
            p2 = False
            p3 = False

            btn1 = tk.Button(self.takephoto, text='拍照', font=('微軟正黑體', 20), bg='white', command=self.photo1, relief=tk.GROOVE)
            btn1.place(relx=0.2, y=350, anchor=tk.N)
            btn2 = tk.Button(self.takephoto, text='拍照', font=('微軟正黑體', 20), bg='white', command=self.photo2, relief=tk.GROOVE)
            btn2.place(relx=0.5, y=350, anchor=tk.N)
            btn3 = tk.Button(self.takephoto, text='拍照', font=('微軟正黑體', 20), bg='white', command=self.photo3, relief=tk.GROOVE)
            btn3.place(relx=0.8, y=350, anchor=tk.N)
            btn = tk.Button(self.takephoto, text='返回', font=('微軟正黑體', 15), bg='white', command=self.phoback, relief=tk.GROOVE)
            btn.place(x=0, y=457)

            self.btn4 = tk.Button(self.takephoto, text='確定', font=('微軟正黑體', 20), bg='white', command=self.train, relief=tk.GROOVE)

            self.label1 = tk.Label(self.takephoto, bg='white', compound=tk.CENTER)
            self.label1.place(relx=0.2, y=100, anchor=tk.N)
            self.label2 = tk.Label(self.takephoto, bg='white', compound=tk.CENTER)
            self.label2.place(relx=0.5, y=100, anchor=tk.N)
            self.label3 = tk.Label(self.takephoto, bg='white', compound=tk.CENTER)
            self.label3.place(relx=0.8, y=100, anchor=tk.N)

    def stuback(self):
        self.add_student.destroy()
        teacher(self.master)
    def phoback(self):
        self.master.geometry('500x200')
        self.takephoto.destroy()
        teacher(self.master)
    def photo1(self):
        global photo1,p1
        face_shot('train1')
        photo1 = tk.PhotoImage(file='train1_small.png')
        self.label1.config(image=photo1)
        p1=True
        self.checkphotos()
    def photo2(self):
        global photo2,p2
        face_shot('train2')
        photo2 = tk.PhotoImage(file='train2_small.png')
        self.label2.config(image=photo2)
        p2=True
        self.checkphotos()
    def photo3(self):
        global photo3,p3
        face_shot('train3')
        photo3 = tk.PhotoImage(file='train3_small.png')
        self.label3.config(image=photo3)
        p3=True
        self.checkphotos()
    def checkphotos(self):
        if (p1 and p2 and p3):
            self.btn4.place(relx=0.5, y=430, anchor=tk.N)
    def train(self):
        train_face()
        tk.messagebox.showinfo(message='辨識成功!')
        self.master.geometry('500x200')
        self.takephoto.destroy()
        teacher(self.master)

class examineStuInfo():
    def __init__(self, master):
        self.name = tk.StringVar()
        self.stuID = tk.StringVar()
        self.master = master
        self.examineStuInfo = tk.Frame(self.master, bg='white', height=200, width=500)
        self.examineStuInfo.pack_propagate(0)
        self.examineStuInfo.pack()

        scrollbar = tk.Scrollbar(self.examineStuInfo)
        scrollbar.pack(side="right", fill="y")
        tree = ttk.Treeview(self.examineStuInfo, yscrollcommand=scrollbar.set)  # 表格
        tree["columns"] = (1, 2)
        tree.column("#0", width=150, minwidth=150, stretch=tk.NO)
        tree.column(1, width=150, minwidth=150, stretch=tk.NO)
        tree.column(2, width=150, minwidth=150, stretch=tk.NO)

        tree.heading("#0", text="姓名")
        tree.heading(1, text="系所")
        tree.heading(2, text="學號")

        for data in db.db_read_stuInfo():
            tree.insert("", 'end', text=data[0], values=(data[1], data[2]))

        tree.pack()

        btn = tk.Button(self.examineStuInfo, text='返回', font=('微軟正黑體', 15), bg='white', command=self.back, relief=tk.GROOVE)
        btn.place(x=0, y=157)

    def back(self):
        self.examineStuInfo.destroy()
        teacher(self.master)

class examineRollCall():
    def __init__(self, master):
        self.name = tk.StringVar()
        self.stuID = tk.StringVar()
        self.master = master
        self.examineRollCall = tk.Frame(self.master, bg='white', height=200, width=500)
        self.examineRollCall.pack_propagate(0)
        self.examineRollCall.pack()

        scrollbar = tk.Scrollbar(self.examineRollCall)
        scrollbar.pack(side="right", fill="y")
        tree = ttk.Treeview(self.examineRollCall, yscrollcommand=scrollbar.set)  # 表格
        tree["columns"] = (1, 2, 3)
        tree.column("#0", width=112, minwidth=112, stretch=tk.NO)
        tree.column(1, width=112, minwidth=112, stretch=tk.NO)
        tree.column(2, width=112, minwidth=112, stretch=tk.NO)
        tree.column(3, width=112, minwidth=112, stretch=tk.NO)

        tree.heading("#0", text="姓名")
        tree.heading(1, text="學號")
        tree.heading(2, text="出席時間")
        tree.heading(3, text="是否遲到")

        for data in db.db_read_rollCall():
            tree.insert("", 'end', text=data[0], values=(data[1], data[2], data[3]))

        tree.pack()

        btn = tk.Button(self.examineRollCall, text='返回', font=('微軟正黑體', 15), bg='white', command=self.back, relief=tk.GROOVE)
        btn.place(x=0, y=157)

    def back(self):
        self.examineRollCall.destroy()
        teacher(self.master)

#face_client.person_group_person.delete(person_group_id=GROUP_ID, person_id='5e7cca42-74d3-440f-ab96-6da9985b05e0')

tempho=tempfile.NamedTemporaryFile(delete=True)
db=database()
#db.db_delete()
db.db_creat()
#recreatPersonGroup()
root = tk.Tk()
basedesk(root)
root.mainloop()