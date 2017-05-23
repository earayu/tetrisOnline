from tkinter import *
import persistence
class Reg (Frame):
    def __init__(self,master):
        frame = Frame(master)
        frame.pack()
        self.f = master
        self.lab1 = Label(frame,text = "用户名:")
        self.lab1.grid(row = 0,column = 0,sticky = W)
        self.ent1 = Entry(frame)
        self.ent1.grid(row = 0,column = 1,sticky = W)
        self.lab2 = Label(frame,text = "密码:")
        self.lab2.grid(row = 1,column = 0)
        self.ent2 = Entry(frame,show = "*")
        self.ent2.grid(row = 1,column = 1,sticky = W)
        self.button = Button(frame,text = "登录",command = self.Submit)
        self.button.grid(row = 2,column = 1,sticky = E)
        self.lab3 = Label(frame,text = "")
        self.lab3.grid(row = 2,column = 0,sticky = W)
        self.username = None
        self.password = None


    def Submit(self):
        username = self.ent1.get()
        password = self.ent2.get()
        if persistence.login(username, password):
            self.username,self.password = username,password
            self.f.quit()
        else:
            self.lab3["text"] = "错误!"
        self.ent1.delete(0,len(username))
        self.ent2.delete(0,len(password))


def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
    print(size)
    root.geometry(size)

root = Tk()
root.title("登录")
center_window(root,200,85)
app = Reg(root)
root.mainloop()
