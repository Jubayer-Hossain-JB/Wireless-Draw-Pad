from bottle import Bottle, ServerAdapter, response, static_file, request
from socket import gethostbyname, gethostname
from io import BytesIO
from base64 import b64encode
import threading
import pyautogui
pyautogui.FAILSAFE = False

from customtkinter import *
from tkinter.ttk import Separator

set_appearance_mode('Dark')
set_default_color_theme('blue')

class ToplevelWidget(CTkFrame):
    def __init__(self,size:tuple=(400,400),pos:tuple=(0,0),*arg):
        self.x=None
        self.y = None

        self.win = CTkToplevel(bd=2,*arg)
        self.mast = CTkFrame(self.win,border_width=2)
        self.mast.place(relwidth=1, relheight=1,bordermode='outside')
        super().__init__(self.win,corner_radius=0)
        self.place(y=27,relwidth=1)
        self.win.grab_set()
        self.win.overrideredirect(True)
        self.titleBar = CTkFrame(self.win, height=25,fg_color='#333333', corner_radius=0)
        self.titleBar.place(relx=0.5,anchor='n', relwidth=1)
        self.ttex=CTkLabel(self.titleBar,text=self.title,font=('arial',12))
        self.ttex.place(relheight=0.5,relx=0.5,rely=0.5,anchor='center')
        CTkButton(self.titleBar,text="X", width=25, height=25,fg_color='#222222',hover_color="#550000",command=self.close).place(relx=1,rely=0,anchor='ne')

        for widget in (self.titleBar._canvas, self.ttex._label):
            widget.bindtags(('titlebar',)+widget.bindtags())

        self.win.bind_class('titlebar','<ButtonPress-1>', self.start)
        self.win.bind_class('titlebar','<B1-Motion>', self.move)
        
    def geometry(self, x):
        self.win.geometry(x)
        self.after(5, lambda:self.configure(height=self.win.winfo_height()-32))
        
    def title(self, text):
        self.ttex.configure(text=text)
    def close(self, *args):
        self.win.destroy()
    def start(self,e):
        self.x,self.y= e.x,e.y
    def move(self,e):
        self.win.geometry("+%d+%d"%(e.x-self.x+self.win.winfo_x(),e.y-self.y+self.win.winfo_y()))        

class Gui(CTk):
    def __init__(self, fg_color: str | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.geometry('400x400')
        self.resizable(False,False)
        self.title('Wireless Draw Pad')
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.bind('<Control-w>', self.on_close)

        self.bt_state=1
        font = ('Arial', 18)
        menuFrame = CTkFrame(self, height=25)
        menuFrame.pack(side=TOP, fill='x', expand=False)
        Separator(self, orient='vertical',).pack(side=TOP, fill=X)
        CTkButton(menuFrame,width=50, corner_radius=5, fg_color="#242424",text="Add Port", command=self.add_port).pack(side=LEFT)
        CTkButton(menuFrame,width=50, corner_radius=5, fg_color="#242424",text="Tutorial", command=self.tutorial).pack(side=LEFT)

        frame = CTkFrame(self)
        frame.pack(expand=1)
        self.log = CTkLabel(master=frame,fg_color=None,text='Only on Mobile browser,\nhttp://'+ip+':'+str(port),font=font, text_color='yellow')
        self.log.pack(pady=15, padx=15)
        self.bt = CTkButton(master=frame, height=120, font=font, text='Stop', corner_radius=10, hover_color=None, command=self.bcommand)
        self.bt.pack(pady=15,anchor='ne', padx=40)

    def bcommand(self):
        if self.bt_state:
            self.bt.configure(text='Start', fg_color="#bd1f1f", hover_color="#8a0f0f")
            server.stop()
            self.bt_state = 0
        else:
            self.bt.configure(text='Stop', fg_color="#1F6AA5", hover_color="#144870")
            threading.Thread(target=server.start, args=()).start()
            self.bt_state = 1
    def on_close(self, *arg):
        self.destroy()
        server.stop()
    def add_port(self):
        tp = ToplevelWidget()
        tp.geometry("200x200+%d+%d"%(self.winfo_x()+100, self.winfo_y()+100))
        # tp.resizable(0,0)
        tp.title("Change Port")

        CTkFrame(tp,border_width=2).place()
        tp.bell()
        entry = CTkEntry(tp,placeholder_text="Enter Port")
        entry.place(relx=0.5, rely=0.45, anchor='s')
        entry._entry.focus()
        
        def setV(*arg):
            if entry.get():
                globals()['port'] = entry.get()
                self.log.configure(text=ip+':'+str(port))
            tp.win.destroy()
        entry.bind('<Return>', setV) #<Return> is for enter event
        CTkButton(tp,text="Enter",command = setV).place(relx=0.5, rely=0.5, anchor='n')
    def tutorial(self):
        tp = ToplevelWidget()
        tp.geometry("500x500+%d+%d"%(self.winfo_x()-50, self.winfo_y()-50))
        tp.title('Tutorial')
        tbox = CTkTextbox(tp, spacing2=10, font=('vrinda',15), wrap='word')
        tbox.place(relwidth=1, relheight=1)
        text ='''
একদম সহজ। চলো তোমার কম্পিউটারকে মোবাইল দিয়ে কনট্রোল করি মাত্র তিনটি ধাপে।

১। তোমার মোবাইল এবং কম্পিউটার একই নেটওয়ার্কে থাকতে হবে।

    ভালো হবে যদি উভয় ডিভাইস একই রাউটারে বা হটস্পটে কানেক্ট থাকে।

২। তোমার কম্পিউটার থেকে সফটওয়্যারটি শুরু করো।

৩। তোমার কম্পিউটার স্ক্রিনে যে নাম্বরটি আসবে তা তোমার মোবাইলে

    ব্রাউসারে লিখে ওয়েভসাইটে প্রবেশ করতে হবে। হ্যাঁ এতে কোনো

    ইন্টারনেট কাটবে না।
'''
        tbox.insert(INSERT,text)
        tbox.configure(state=DISABLED)

ip = gethostbyname(gethostname())
port = 8080

class Server(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args,**kw): pass #print('Closing')
            self.options['handler_class']=QuietHandler
        self.server = make_server(self.host, self.port, handler,**self.options)
        self.server.serve_forever()
    def stop(self):
        self.server.shutdown()
    def start(self):
        server_app.run(server=self, quiet=True)

draw =False
clicked = False

def mouse(x,y,):
    if draw==False:
        xC, yC = pyautogui.position()
        x,y = xC+x, yC+y
    
    pyautogui.moveTo(x,y)
    return

def screen_shot():
    byte_img = BytesIO()
    screen = pyautogui.screenshot()
    screen = screen.resize((w, h))
    screen.save(byte_img,'jpeg', quality = 80)
    byte_img.seek(0)
    return b64encode(byte_img.getvalue())

server_app = Bottle()
@server_app.route('/')
def go():
    return static_file('index.html', root='./HTML/')

@server_app.route('/<file>')
def serve(file):
    response.set_header('status', 200)
    return static_file(file, root='./HTML/')


@server_app.post('/catch/pos')
def data():
    if draw and not globals()['clicked']:
        pyautogui.mouseDown()
        globals()['clicked'] = True

    data = request.json
    x,y = data['value']
    print(x, y)
    threading.Thread(target=mouse, args=(x,y)).start()

@server_app.post('/catch/touchstart')
def touchstart():
    data = request.json
    x,y = data['value']
    pyautogui.moveTo(x, y)
    
@server_app.post('/catch/mousedown')
def mousedown():
    pyautogui.mouseDown()

@server_app.post('/catch/touchend')
def mouseup():
    pyautogui.mouseUp()
    globals()['clicked'] = False
    return screen_shot()


w, h = pyautogui.getInfo()[4]
h, w = h*round(800/w), 800
@server_app.post('/catch/drag/<drag:int>')
def drag_init(drag):
    if drag:
        globals()['draw'] = True
        response.set_header('Content-type', 'image/jpeg')
        return screen_shot()
    else:
        globals()['draw'] = False

@server_app.post('/catch/undo')
def undo():
    pyautogui.hotkey('ctrl', 'z')

@server_app.post('/catch/info')
def info():
    screen = pyautogui.getInfo()[4]
    response.set_header('Content-type', 'application/json; charset=utf-8')
    return f"[{screen.width}, {screen.height}]"






if __name__ == "__main__":
    app = Gui()
    server = Server(ip, port)
    threading.Thread(target=server.start, args=()).start()
    app.mainloop()