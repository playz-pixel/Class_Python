#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║        CHRONO AI - Quản Lý Thời Gian Thông Minh  v2.0      ║
║  • Đồng hồ thực với vòng Âm lịch  • Múi giờ toàn cầu      ║
║  • Lịch Dương + Âm  • Sự kiện / Nhắc việc AI-lite           ║
║  • Bản đồ múi giờ  • Thống kê thói quen  • Gamification     ║
╚══════════════════════════════════════════════════════════════╝
Yêu cầu: pip install PyQt5 pytz
"""

import sys, json, os, math, calendar
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

try:
    import pytz
    ALL_TZ = sorted(pytz.all_timezones)
    HAS_PYTZ = True
except ImportError:
    ALL_TZ = ["UTC","Asia/Ho_Chi_Minh","Asia/Bangkok","Asia/Tokyo","Asia/Shanghai",
              "Asia/Seoul","Asia/Singapore","Asia/Kolkata","Europe/London",
              "Europe/Paris","Europe/Berlin","America/New_York","America/Chicago",
              "America/Los_Angeles","America/Sao_Paulo","Australia/Sydney","Pacific/Auckland"]
    HAS_PYTZ = False

DATA_FILE = os.path.join(os.path.expanduser("~"), ".chrono_ai_v2.json")

# ═══════════════════════════════════════════════════════════════
#  ÂM LỊCH  (Ho Ngoc Duc Algorithm)
# ═══════════════════════════════════════════════════════════════
def _jd(d, m, y):
    a=(14-m)//12; yy=y+4800-a; mm=m+12*a-3
    j=d+(153*mm+2)//5+365*yy+yy//4-yy//100+yy//400-32045
    return j if j>=2299161 else d+(153*mm+2)//5+365*yy+yy//4-32083

def _new_moon(k):
    T=k/1236.85; T2=T*T; dr=math.pi/180
    jd=2415020.75933+29.53058868*k+0.0001178*T2
    jd+=0.00033*math.sin((166.56+132.87*T-0.009173*T2)*dr)
    M=(357.52910+35999.05030*T-0.0001559*T2)*dr
    Mpr=(306.0253+385.81691806*k+0.0107306*T2)*dr
    F=(21.2964+390.67050646*k-0.0016528*T2)*dr
    C=(0.1734-0.000393*T)*math.sin(M)+0.0021*math.sin(2*M)
    C-=0.4068*math.sin(Mpr)+0.0161*math.sin(2*Mpr)
    C+=0.0104*math.sin(2*F)-0.0051*math.sin(M+Mpr)
    C-=0.0074*math.sin(M-Mpr)+0.0010*math.sin(2*F-Mpr)+0.0005*math.sin(2*Mpr+M)
    return jd+C-(-0.000278+0.000265*T+0.000262*T2)

def _sun_lon(jd):
    T=(jd-2451545.0)/36525; dr=math.pi/180
    M=(357.52910+35999.05030*T-0.0001559*T*T)*dr
    L0=280.46645+36000.76983*T+0.0003032*T*T
    DL=(1.9146-0.004817*T)*math.sin(M)+(0.019993-0.000101*T)*math.sin(2*M)+0.00029*math.sin(3*M)
    L=(L0+DL)*dr
    return L-2*math.pi*int(L/(2*math.pi))

def _gsl(day, tz=7): return int(_sun_lon(day-0.5-tz/24)/math.pi*6)
def _gnm(k, tz=7): return int(_new_moon(k)+0.5+tz/24)

def _lm11(y, tz=7):
    k=int((_jd(31,12,y)-2415021)/29.530588853); nm=_gnm(k,tz)
    if _gsl(nm,tz)>=9: nm=_gnm(k-1,tz)
    return nm

def _lo(a11, tz=7):
    k=int((a11-2415021.076998695)/29.530588853+0.5); i=1
    arc=_gsl(_gnm(k+i,tz),tz)
    while True:
        last=arc; i+=1; arc=_gsl(_gnm(k+i,tz),tz)
        if arc==last or i>=14: break
    return i-1

def solar_to_lunar(d, m, y, tz=7):
    jd=_jd(d,m,y); k=int((jd-2415021.076998695)/29.530588853)
    ms=_gnm(k+1,tz)
    if ms>jd: ms=_gnm(k,tz)
    a11=_lm11(y,tz); b11=a11
    if a11>=ms: ly=y; a11=_lm11(y-1,tz)
    else: ly=y+1; b11=_lm11(y+1,tz)
    ld=jd-ms+1; diff=int((ms-a11)/29); leap=False; lm=diff+11
    if b11-a11>365:
        lo=_lo(a11,tz)
        if diff>=lo: lm=diff+10
        if diff==lo: leap=True
    if lm>12: lm-=12
    if lm>=11 and diff<4: ly-=1
    return int(ld),int(lm),int(ly),leap

CAN=["Giáp","Ất","Bính","Đinh","Mậu","Kỷ","Canh","Tân","Nhâm","Quý"]
CHI=["Tý","Sửu","Dần","Mão","Thìn","Tị","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
MONTHS_AL=["Giêng","Hai","Ba","Tư","Năm","Sáu","Bảy","Tám","Chín","Mười","M.Một","Chạp"]
MONTHS_DL=["Tháng 1","Tháng 2","Tháng 3","Tháng 4","Tháng 5","Tháng 6",
           "Tháng 7","Tháng 8","Tháng 9","Tháng 10","Tháng 11","Tháng 12"]
DAYS_VI=["T2","T3","T4","T5","T6","T7","CN"]
def can_chi(y): return f"{CAN[(y-4)%10]} {CHI[(y-4)%12]}"
def thu_vi(wd): return ["Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ Nhật"][wd]

HOLIDAYS={(1,1):"Tết Dương lịch",(4,30):"Giải phóng Miền Nam",
          (5,1):"Quốc tế Lao động",(9,2):"Quốc khánh Việt Nam",
          (12,25):"Giáng sinh",(3,8):"Quốc tế Phụ nữ",
          (11,20):"Ngày Nhà giáo VN",(6,1):"Thiếu nhi Quốc tế",(10,20):"Phụ nữ Việt Nam"}

ZODIAC_DATA=[("Bạch Dương ♈",3,21),("Kim Ngưu ♉",4,20),("Song Tử ♊",5,21),
             ("Cự Giải ♋",6,21),("Sư Tử ♌",7,23),("Xử Nữ ♍",8,23),
             ("Thiên Bình ♎",9,23),("Bọ Cạp ♏",10,23),("Nhân Mã ♐",11,22),
             ("Ma Kết ♑",12,22),("Bảo Bình ♒",1,20),("Song Ngư ♓",2,19)]

WORLD_TZ=[
    ("🇻🇳 Việt Nam","Asia/Ho_Chi_Minh"),("🇹🇭 Bangkok","Asia/Bangkok"),
    ("🇸🇬 Singapore","Asia/Singapore"),("🇯🇵 Tokyo","Asia/Tokyo"),
    ("🇨🇳 Bắc Kinh","Asia/Shanghai"),("🇰🇷 Seoul","Asia/Seoul"),
    ("🇮🇳 Mumbai","Asia/Kolkata"),("🇦🇪 Dubai","Asia/Dubai"),
    ("🇩🇪 Berlin","Europe/Berlin"),("🇫🇷 Paris","Europe/Paris"),
    ("🇬🇧 London","Europe/London"),("🇷🇺 Moscow","Europe/Moscow"),
    ("🇺🇸 New York","America/New_York"),("🇺🇸 Chicago","America/Chicago"),
    ("🇺🇸 LA","America/Los_Angeles"),("🇨🇦 Toronto","America/Toronto"),
    ("🇧🇷 São Paulo","America/Sao_Paulo"),("🇦🇺 Sydney","Australia/Sydney"),
    ("🇳🇿 Auckland","Pacific/Auckland"),("🌐 UTC","UTC"),
]

AI_KEYWORDS={
    "sáng sớm":"05:30","buổi sáng":"08:00","trưa":"12:00",
    "chiều":"14:00","tối":"19:00","tối nay":"20:00","đêm":"22:00",
    "học bài":"20:00","họp":"09:00","ăn tối":"18:30","ăn sáng":"07:00",
    "thể dục":"06:00","chạy bộ":"06:00","tập gym":"17:30","ngủ":"22:30"
}

# ═══════════════════════════════════════════════════════════════
#  DATA MANAGER
# ═══════════════════════════════════════════════════════════════
class DM:
    def __init__(self):
        self.d={"events":[],"sets":{"theme":"dark","fmt":"24",
            "tz":"Asia/Ho_Chi_Minh","lunar":True,"acc":"#00d4ff","sound":True},
            "game":{"pts":0,"streak":0,"last":"","done":0},
            "fav":["Asia/Ho_Chi_Minh","America/New_York","Europe/London","Asia/Tokyo"]}
        self.load()

    def load(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE,'r',encoding='utf-8') as f:
                    saved=json.load(f)
                    for k,v in saved.items():
                        if isinstance(v,dict) and isinstance(self.d.get(k),dict): self.d[k].update(v)
                        else: self.d[k]=v
        except: pass

    def save(self):
        try:
            with open(DATA_FILE,'w',encoding='utf-8') as f:
                json.dump(self.d,f,ensure_ascii=False,indent=2)
        except: pass

    def S(self,k,dv=None): return self.d["sets"].get(k,dv)
    def sS(self,k,v): self.d["sets"][k]=v; self.save()
    def events(self): return self.d.get("events",[])
    def add_ev(self,e): self.d["events"].append(e); self.save()
    def del_ev(self,i):
        if 0<=i<len(self.d["events"]): self.d["events"].pop(i); self.save()
    def toggle_done(self,i):
        if 0<=i<len(self.d["events"]):
            self.d["events"][i]["done"]=not self.d["events"][i].get("done",False)
            if self.d["events"][i]["done"]: self.complete_task()
            else: self.save()
    def get_game(self): return self.d.get("game",{})
    def fav_tz(self): return self.d.get("fav",[])
    def add_fav(self,tz):
        if tz not in self.d["fav"]: self.d["fav"].append(tz); self.save()
    def del_fav(self,tz):
        if tz in self.d["fav"]: self.d["fav"].remove(tz); self.save()

    def complete_task(self):
        g=self.d["game"]; t=datetime.now().strftime("%Y-%m-%d")
        y=(datetime.now()-timedelta(1)).strftime("%Y-%m-%d")
        if g.get("last")!=t:
            g["streak"]=(g.get("streak",0)+1) if g.get("last")==y else 1
            g["last"]=t
        g["done"]=g.get("done",0)+1; g["pts"]=g.get("pts",0)+10; self.save()
        return g["pts"],g["streak"]

# ═══════════════════════════════════════════════════════════════
#  THEME ENGINE
# ═══════════════════════════════════════════════════════════════
DARK={"bg":"#07091a","bg2":"#0d1428","card":"#0f172a","card2":"#1a2340",
      "acc":"#00d4ff","acc2":"#4f46e5","txt":"#e2e8f0","txt2":"#94a3b8",
      "txt3":"#475569","ok":"#10b981","warn":"#f59e0b","err":"#ef4444",
      "bdr":"#1e3a5f","hov":"#162035"}
LITE={"bg":"#f0f4f8","bg2":"#dde3ed","card":"#ffffff","card2":"#f1f5f9",
      "acc":"#0284c7","acc2":"#4f46e5","txt":"#0f172a","txt2":"#475569",
      "txt3":"#94a3b8","ok":"#059669","warn":"#d97706","err":"#dc2626",
      "bdr":"#c4cfda","hov":"#dbeafe"}
ACCENT_MAP={"Cyan":"#00d4ff","Xanh":"#3b82f6","Tím":"#8b5cf6",
            "Hồng":"#ec4899","Cam":"#f97316","Xanh lá":"#10b981"}

def get_qss(T, acc):
    T=dict(T); T["acc"]=acc
    return f"""
QMainWindow {{ background:{T['bg']}; }}
QWidget {{ background:transparent; color:{T['txt']}; font-family:'Segoe UI',Arial,sans-serif; }}
QScrollBar:vertical {{ background:{T['bg2']}; width:5px; border-radius:3px; }}
QScrollBar::handle:vertical {{ background:{T['acc']}; border-radius:3px; min-height:20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QScrollBar:horizontal {{ background:{T['bg2']}; height:5px; border-radius:3px; }}
QScrollBar::handle:horizontal {{ background:{T['acc']}; border-radius:3px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0; }}
QPushButton {{ background:{T['card2']}; color:{T['txt']}; border:1px solid {T['bdr']};
    border-radius:8px; padding:8px 16px; font-size:13px; font-weight:500; }}
QPushButton:hover {{ background:{T['hov']}; border-color:{T['acc']}; color:{T['acc']}; }}
QPushButton:pressed {{ background:{T['acc']}; color:#000; }}
QPushButton:disabled {{ color:{T['txt3']}; }}
QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {{
    background:{T['card2']}; color:{T['txt']}; border:1px solid {T['bdr']};
    border-radius:8px; padding:6px 10px; font-size:13px; }}
QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus {{ border-color:{T['acc']}; }}
QComboBox::drop-down {{ border:none; width:22px; }}
QComboBox QAbstractItemView {{ background:{T['card']}; color:{T['txt']}; border:1px solid {T['bdr']};
    selection-background-color:{T['acc']}; selection-color:#000; }}
QListWidget {{ background:{T['card']}; border:1px solid {T['bdr']}; border-radius:10px; outline:none; padding:4px; }}
QListWidget::item {{ padding:10px 12px; border-radius:6px; margin:1px; }}
QListWidget::item:selected {{ background:{T['acc']}; color:#000; }}
QListWidget::item:hover:!selected {{ background:{T['hov']}; }}
QCheckBox {{ spacing:8px; color:{T['txt']}; }}
QCheckBox::indicator {{ width:17px; height:17px; border-radius:4px; border:2px solid {T['bdr']}; background:{T['card2']}; }}
QCheckBox::indicator:checked {{ background:{T['acc']}; border-color:{T['acc']}; }}
QGroupBox {{ border:1px solid {T['bdr']}; border-radius:10px; margin-top:14px; padding-top:10px; }}
QGroupBox::title {{ subcontrol-origin:margin; left:12px; padding:0 6px;
    color:{T['acc']}; font-weight:bold; font-size:12px; }}
QDialog {{ background:{T['card']}; }}
QMessageBox {{ background:{T['card']}; }} QMessageBox QLabel {{ color:{T['txt']}; }}
QTabWidget::pane {{ border:1px solid {T['bdr']}; border-radius:8px; }}
QTabBar::tab {{ background:{T['card2']}; color:{T['txt2']}; padding:8px 16px; border-radius:6px; margin:2px; }}
QTabBar::tab:selected {{ background:{T['acc']}; color:#000; font-weight:bold; }}
"""

# ═══════════════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════
class Card(QFrame):
    def __init__(self, parent=None, r=12, border=True):
        super().__init__(parent)
        self._r=r; self._border=border; self.T=DARK
    def set_theme(self, T): self.T=T; self.update()
    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        rect=QRectF(self.rect()).adjusted(0.5,0.5,-0.5,-0.5)
        p.setBrush(QColor(self.T["card"]))
        p.setPen(QPen(QColor(self.T["bdr"]),1) if self._border else Qt.NoPen)
        p.drawRoundedRect(rect,self._r,self._r)


class AccentBtn(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._T=DARK; self._acc="#00d4ff"
    def set_theme(self, T, acc): self._T=T; self._acc=acc; self.update()
    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        col=QColor(self._acc)
        if self.underMouse(): col=col.lighter(115)
        p.setBrush(col); p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(self.rect()),8,8)
        p.setPen(QColor("#000"))
        f=p.font(); f.setPointSize(12); f.setBold(True); p.setFont(f)
        p.drawText(self.rect(),Qt.AlignCenter,self.text())


class NavBtn(QAbstractButton):
    def __init__(self, icon, label, parent=None):
        super().__init__(parent)
        self._icon=icon; self._label=label; self.T=DARK; self._acc="#00d4ff"
        self.setCheckable(True); self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
    def set_theme(self, T, acc): self.T=T; self._acc=acc; self.update()
    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        chk=self.isChecked(); hov=self.underMouse() and not chk
        if chk:
            p.setBrush(QColor(self._acc)); p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(self.rect()).adjusted(4,2,-4,-2),8,8)
        elif hov:
            p.setBrush(QColor(self.T["hov"])); p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(self.rect()).adjusted(4,2,-4,-2),8,8)
        f=p.font()
        # icon
        f.setPointSize(17); p.setFont(f)
        p.setPen(QColor("#000" if chk else (self._acc if hov else self.T["txt2"])))
        p.drawText(QRect(0,0,52,50), Qt.AlignCenter, self._icon)
        # label
        f.setPointSize(12); f.setBold(chk); p.setFont(f)
        p.setPen(QColor("#000" if chk else (self.T["txt"] if hov else self.T["txt2"])))
        p.drawText(QRect(52,0,self.width()-56,50), Qt.AlignVCenter|Qt.AlignLeft, self._label)
    def sizeHint(self): return QSize(220,50)
    def enterEvent(self,e): self.update()
    def leaveEvent(self,e): self.update()


class GlowLabel(QLabel):
    """Label with optional glow effect"""
    def __init__(self, text="", parent=None, glow=True):
        super().__init__(text, parent)
        self._glow=glow; self._acc="#00d4ff"
    def set_acc(self, acc): self._acc=acc; self.update()
    def paintEvent(self, e):
        if not self._glow: return super().paintEvent(e)
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setFont(self.font())
        if self._glow:
            shadow=QColor(self._acc); shadow.setAlpha(60)
            for off in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1)]:
                p.setPen(shadow)
                p.drawText(self.rect().adjusted(off[0],off[1],off[0],off[1]),
                           self.alignment(),self.text())
        p.setPen(QColor(self._acc if self._glow else self.palette().text().color()))
        p.drawText(self.rect(),self.alignment(),self.text())


# ═══════════════════════════════════════════════════════════════
#  ANALOG CLOCK RING WIDGET
# ═══════════════════════════════════════════════════════════════
class ClockRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._s=0; self._m=0; self._h=0; self.T=DARK; self._acc="#00d4ff"
        self.setMinimumSize(240,240); self.setMaximumSize(300,300)
    def set_theme(self, T, acc): self.T=T; self._acc=acc; self.update()
    def set_time(self, h, m, s): self._h=h; self._m=m; self._s=s; self.update()
    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w=self.width(); h=self.height(); cx=w//2; cy=h//2; R=min(w,h)//2-6
        # BG circle
        p.setBrush(QColor(self.T["card"])); p.setPen(Qt.NoPen)
        p.drawEllipse(cx-R,cy-R,2*R,2*R)
        # Track
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(self.T["bdr"]),4,Qt.SolidLine,Qt.RoundCap))
        p.drawEllipse(cx-R+8,cy-R+8,2*(R-8),2*(R-8))
        # Second arc
        sec_a=int(self._s/60*360*16)
        c=QColor(self._acc); pen=QPen(c,5,Qt.SolidLine,Qt.RoundCap)
        p.setPen(pen); p.drawArc(cx-R+8,cy-R+8,2*(R-8),2*(R-8),90*16,-sec_a)
        # Minute arc (inner)
        R2=R-20
        min_a=int((self._m+self._s/60)/60*360*16)
        c2=QColor(self.T["acc2"]); c2.setAlpha(180)
        p.setPen(QPen(c2,3,Qt.SolidLine,Qt.RoundCap))
        p.drawArc(cx-R2+8,cy-R2+8,2*(R2-8),2*(R2-8),90*16,-min_a)
        # Hour markers
        for i in range(60):
            ang=math.radians(i*6-90)
            is_hr=(i%5==0)
            r1=R-3; r2=R-(10 if is_hr else 5)
            col=self._acc if is_hr and (i*6<=self._m*6+self._s*0.1) else (self.T["txt"] if is_hr else self.T["bdr"])
            p.setPen(QPen(QColor(col),2.5 if is_hr else 1))
            p.drawLine(int(cx+r2*math.cos(ang)),int(cy+r2*math.sin(ang)),
                       int(cx+r1*math.cos(ang)),int(cy+r1*math.sin(ang)))
        # Center
        p.setPen(Qt.NoPen); p.setBrush(QColor(self._acc))
        p.drawEllipse(cx-5,cy-5,10,10)
        p.setBrush(QColor(self.T["bg"])); p.drawEllipse(cx-2,cy-2,4,4)


# ═══════════════════════════════════════════════════════════════
#  PAGE: CLOCK
# ═══════════════════════════════════════════════════════════════
class ClockPage(QWidget):
    def __init__(self, dm):
        super().__init__(); self.dm=dm; self.T=DARK; self._acc="#00d4ff"
        self._init_ui()

    def _init_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(20)
        # Top section
        top=QHBoxLayout(); top.setAlignment(Qt.AlignCenter); top.setSpacing(30)
        self.ring=ClockRing()
        top.addWidget(self.ring)
        digi=QVBoxLayout(); digi.setSpacing(6)
        self.lbl_time=GlowLabel("00:00:00"); self.lbl_time.setAlignment(Qt.AlignCenter)
        f=self.lbl_time.font(); f.setPointSize(52); f.setBold(True); f.setFamily("Courier New"); self.lbl_time.setFont(f)
        self.lbl_date=QLabel(); self.lbl_date.setAlignment(Qt.AlignCenter)
        f2=self.lbl_date.font(); f2.setPointSize(14); self.lbl_date.setFont(f2)
        self.lbl_lunar=QLabel(); self.lbl_lunar.setAlignment(Qt.AlignCenter)
        f3=self.lbl_lunar.font(); f3.setPointSize(12); self.lbl_lunar.setFont(f3)
        self.lbl_canchi=QLabel(); self.lbl_canchi.setAlignment(Qt.AlignCenter)
        f4=self.lbl_canchi.font(); f4.setPointSize(11); self.lbl_canchi.setFont(f4)
        self.lbl_tz=QLabel(); self.lbl_tz.setAlignment(Qt.AlignCenter)
        for w in [self.lbl_time,self.lbl_date,self.lbl_lunar,self.lbl_canchi,self.lbl_tz]:
            digi.addWidget(w)
        digi.addStretch(); top.addLayout(digi); root.addLayout(top)
        # Info cards
        row=QHBoxLayout(); row.setSpacing(12)
        self.info_cards=[]
        for icon,lbl in [("📅","Tuần"),("🗓️","Ngày/Năm"),("🎉","Ngày lễ"),("✨","Cung HĐ"),("🌙","Ngày tốt")]:
            card=Card(); card.setFixedHeight(95)
            v=QVBoxLayout(card); v.setContentsMargins(10,8,10,8); v.setSpacing(2)
            li=QLabel(icon); li.setAlignment(Qt.AlignCenter)
            fi=li.font(); fi.setPointSize(18); li.setFont(fi)
            ll=QLabel(lbl); ll.setAlignment(Qt.AlignCenter)
            fl=ll.font(); fl.setPointSize(9); ll.setFont(fl)
            lv=QLabel("—"); lv.setAlignment(Qt.AlignCenter); lv.setObjectName("val")
            fv=lv.font(); fv.setPointSize(11); fv.setBold(True); lv.setFont(fv)
            v.addWidget(li); v.addWidget(ll); v.addWidget(lv)
            self.info_cards.append((card,lv)); row.addWidget(card)
        root.addLayout(row); root.addStretch()

    def update_clock(self):
        now=datetime.now()
        fmt=self.dm.S("fmt","24")
        if fmt=="24": ts=now.strftime("%H:%M:%S")
        else:
            h=now.hour%12 or 12
            ts=f"{h:02d}:{now.minute:02d}:{now.second:02d} {'SA' if now.hour<12 else 'CH'}"
        self.lbl_time.setText(ts)
        self.lbl_date.setText(f"{thu_vi(now.weekday())}, {now.day:02d}/{now.month:02d}/{now.year}")
        if self.dm.S("lunar",True):
            ld,lm,ly,leap=solar_to_lunar(now.day,now.month,now.year)
            self.lbl_lunar.setText(f"🌙 {ld} tháng {MONTHS_AL[lm-1]}{'(Nhuận)' if leap else ''} ÂL")
            self.lbl_canchi.setText(f"⭐ Năm {can_chi(ly)}")
        else: self.lbl_lunar.setText(""); self.lbl_canchi.setText("")
        self.lbl_tz.setText(f"🌐 {self.dm.S('tz','Asia/Ho_Chi_Minh')}")
        self.ring.set_time(now.hour,now.minute,now.second)
        # Info cards
        vals=[f"Tuần {now.isocalendar()[1]}",
              f"Ngày {now.timetuple().tm_yday}/365",
              HOLIDAYS.get((now.month,now.day),"—"),
              self._zodiac(now),self._good_day(now)]
        for i,(card,lv) in enumerate(self.info_cards):
            lv.setText(vals[i])

    def _zodiac(self, now):
        z="Song Ngư ♓"
        for name,sm,sd in ZODIAC_DATA:
            if now.month>sm or (now.month==sm and now.day>=sd): z=name
        return z

    def _good_day(self, now):
        ld,lm,ly,_=solar_to_lunar(now.day,now.month,now.year)
        good=[1,3,6,7,10,13,17,20,23,26,27,30]
        return "✅ Ngày tốt" if ld in good else "⬜ Bình thường"

    def set_theme(self, T, acc):
        self.T=T; self._acc=acc
        self.ring.set_theme(T,acc)
        self.lbl_time.set_acc(acc)
        self.lbl_time.setStyleSheet(f"background:transparent;")
        self.lbl_date.setStyleSheet(f"color:{T['txt']}; background:transparent; font-weight:600;")
        self.lbl_lunar.setStyleSheet(f"color:{T['ok']}; background:transparent;")
        self.lbl_canchi.setStyleSheet(f"color:{T['txt2']}; background:transparent;")
        self.lbl_tz.setStyleSheet(f"color:{T['txt3']}; background:transparent; font-size:12px;")
        for card,lv in self.info_cards:
            card.set_theme(T); lv.setStyleSheet(f"color:{acc}; background:transparent;")


# ═══════════════════════════════════════════════════════════════
#  PAGE: TIMEZONE
# ═══════════════════════════════════════════════════════════════
class TZPage(QWidget):
    def __init__(self, dm):
        super().__init__(); self.dm=dm; self.T=DARK; self._acc="#00d4ff"; self._init_ui()

    def _init_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(16)
        # Search + add
        row=QHBoxLayout(); row.setSpacing(10)
        self.search=QLineEdit(); self.search.setPlaceholderText("🔍 Tìm múi giờ...")
        self.combo=QComboBox(); self.combo.addItems(ALL_TZ); self.combo.setMaximumWidth(260)
        btn_add=QPushButton("+ Thêm")
        btn_add.clicked.connect(self._add_fav)
        self.search.textChanged.connect(self._filter)
        row.addWidget(self.search,2); row.addWidget(self.combo,2); row.addWidget(btn_add)
        root.addLayout(row)
        # Splitter
        spl=QSplitter(Qt.Horizontal)
        # Favorites
        fav_w=QWidget(); fav_v=QVBoxLayout(fav_w); fav_v.setContentsMargins(0,0,0,0); fav_v.setSpacing(8)
        lf=QLabel("⭐ Yêu thích"); lf.setStyleSheet("font-weight:bold; font-size:14px;")
        fav_v.addWidget(lf)
        self.fav_list=QListWidget(); fav_v.addWidget(self.fav_list)
        btn_del=QPushButton("🗑 Xóa"); btn_del.clicked.connect(self._del_fav)
        fav_v.addWidget(btn_del)
        spl.addWidget(fav_w)
        # World list
        world_w=QWidget(); world_v=QVBoxLayout(world_w); world_v.setContentsMargins(0,0,0,0); world_v.setSpacing(8)
        lw=QLabel("🌍 Thế giới"); lw.setStyleSheet("font-weight:bold; font-size:14px;")
        world_v.addWidget(lw)
        self.world_list=QListWidget(); world_v.addWidget(self.world_list)
        spl.addWidget(world_w)
        spl.setSizes([400,400])
        root.addWidget(spl)
        # Converter
        conv=Card(); conv_v=QVBoxLayout(conv); conv_v.setSpacing(8)
        lc=QLabel("🔄 Chuyển đổi múi giờ"); lc.setStyleSheet("font-weight:bold;")
        conv_v.addWidget(lc)
        hh=QHBoxLayout(); hh.setSpacing(10)
        self.from_tz=QComboBox(); self.from_tz.addItems(ALL_TZ)
        idx=self.from_tz.findText("Asia/Ho_Chi_Minh"); self.from_tz.setCurrentIndex(max(idx,0))
        self.to_tz=QComboBox(); self.to_tz.addItems(ALL_TZ)
        idx2=self.to_tz.findText("America/New_York"); self.to_tz.setCurrentIndex(max(idx2,0))
        self.from_time=QTimeEdit(QTime.currentTime()); self.from_time.setDisplayFormat("HH:mm")
        self.result_lbl=QLabel("—"); self.result_lbl.setStyleSheet("font-size:18px; font-weight:bold;")
        btn_conv=QPushButton("Chuyển →"); btn_conv.clicked.connect(self._convert)
        hh.addWidget(self.from_tz); hh.addWidget(self.from_time)
        hh.addWidget(QLabel("→")); hh.addWidget(self.to_tz)
        hh.addWidget(btn_conv); hh.addWidget(self.result_lbl)
        conv_v.addLayout(hh); self.conv_card=conv; root.addWidget(conv)

    def refresh(self):
        self.fav_list.clear()
        for tz in self.dm.fav_tz():
            t=self._get_time(tz)
            item=QListWidgetItem(f"  {tz.split('/')[-1].replace('_',' ')}  —  {t}  ({tz})")
            self.fav_list.addItem(item)
        self.world_list.clear()
        q=self.search.text().lower()
        for flag,tz in WORLD_TZ:
            t=self._get_time(tz)
            name=tz.split("/")[-1].replace("_"," ")
            if q and q not in name.lower() and q not in tz.lower(): continue
            item=QListWidgetItem(f"  {flag} {name}   {t}")
            self.world_list.addItem(item)

    def _get_time(self, tz_name):
        try:
            if HAS_PYTZ:
                tz=pytz.timezone(tz_name)
                t=datetime.now(tz)
                fmt=self.dm.S("fmt","24")
                return t.strftime("%H:%M:%S" if fmt=="24" else "%I:%M %p")+" "+t.strftime("%Z")
            else:
                import time as _time
                return datetime.utcnow().strftime("%H:%M")+" UTC"
        except: return "—"

    def _add_fav(self):
        tz=self.combo.currentText()
        if tz: self.dm.add_fav(tz); self.refresh()

    def _del_fav(self):
        item=self.fav_list.currentItem()
        if not item: return
        text=item.text()
        tz=text.split("(")[-1].rstrip(")")
        self.dm.del_fav(tz.strip()); self.refresh()

    def _filter(self): self.refresh()

    def _convert(self):
        try:
            ft=self.from_time.time(); h=ft.hour(); m=ft.minute()
            if HAS_PYTZ:
                from_tz=pytz.timezone(self.from_tz.currentText())
                to_tz=pytz.timezone(self.to_tz.currentText())
                now=datetime.now()
                dt=now.replace(hour=h,minute=m,second=0)
                dt_from=from_tz.localize(dt)
                dt_to=dt_from.astimezone(to_tz)
                self.result_lbl.setText(dt_to.strftime("%H:%M (%Z)"))
            else: self.result_lbl.setText("Cần pytz")
        except Exception as ex: self.result_lbl.setText("Lỗi")

    def set_theme(self, T, acc):
        self.T=T; self._acc=acc
        self.conv_card.set_theme(T)
        self.result_lbl.setStyleSheet(f"font-size:18px; font-weight:bold; color:{acc}; background:transparent;")


# ═══════════════════════════════════════════════════════════════
#  PAGE: CALENDAR
# ═══════════════════════════════════════════════════════════════
class CalPage(QWidget):
    def __init__(self, dm):
        super().__init__(); self.dm=dm; self.T=DARK; self._acc="#00d4ff"
        self._year=datetime.now().year; self._month=datetime.now().month
        self._cells=[]; self._init_ui()

    def _init_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(12)
        # Header
        hdr=QHBoxLayout()
        self.btn_prev=QPushButton("◀"); self.btn_prev.setFixedWidth(50)
        self.btn_prev.clicked.connect(self._prev)
        self.lbl_month=QLabel(); self.lbl_month.setAlignment(Qt.AlignCenter)
        f=self.lbl_month.font(); f.setPointSize(16); f.setBold(True); self.lbl_month.setFont(f)
        self.btn_next=QPushButton("▶"); self.btn_next.setFixedWidth(50)
        self.btn_next.clicked.connect(self._next)
        self.btn_today=QPushButton("Hôm nay"); self.btn_today.clicked.connect(self._go_today)
        hdr.addWidget(self.btn_prev); hdr.addWidget(self.lbl_month,1)
        hdr.addWidget(self.btn_today); hdr.addWidget(self.btn_next)
        root.addLayout(hdr)
        # Day headers
        days_w=QWidget(); days_grid=QGridLayout(days_w); days_grid.setSpacing(4)
        for i,d in enumerate(DAYS_VI):
            l=QLabel(d); l.setAlignment(Qt.AlignCenter)
            f=l.font(); f.setBold(True); f.setPointSize(11); l.setFont(f)
            if i>=5: l.setStyleSheet(f"color:#ef4444; background:transparent;")
            days_grid.addWidget(l,0,i)
        root.addWidget(days_w)
        # Grid
        self.grid_w=QWidget(); self.grid=QGridLayout(self.grid_w)
        self.grid.setSpacing(4)
        self._cells=[]
        for r in range(6):
            row_cells=[]
            for c in range(7):
                cell=self._make_cell()
                self.grid.addWidget(cell,r,c)
                row_cells.append(cell)
            self._cells.append(row_cells)
        root.addWidget(self.grid_w)
        # Event preview
        self.ev_label=QLabel("Nhấp vào ngày để xem sự kiện")
        self.ev_label.setWordWrap(True); self.ev_label.setContentsMargins(4,0,4,0)
        root.addWidget(self.ev_label)
        self._refresh_cal()

    def _make_cell(self):
        cell=QFrame(); cell.setMinimumSize(50,56)
        cell.setCursor(Qt.PointingHandCursor)
        v=QVBoxLayout(cell); v.setContentsMargins(4,4,4,4); v.setSpacing(0)
        solar=QLabel(); solar.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
        fs=solar.font(); fs.setPointSize(13); fs.setBold(True); solar.setFont(fs)
        lunar=QLabel(); lunar.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)
        fl=lunar.font(); fl.setPointSize(8); lunar.setFont(fl)
        solar.setObjectName("solar"); lunar.setObjectName("lunar")
        v.addWidget(solar); v.addWidget(lunar)
        return cell

    def _refresh_cal(self):
        self.lbl_month.setText(f"{MONTHS_DL[self._month-1]} / {self._year}")
        first_day=calendar.monthrange(self._year,self._month)[0]
        days_in_month=calendar.monthrange(self._year,self._month)[1]
        today=datetime.now()
        events_by_date={}
        for ev in self.dm.events():
            try:
                ed=datetime.strptime(ev["date"],"%Y-%m-%d")
                key=(ed.year,ed.month,ed.day)
                events_by_date.setdefault(key,[]).append(ev["title"])
            except: pass
        day=1
        for r in range(6):
            for c in range(7):
                cell=self._cells[r][c]
                solar=cell.findChild(QLabel,"solar")
                lunar=cell.findChild(QLabel,"lunar")
                col=c
                if r==0 and col<first_day or day>days_in_month:
                    solar.setText(""); lunar.setText("")
                    cell.setStyleSheet(f"background:transparent; border:none;")
                    cell.mousePressEvent=lambda e,d=None: None
                else:
                    d=day
                    is_today=(d==today.day and self._month==today.month and self._year==today.year)
                    is_weekend=(col>=5)
                    is_holiday=(self._month,d) in HOLIDAYS
                    ld,lm,ly,_=solar_to_lunar(d,self._month,self._year)
                    has_event=(self._year,self._month,d) in events_by_date
                    solar.setText(str(d)); lunar.setText(f"{ld}/{lm}")
                    # Styling
                    if is_today:
                        bg=self._acc; tc="#000"; lc="#000"
                    elif is_holiday:
                        bg=QColor(self.T["err"]).name(); tc="#fff"; lc="#ffcccc"
                    elif is_weekend:
                        bg=self.T["card2"]; tc=self.T["err"]; lc=self.T["txt3"]
                    else:
                        bg=self.T["card"]; tc=self.T["txt"]; lc=self.T["txt3"]
                    ev_dot="•" if has_event else ""
                    solar.setText(str(d)+ev_dot)
                    solar.setStyleSheet(f"color:{tc}; background:transparent; font-weight:{'bold' if is_today else '600'};")
                    lunar.setStyleSheet(f"color:{lc}; background:transparent;")
                    cell.setStyleSheet(f"background:{bg}; border-radius:8px; border:{'2px solid '+self._acc if is_today else '1px solid '+self.T['bdr']};")
                    def on_click(ev, dd=d, mm=self._month, yy=self._year, evd=events_by_date):
                        evs=evd.get((yy,mm,dd),[])
                        ld2,lm2,ly2,_=solar_to_lunar(dd,mm,yy)
                        txt=f"📅 {dd}/{mm}/{yy} — ÂL: {ld2}/{lm2} — {can_chi(ly2)}"
                        h=(mm,dd)
                        if h in HOLIDAYS: txt+=f"\n🎉 {HOLIDAYS[h]}"
                        if evs: txt+="\n📌 Sự kiện: "+", ".join(evs)
                        self.ev_label.setText(txt)
                    cell.mousePressEvent=on_click
                    day+=1

    def _prev(self):
        self._month-=1
        if self._month<1: self._month=12; self._year-=1
        self._refresh_cal()
    def _next(self):
        self._month+=1
        if self._month>12: self._month=1; self._year+=1
        self._refresh_cal()
    def _go_today(self):
        now=datetime.now(); self._year=now.year; self._month=now.month; self._refresh_cal()

    def set_theme(self, T, acc):
        self.T=T; self._acc=acc; self._refresh_cal()
        self.ev_label.setStyleSheet(f"color:{T['txt2']}; background:{T['card']}; border-radius:8px; padding:8px; font-size:12px;")


# ═══════════════════════════════════════════════════════════════
#  DIALOG: ADD EVENT
# ═══════════════════════════════════════════════════════════════
class AddEventDialog(QDialog):
    def __init__(self, dm, parent=None):
        super().__init__(parent); self.dm=dm; self.T=DARK; self._acc="#00d4ff"
        self.setWindowTitle("Thêm sự kiện"); self.setMinimumWidth(440)
        self.result_ev=None; self._init_ui()

    def _init_ui(self):
        v=QVBoxLayout(self); v.setSpacing(12); v.setContentsMargins(20,20,20,20)
        v.addWidget(QLabel("📋 Thêm Sự Kiện / Nhắc Việc"))
        self.title_e=QLineEdit(); self.title_e.setPlaceholderText("Tiêu đề sự kiện...")
        self.title_e.textChanged.connect(self._ai_suggest)
        v.addWidget(self.title_e)
        self.ai_lbl=QLabel(); self.ai_lbl.setWordWrap(True)
        v.addWidget(self.ai_lbl)
        row=QHBoxLayout(); row.setSpacing(10)
        self.date_e=QDateEdit(QDate.currentDate()); self.date_e.setCalendarPopup(True)
        self.date_e.setDisplayFormat("dd/MM/yyyy")
        self.time_e=QTimeEdit(QTime.currentTime()); self.time_e.setDisplayFormat("HH:mm")
        row.addWidget(QLabel("📅")); row.addWidget(self.date_e)
        row.addWidget(QLabel("⏰")); row.addWidget(self.time_e)
        v.addLayout(row)
        row2=QHBoxLayout(); row2.setSpacing(10)
        self.cat_cb=QComboBox()
        self.cat_cb.addItems(["📌 Công việc","🎓 Học tập","🏃 Thể thao","👨‍👩‍👧 Gia đình","🎉 Cá nhân","💊 Sức khỏe"])
        self.repeat_cb=QComboBox()
        self.repeat_cb.addItems(["Không lặp","Hàng ngày","Hàng tuần","Hàng tháng"])
        row2.addWidget(QLabel("Loại:")); row2.addWidget(self.cat_cb)
        row2.addWidget(QLabel("Lặp:")); row2.addWidget(self.repeat_cb)
        v.addLayout(row2)
        self.note_e=QTextEdit(); self.note_e.setPlaceholderText("Ghi chú...")
        self.note_e.setFixedHeight(60)
        v.addWidget(self.note_e)
        self.reminder_cb=QCheckBox("Nhắc trước 15 phút")
        v.addWidget(self.reminder_cb)
        btns=QHBoxLayout()
        ok=QPushButton("✅ Lưu"); ok.clicked.connect(self._save)
        cancel=QPushButton("Hủy"); cancel.clicked.connect(self.reject)
        btns.addWidget(cancel); btns.addWidget(ok)
        v.addLayout(btns)

    def _ai_suggest(self, text):
        text_l=text.lower()
        for kw,sug_time in AI_KEYWORDS.items():
            if kw in text_l:
                self.ai_lbl.setText(f"🤖 AI gợi ý: {sug_time} (dựa trên \"{kw}\")")
                h,m=sug_time.split(":"); self.time_e.setTime(QTime(int(h),int(m)))
                return
        self.ai_lbl.setText("")

    def _save(self):
        title=self.title_e.text().strip()
        if not title:
            QMessageBox.warning(self,"Lỗi","Vui lòng nhập tiêu đề!"); return
        d=self.date_e.date(); t=self.time_e.time()
        self.result_ev={
            "title":title,
            "date":f"{d.year()}-{d.month():02d}-{d.day():02d}",
            "time":f"{t.hour():02d}:{t.minute():02d}",
            "cat":self.cat_cb.currentText(),
            "repeat":self.repeat_cb.currentText(),
            "note":self.note_e.toPlainText(),
            "reminder":self.reminder_cb.isChecked(),
            "done":False
        }
        self.accept()

    def set_theme(self, T, acc): self.T=T; self._acc=acc


# ═══════════════════════════════════════════════════════════════
#  PAGE: EVENTS
# ═══════════════════════════════════════════════════════════════
class EventPage(QWidget):
    task_completed=pyqtSignal(int,int)
    def __init__(self, dm):
        super().__init__(); self.dm=dm; self.T=DARK; self._acc="#00d4ff"; self._init_ui()

    def _init_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(12)
        # Toolbar
        tb=QHBoxLayout(); tb.setSpacing(10)
        self.filter_cb=QComboBox()
        self.filter_cb.addItems(["Tất cả","Hôm nay","Tuần này","Chưa xong","Đã xong"])
        self.filter_cb.currentIndexChanged.connect(self.refresh)
        btn_add=AccentBtn("+ Thêm sự kiện")
        btn_add.setFixedHeight(36); btn_add.clicked.connect(self._add_event)
        btn_del=QPushButton("🗑 Xóa"); btn_del.clicked.connect(self._del_event)
        btn_done=QPushButton("✅ Hoàn thành"); btn_done.clicked.connect(self._mark_done)
        tb.addWidget(QLabel("Lọc:")); tb.addWidget(self.filter_cb,1)
        tb.addStretch(); tb.addWidget(btn_done); tb.addWidget(btn_del); tb.addWidget(btn_add)
        root.addLayout(tb)
        # List
        self.ev_list=QListWidget(); self.ev_list.setAlternatingRowColors(False)
        root.addWidget(self.ev_list,1)
        # Stats row
        self.stats_lbl=QLabel()
        root.addWidget(self.stats_lbl)

    def refresh(self):
        self.ev_list.clear()
        filt=self.filter_cb.currentText()
        now=datetime.now()
        today_str=now.strftime("%Y-%m-%d")
        week_start=(now-timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        week_end=(now+timedelta(days=6-now.weekday())).strftime("%Y-%m-%d")
        for i,ev in enumerate(self.dm.events()):
            d=ev.get("date","")
            if filt=="Hôm nay" and d!=today_str: continue
            if filt=="Tuần này" and not (week_start<=d<=week_end): continue
            if filt=="Chưa xong" and ev.get("done"): continue
            if filt=="Đã xong" and not ev.get("done"): continue
            done=ev.get("done",False)
            txt=f"{'✅ ' if done else '○ '}{ev['cat']} {ev['title']}"
            txt+=f"  —  {d} {ev.get('time','')}"
            if ev.get("repeat","Không lặp")!="Không lặp": txt+=f"  🔁{ev['repeat']}"
            if ev.get("reminder"): txt+="  🔔"
            item=QListWidgetItem(txt); item.setData(Qt.UserRole,i)
            if done: item.setForeground(QColor(self.T["txt3"]))
            self.ev_list.addItem(item)
        total=len(self.dm.events()); done_n=sum(1 for e in self.dm.events() if e.get("done"))
        self.stats_lbl.setText(f"📊 Tổng: {total}  •  Đã xong: {done_n}  •  Còn lại: {total-done_n}")

    def _add_event(self):
        dlg=AddEventDialog(self.dm,self); dlg.set_theme(self.T,self._acc)
        dlg.setStyleSheet(f"QDialog{{background:{self.T['card']};}} QLabel{{color:{self.T['txt']};background:transparent;}} QLineEdit,QTextEdit,QComboBox,QDateEdit,QTimeEdit{{background:{self.T['card2']};color:{self.T['txt']};border:1px solid {self.T['bdr']};border-radius:8px;padding:6px 10px;}}")
        if dlg.exec_()==QDialog.Accepted and dlg.result_ev:
            self.dm.add_ev(dlg.result_ev); self.refresh()

    def _del_event(self):
        item=self.ev_list.currentItem()
        if not item: return
        idx=item.data(Qt.UserRole)
        if QMessageBox.question(self,"Xóa","Bạn có chắc muốn xóa?",
                                 QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.dm.del_ev(idx); self.refresh()

    def _mark_done(self):
        item=self.ev_list.currentItem()
        if not item: return
        idx=item.data(Qt.UserRole)
        self.dm.toggle_done(idx)
        pts,streak=self.dm.get_game()["pts"],self.dm.get_game()["streak"]
        self.task_completed.emit(pts,streak)
        self.refresh()

    def set_theme(self, T, acc):
        self.T=T; self._acc=acc
        self.stats_lbl.setStyleSheet(f"color:{T['txt2']}; font-size:12px; background:transparent; padding:4px;")


# ═══════════════════════════════════════════════════════════════
#  PAGE: WORLD TIME MAP
# ═══════════════════════════════════════════════════════════════
class MapPage(QWidget):
    def __init__(self, dm):
        super().__init__(); self.dm=dm; self.T=DARK; self._acc="#00d4ff"; self._init_ui()

    def _init_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(12)
        lbl=QLabel("🌍 Bản Đồ Múi Giờ Thế Giới")
        f=lbl.font(); f.setPointSize(15); f.setBold(True); lbl.setFont(f)
        root.addWidget(lbl)
        # Map widget (custom painted)
        self.map_w=WorldMapWidget(); self.map_w.setMinimumHeight(220)
        self.map_w.tz_clicked.connect(self._on_tz_click)
        root.addWidget(self.map_w)
        # City grid
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        inner=QWidget(); grid=QGridLayout(inner); grid.setSpacing(10)
        self.city_cards=[]
        for i,(flag,tz) in enumerate(WORLD_TZ):
            card=Card(); card.setFixedHeight(72)
            v=QVBoxLayout(card); v.setContentsMargins(10,6,10,6); v.setSpacing(2)
            name=tz.split("/")[-1].replace("_"," ")
            ln=QLabel(f"{flag} {name}"); ln.setStyleSheet("font-weight:bold; font-size:12px;")
            lt=QLabel("—"); lt.setStyleSheet("font-size:16px; font-weight:bold;")
            lt.setObjectName("tz_time")
            v.addWidget(ln); v.addWidget(lt)
            card.setProperty("tz",tz)
            card.setCursor(Qt.PointingHandCursor)
            def on_click(e, card=card): self._on_tz_click(card.property("tz"))
            card.mousePressEvent=on_click
            grid.addWidget(card,i//4,i%4)
            self.city_cards.append((card,lt,tz))
        scroll.setWidget(inner); root.addWidget(scroll,1)
        # Detail panel
        self.detail=QLabel("Nhấp vào thành phố để xem chi tiết")
        self.detail.setWordWrap(True)
        root.addWidget(self.detail)

    def _on_tz_click(self, tz_name):
        t=self._get_time(tz_name)
        try:
            if HAS_PYTZ:
                tz=pytz.timezone(tz_name)
                dt=datetime.now(tz)
                offset=dt.utcoffset().total_seconds()/3600
                self.detail.setText(f"🕐 {tz_name}\n⏰ {dt.strftime('%H:%M:%S %Z')} — UTC{'+' if offset>=0 else ''}{offset:.1f}\n📅 {thu_vi(dt.weekday())}, {dt.strftime('%d/%m/%Y')}")
        except: self.detail.setText(tz_name)

    def _get_time(self, tz_name):
        try:
            if HAS_PYTZ:
                tz=pytz.timezone(tz_name); dt=datetime.now(tz)
                fmt=self.dm.S("fmt","24")
                return dt.strftime("%H:%M" if fmt=="24" else "%I:%M %p")
            return datetime.utcnow().strftime("%H:%M")
        except: return "—"

    def refresh(self):
        for card,lbl,tz in self.city_cards: lbl.setText(self._get_time(tz))

    def set_theme(self, T, acc):
        self.T=T; self._acc=acc
        self.map_w.set_theme(T,acc)
        for card,lbl,tz in self.city_cards:
            card.set_theme(T); lbl.setStyleSheet(f"font-size:16px; font-weight:bold; color:{acc}; background:transparent;")
        self.detail.setStyleSheet(f"color:{T['txt2']}; background:{T['card']}; border-radius:8px; padding:10px; font-size:12px;")


class WorldMapWidget(QWidget):
    tz_clicked=pyqtSignal(str)
    def __init__(self):
        super().__init__(); self.T=DARK; self._acc="#00d4ff"; self.setMinimumHeight(200)
        # Simplified timezone zone positions (x% of width, y% of height)
        self._zones=[
            ("UTC-5\nNew York",12,45,"America/New_York"),
            ("UTC-8\nLA",6,42,"America/Los_Angeles"),
            ("UTC-3\nSão Paulo",18,65,"America/Sao_Paulo"),
            ("UTC+0\nLondon",42,30,"Europe/London"),
            ("UTC+1\nParis",45,30,"Europe/Paris"),
            ("UTC+3\nMoscow",55,28,"Europe/Moscow"),
            ("UTC+3\nCairo",52,42,"Africa/Cairo"),
            ("UTC+5:30\nMumbai",65,48,"Asia/Kolkata"),
            ("UTC+7\nHCM",74,53,"Asia/Ho_Chi_Minh"),
            ("UTC+8\nShanghai",79,38,"Asia/Shanghai"),
            ("UTC+9\nTokyo",84,38,"Asia/Tokyo"),
            ("UTC+10\nSydney",85,65,"Australia/Sydney"),
        ]
        self._hover=None; self.setMouseTracking(True)

    def set_theme(self, T, acc): self.T=T; self._acc=acc; self.update()

    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w=self.width(); h=self.height()
        # Background ocean
        grad=QLinearGradient(0,0,w,h)
        grad.setColorAt(0,QColor(self.T["bg2"])); grad.setColorAt(1,QColor(self.T["card"]))
        p.fillRect(self.rect(),grad)
        # Grid lines (meridians)
        p.setPen(QPen(QColor(self.T["bdr"]),1,Qt.DotLine))
        for i in range(0,24):
            x=int(i/24*w); p.drawLine(x,0,x,h)
        for i in range(0,4):
            y=int(i/4*h); p.drawLine(0,y,w,y)
        # Landmass (simple rectangles)
        lands=[(3,25,22,45),(35,20,25,35),(40,35,15,30),(55,20,20,35),(60,35,20,30),(72,20,15,30),(79,25,10,55)]
        for lx,ly,lw,lh in lands:
            p.setBrush(QColor(self.T["card2"])); p.setPen(Qt.NoPen)
            p.drawRoundedRect(int(lx/100*w),int(ly/100*h),int(lw/100*w),int(lh/100*h),4,4)
        # TZ zones
        for name,xp,yp,tz in self._zones:
            x=int(xp/100*w); y=int(yp/100*h)
            is_hov=(self._hover==tz)
            col=QColor(self._acc) if is_hov else QColor(self.T["acc2"])
            p.setBrush(col); p.setPen(Qt.NoPen)
            r=10 if is_hov else 8
            p.drawEllipse(x-r,y-r,2*r,2*r)
            if is_hov:
                p.setPen(QColor(self._acc))
                f=p.font(); f.setPointSize(9); f.setBold(True); p.setFont(f)
                p.drawText(QRect(x-40,y+12,80,30),Qt.AlignCenter,name)
        # Labels
        p.setPen(QColor(self.T["txt3"]))
        f=p.font(); f.setPointSize(8); p.setFont(f)
        for i,label in enumerate(["W","","","E"]):
            p.drawText(i*w//3,h-4,label)

    def mouseMoveEvent(self, e):
        w=self.width(); h=self.height(); closest=None; min_d=30
        for name,xp,yp,tz in self._zones:
            x=int(xp/100*w); y=int(yp/100*h)
            d=math.sqrt((e.x()-x)**2+(e.y()-y)**2)
            if d<min_d: min_d=d; closest=tz
        if self._hover!=closest: self._hover=closest; self.update()

    def mousePressEvent(self, e):
        if self._hover: self.tz_clicked.emit(self._hover)


# ═══════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS / STATS
# ═══════════════════════════════════════════════════════════════
class StatsPage(QWidget):
    def __init__(self, dm):
        super().__init__(); self.dm=dm; self.T=DARK; self._acc="#00d4ff"; self._init_ui()

    def _init_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(16)
        lbl=QLabel("📊 Thống Kê & Phân Tích Thói Quen")
        f=lbl.font(); f.setPointSize(15); f.setBold(True); lbl.setFont(f)
        root.addWidget(lbl)
        # Game stats row
        self.game_row=QHBoxLayout(); self.game_row.setSpacing(12)
        self.pts_card=self._stat_card("🏆","Tổng điểm","0")
        self.streak_card=self._stat_card("🔥","Streak","0 ngày")
        self.done_card=self._stat_card("✅","Đã hoàn thành","0 việc")
        self.rate_card=self._stat_card("📈","Tỷ lệ","0%")
        for c in [self.pts_card,self.streak_card,self.done_card,self.rate_card]:
            self.game_row.addWidget(c)
        root.addLayout(self.game_row)
        # Chart area
        self.chart=BarChartWidget(); self.chart.setMinimumHeight(180)
        root.addWidget(self.chart,1)
        # Suggestions
        sug_card=Card(); sv=QVBoxLayout(sug_card)
        sv.addWidget(QLabel("💡 Gợi ý thói quen làm việc"))
        self.sug_lbl=QLabel(); self.sug_lbl.setWordWrap(True)
        sv.addWidget(self.sug_lbl); root.addWidget(sug_card)

    def _stat_card(self, icon, label, val):
        card=Card(); card.setFixedHeight(90)
        v=QVBoxLayout(card); v.setContentsMargins(10,8,10,8); v.setSpacing(2)
        li=QLabel(icon); li.setAlignment(Qt.AlignCenter)
        fi=li.font(); fi.setPointSize(18); li.setFont(fi)
        ll=QLabel(label); ll.setAlignment(Qt.AlignCenter)
        fl=ll.font(); fl.setPointSize(9); ll.setFont(fl)
        lv=QLabel(val); lv.setAlignment(Qt.AlignCenter); lv.setObjectName("val")
        fv=lv.font(); fv.setPointSize(14); fv.setBold(True); lv.setFont(fv)
        v.addWidget(li); v.addWidget(ll); v.addWidget(lv)
        return card

    def _get_val(self, card): return card.findChild(QLabel,"val")

    def refresh(self):
        g=self.dm.get_game()
        total=len(self.dm.events()); done=sum(1 for e in self.dm.events() if e.get("done"))
        rate=int(done/max(total,1)*100)
        self._get_val(self.pts_card).setText(f"{g.get('pts',0):,}")
        self._get_val(self.streak_card).setText(f"{g.get('streak',0)} ngày")
        self._get_val(self.done_card).setText(f"{g.get('done',0)} việc")
        self._get_val(self.rate_card).setText(f"{rate}%")
        # Hour distribution
        hour_counts=[0]*24
        for ev in self.dm.events():
            try:
                h=int(ev.get("time","00:00").split(":")[0])
                hour_counts[h]+=1
            except: pass
        self.chart.set_data(hour_counts,"Phân bố sự kiện theo giờ",self.T,self._acc)
        # Suggestions
        peak_h=hour_counts.index(max(hour_counts)) if any(hour_counts) else 9
        sugs=[f"• Bạn thường đặt lịch nhất vào {peak_h:02d}:00",
              f"• Streak hiện tại: {g.get('streak',0)} ngày — hãy duy trì!",
              "• Nên nghỉ 10 phút sau mỗi 50 phút làm việc",
              f"• Đã hoàn thành {done}/{total} việc — tỷ lệ {rate}%"]
        if g.get("streak",0)>=7: sugs.append("🏆 Tuyệt vời! Streak 7+ ngày liên tiếp!")
        self.sug_lbl.setText("\n".join(sugs))

    def set_theme(self, T, acc):
        self.T=T; self._acc=acc
        for card in [self.pts_card,self.streak_card,self.done_card,self.rate_card]:
            card.set_theme(T)
            v=self._get_val(card)
            if v: v.setStyleSheet(f"color:{acc}; background:transparent;")
        self.sug_lbl.setStyleSheet(f"color:{T['txt2']}; background:transparent; font-size:12px; line-height:1.8;")
        self.chart.set_theme(T,acc)


class BarChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._data=[0]*24; self._title=""; self.T=DARK; self._acc="#00d4ff"

    def set_data(self, data, title, T, acc):
        self._data=data; self._title=title; self.T=T; self._acc=acc; self.update()

    def set_theme(self, T, acc): self.T=T; self._acc=acc; self.update()

    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w=self.width(); h=self.height()
        p.fillRect(self.rect(),QColor(self.T["card"]))
        if not self._data or max(self._data)==0:
            p.setPen(QColor(self.T["txt3"]))
            p.drawText(self.rect(),Qt.AlignCenter,"Chưa có dữ liệu")
            return
        pad=30; chart_w=w-2*pad; chart_h=h-50
        maxv=max(self._data); n=len(self._data)
        bw=max(2,chart_w//n-2)
        # Title
        p.setPen(QColor(self.T["txt2"]))
        f=p.font(); f.setPointSize(10); f.setBold(True); p.setFont(f)
        p.drawText(pad,20,self._title)
        # Bars
        for i,v in enumerate(self._data):
            if v==0: continue
            bh=int(v/maxv*chart_h)
            x=pad+i*(chart_w//n); y=h-20-bh
            grad=QLinearGradient(x,y,x,h-20)
            c=QColor(self._acc); c2=QColor(self._acc); c2.setAlpha(60)
            grad.setColorAt(0,c); grad.setColorAt(1,c2)
            p.setBrush(grad); p.setPen(Qt.NoPen)
            p.drawRoundedRect(x,y,bw,bh,2,2)
        # X labels
        p.setPen(QColor(self.T["txt3"]))
        f.setPointSize(7); f.setBold(False); p.setFont(f)
        for i in range(0,24,3):
            x=pad+i*(chart_w//n)+bw//2
            p.drawText(x-8,h-4,f"{i:02d}h")
        # Border
        p.setPen(QPen(QColor(self.T["bdr"]),1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(pad,20,chart_w,chart_h)


# ═══════════════════════════════════════════════════════════════
#  PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════
class SettingsPage(QWidget):
    settings_changed=pyqtSignal()
    def __init__(self, dm):
        super().__init__(); self.dm=dm; self.T=DARK; self._acc="#00d4ff"; self._init_ui()

    def _init_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(16)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        inner=QWidget(); iv=QVBoxLayout(inner); iv.setSpacing(16); iv.setContentsMargins(0,0,10,0)
        # Appearance
        g1=QGroupBox("🎨 Giao Diện"); g1v=QVBoxLayout(g1)
        theme_row=QHBoxLayout()
        theme_row.addWidget(QLabel("Chủ đề:")); self.theme_cb=QComboBox()
        self.theme_cb.addItems(["Dark (Tối)","Light (Sáng)"])
        self.theme_cb.setCurrentIndex(0 if self.dm.S("theme","dark")=="dark" else 1)
        self.theme_cb.currentIndexChanged.connect(self._on_theme)
        theme_row.addWidget(self.theme_cb); theme_row.addStretch()
        g1v.addLayout(theme_row)
        acc_row=QHBoxLayout(); acc_row.addWidget(QLabel("Màu nhấn:"))
        self.acc_btns={}
        for name,col in ACCENT_MAP.items():
            btn=QPushButton()
            btn.setFixedSize(28,28); btn.setStyleSheet(f"background:{col};border-radius:14px;border:2px solid #fff;")
            btn.clicked.connect(lambda _,c=col: self._on_accent(c))
            self.acc_btns[col]=btn; acc_row.addWidget(btn)
        acc_row.addStretch(); g1v.addLayout(acc_row)
        iv.addWidget(g1)
        # Time
        g2=QGroupBox("⏰ Thời gian"); g2v=QVBoxLayout(g2)
        fmt_row=QHBoxLayout(); fmt_row.addWidget(QLabel("Định dạng giờ:"))
        self.fmt24=QRadioButton("24 giờ"); self.fmt12=QRadioButton("12 giờ (AM/PM)")
        if self.dm.S("fmt","24")=="24": self.fmt24.setChecked(True)
        else: self.fmt12.setChecked(True)
        self.fmt24.toggled.connect(self._on_fmt)
        fmt_row.addWidget(self.fmt24); fmt_row.addWidget(self.fmt12); fmt_row.addStretch()
        g2v.addLayout(fmt_row)
        tz_row=QHBoxLayout(); tz_row.addWidget(QLabel("Múi giờ:"))
        self.tz_cb=QComboBox(); self.tz_cb.addItems(ALL_TZ)
        idx=self.tz_cb.findText(self.dm.S("tz","Asia/Ho_Chi_Minh"))
        self.tz_cb.setCurrentIndex(max(idx,0))
        self.tz_cb.currentTextChanged.connect(lambda v: (self.dm.sS("tz",v),self.settings_changed.emit()))
        tz_row.addWidget(self.tz_cb,1); g2v.addLayout(tz_row)
        self.lunar_cb=QCheckBox("Hiển thị Âm lịch")
        self.lunar_cb.setChecked(self.dm.S("lunar",True))
        self.lunar_cb.toggled.connect(lambda v: (self.dm.sS("lunar",v),self.settings_changed.emit()))
        g2v.addWidget(self.lunar_cb); iv.addWidget(g2)
        # Notifications
        g3=QGroupBox("🔔 Thông báo"); g3v=QVBoxLayout(g3)
        self.sound_cb=QCheckBox("Âm thanh nhắc việc")
        self.sound_cb.setChecked(self.dm.S("sound",True))
        self.sound_cb.toggled.connect(lambda v: self.dm.sS("sound",v))
        g3v.addWidget(self.sound_cb); iv.addWidget(g3)
        # About
        g4=QGroupBox("ℹ️ Thông tin"); g4v=QVBoxLayout(g4)
        g4v.addWidget(QLabel("CHRONO AI v2.0\nỨng dụng quản lý thời gian thông minh\nHỗ trợ: Dương lịch + Âm lịch Việt Nam\nGamification, AI-lite reminder, Phân tích thói quen"))
        iv.addWidget(g4)
        iv.addStretch()
        scroll.setWidget(inner); root.addWidget(scroll)

    def _on_theme(self):
        v="dark" if self.theme_cb.currentIndex()==0 else "light"
        self.dm.sS("theme",v); self.settings_changed.emit()

    def _on_fmt(self):
        v="24" if self.fmt24.isChecked() else "12"
        self.dm.sS("fmt",v); self.settings_changed.emit()

    def _on_accent(self, col): self.dm.sS("acc",col); self.settings_changed.emit()

    def set_theme(self, T, acc): self.T=T; self._acc=acc


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR GAMIFICATION WIDGET
# ═══════════════════════════════════════════════════════════════
class GameBar(QWidget):
    def __init__(self):
        super().__init__(); self.T=DARK; self._acc="#00d4ff"
        self._pts=0; self._streak=0; self._done=0; self.setFixedHeight(100)

    def set_data(self, pts, streak, done): self._pts=pts; self._streak=streak; self._done=done; self.update()
    def set_theme(self, T, acc): self.T=T; self._acc=acc; self.update()

    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w=self.width(); h=self.height()
        # Background
        p.setBrush(QColor(self.T["card"])); p.setPen(QPen(QColor(self.T["bdr"]),1))
        p.drawRoundedRect(6,4,w-12,h-8,10,10)
        # Stats
        def draw_stat(icon, val, lbl, x, y):
            p.setPen(QColor(self._acc))
            f=p.font(); f.setPointSize(14); f.setBold(True); p.setFont(f)
            p.drawText(QRect(x,y,w-24,20),Qt.AlignHCenter,icon)
            f.setPointSize(11); f.setBold(True); p.setFont(f)
            p.setPen(QColor(self.T["txt"]))
            p.drawText(QRect(x,y+20,w-24,16),Qt.AlignHCenter,str(val))
            f.setPointSize(8); f.setBold(False); p.setFont(f)
            p.setPen(QColor(self.T["txt3"]))
            p.drawText(QRect(x,y+36,w-24,14),Qt.AlignHCenter,lbl)
        dw=(w-24)//3
        draw_stat("🏆",self._pts,"Điểm",12,8)
        draw_stat("🔥",f"{self._streak}d","Streak",12+dw,8)
        draw_stat("✅",self._done,"Xong",12+2*dw,8)


# ═══════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dm=DM()
        self.T=DARK if self.dm.S("theme","dark")=="dark" else LITE
        self._acc=self.dm.S("acc","#00d4ff")
        self._pages={}; self._cur_idx=0
        self.setWindowTitle("CHRONO AI — Quản Lý Thời Gian Thông Minh")
        self.setMinimumSize(1050,680)
        self._init_ui()
        self._apply_theme()
        # Timers
        self.clock_timer=QTimer(self); self.clock_timer.timeout.connect(self._tick)
        self.clock_timer.start(1000)
        self.tz_timer=QTimer(self); self.tz_timer.timeout.connect(self._tz_tick)
        self.tz_timer.start(5000)
        self.reminder_timer=QTimer(self); self.reminder_timer.timeout.connect(self._check_reminders)
        self.reminder_timer.start(30000)
        self._tick()

    def _init_ui(self):
        central=QWidget(); self.setCentralWidget(central)
        main_h=QHBoxLayout(central); main_h.setContentsMargins(0,0,0,0); main_h.setSpacing(0)
        # ─── SIDEBAR ───
        self.sidebar=QWidget(); self.sidebar.setFixedWidth(230)
        self.sidebar.setObjectName("sidebar")
        sb_v=QVBoxLayout(self.sidebar); sb_v.setContentsMargins(8,12,8,12); sb_v.setSpacing(4)
        # Logo
        logo=QLabel("⏱ CHRONO AI"); logo.setAlignment(Qt.AlignCenter)
        fl=logo.font(); fl.setPointSize(14); fl.setBold(True); logo.setFont(fl)
        logo.setFixedHeight(50); logo.setObjectName("logo")
        sb_v.addWidget(logo)
        # Separator
        sep=QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("sep")
        sb_v.addWidget(sep); sb_v.addSpacing(6)
        # Nav buttons
        nav_items=[("🕐","Đồng Hồ"),("🌐","Múi Giờ"),("📅","Lịch"),
                   ("📋","Sự Kiện"),("🗺️","Bản Đồ TG"),("📊","Thống Kê"),("⚙️","Cài Đặt")]
        self.nav_btns=[]; self.btn_group=QButtonGroup(self); self.btn_group.setExclusive(True)
        for i,(icon,label) in enumerate(nav_items):
            btn=NavBtn(icon,label); btn.clicked.connect(lambda _,idx=i: self._switch_page(idx))
            self.nav_btns.append(btn); self.btn_group.addButton(btn,i); sb_v.addWidget(btn)
        sb_v.addStretch()
        # Game bar
        self.game_bar=GameBar(); sb_v.addWidget(self.game_bar)
        # Time mini
        self.mini_clock=QLabel(); self.mini_clock.setAlignment(Qt.AlignCenter)
        fm=self.mini_clock.font(); fm.setPointSize(11); fm.setBold(True); self.mini_clock.setFont(fm)
        sb_v.addWidget(self.mini_clock)
        main_h.addWidget(self.sidebar)
        # ─── CONTENT ───
        content_wrap=QWidget()
        cw_v=QVBoxLayout(content_wrap); cw_v.setContentsMargins(0,0,0,0); cw_v.setSpacing(0)
        # Page title bar
        self.title_bar=QWidget(); self.title_bar.setFixedHeight(54); self.title_bar.setObjectName("titlebar")
        tb_h=QHBoxLayout(self.title_bar); tb_h.setContentsMargins(20,8,20,8)
        self.page_title=QLabel("⏱ Đồng Hồ")
        ft=self.page_title.font(); ft.setPointSize(16); ft.setBold(True); self.page_title.setFont(ft)
        self.page_sub=QLabel(datetime.now().strftime("%A, %d/%m/%Y"))
        tb_h.addWidget(self.page_title); tb_h.addStretch(); tb_h.addWidget(self.page_sub)
        cw_v.addWidget(self.title_bar)
        # Stack
        self.stack=QStackedWidget()
        self.clock_page=ClockPage(self.dm)
        self.tz_page=TZPage(self.dm)
        self.cal_page=CalPage(self.dm)
        self.ev_page=EventPage(self.dm)
        self.map_page=MapPage(self.dm)
        self.stats_page=StatsPage(self.dm)
        self.sets_page=SettingsPage(self.dm)
        for pg in [self.clock_page,self.tz_page,self.cal_page,self.ev_page,
                   self.map_page,self.stats_page,self.sets_page]:
            w=QWidget()
            wv=QVBoxLayout(w); wv.setContentsMargins(20,12,20,12); wv.setSpacing(0)
            wv.addWidget(pg)
            self.stack.addWidget(w)
        self.ev_page.task_completed.connect(self._on_task_done)
        self.sets_page.settings_changed.connect(self._on_settings_changed)
        cw_v.addWidget(self.stack,1)
        main_h.addWidget(content_wrap,1)
        # Select first
        self.nav_btns[0].setChecked(True)

    def _switch_page(self, idx):
        self._cur_idx=idx
        self.stack.setCurrentIndex(idx)
        titles=["⏱ Đồng Hồ","🌐 Múi Giờ","📅 Lịch","📋 Sự Kiện","🗺️ Bản Đồ TG","📊 Thống Kê","⚙️ Cài Đặt"]
        self.page_title.setText(titles[idx])
        if idx==2: self.cal_page._refresh_cal()
        if idx==3: self.ev_page.refresh()
        if idx==4: self.map_page.refresh()
        if idx==5: self.stats_page.refresh()

    def _tick(self):
        now=datetime.now()
        self.clock_page.update_clock()
        fmt=self.dm.S("fmt","24")
        ts=now.strftime("%H:%M:%S" if fmt=="24" else "%I:%M %p")
        self.mini_clock.setText(ts)
        self.page_sub.setText(now.strftime("%A, %d/%m/%Y"))
        g=self.dm.get_game()
        self.game_bar.set_data(g.get("pts",0),g.get("streak",0),g.get("done",0))

    def _tz_tick(self):
        if self._cur_idx in (1,4):
            if self._cur_idx==1: self.tz_page.refresh()
            if self._cur_idx==4: self.map_page.refresh()

    def _check_reminders(self):
        now=datetime.now()
        for ev in self.dm.events():
            if ev.get("done"): continue
            if not ev.get("reminder"): continue
            try:
                ev_dt=datetime.strptime(f"{ev['date']} {ev.get('time','00:00')}","%Y-%m-%d %H:%M")
                diff=(ev_dt-now).total_seconds()
                if 0<diff<=900:
                    self._show_notification(f"🔔 Nhắc việc: {ev['title']}",
                                            f"Còn {int(diff//60)} phút — {ev['time']}")
            except: pass

    def _show_notification(self, title, msg):
        box=QMessageBox(self); box.setWindowTitle(title); box.setText(msg)
        box.setIcon(QMessageBox.Information); box.exec_()

    def _on_task_done(self, pts, streak):
        bar=self.statusBar() if hasattr(self,"statusBar") else None
        if streak>1:
            self._show_notification("🎉 Hoàn thành!",f"+10 điểm! Streak: 🔥{streak} ngày!")

    def _on_settings_changed(self):
        self.T=DARK if self.dm.S("theme","dark")=="dark" else LITE
        self._acc=self.dm.S("acc","#00d4ff")
        self._apply_theme()

    def _apply_theme(self):
        T=self.T; acc=self._acc
        self.setStyleSheet(get_qss(T,acc))
        # Sidebar styling
        self.sidebar.setStyleSheet(f"#sidebar{{background:{T['bg2']}; border-right:1px solid {T['bdr']};}}")
        self.sidebar.findChild(QLabel,"logo").setStyleSheet(f"color:{acc}; font-weight:bold; background:transparent;")
        self.sidebar.findChild(QFrame,"sep").setStyleSheet(f"color:{T['bdr']}; background:{T['bdr']};")
        # Title bar
        self.title_bar.setStyleSheet(f"#titlebar{{background:{T['bg2']}; border-bottom:1px solid {T['bdr']};}}")
        self.page_title.setStyleSheet(f"color:{T['txt']}; background:transparent;")
        self.page_sub.setStyleSheet(f"color:{T['txt3']}; background:transparent; font-size:12px;")
        self.mini_clock.setStyleSheet(f"color:{acc}; background:transparent;")
        # Nav buttons
        for btn in self.nav_btns: btn.set_theme(T,acc)
        # Game bar
        self.game_bar.set_theme(T,acc)
        # Pages
        self.clock_page.set_theme(T,acc)
        self.tz_page.set_theme(T,acc)
        self.cal_page.set_theme(T,acc)
        self.ev_page.set_theme(T,acc)
        self.map_page.set_theme(T,acc)
        self.stats_page.set_theme(T,acc)
        self.sets_page.set_theme(T,acc)
        # Stack backgrounds
        for i in range(self.stack.count()):
            w=self.stack.widget(i)
            if w: w.setStyleSheet(f"background:{T['bg']};")


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
def main():
    app=QApplication(sys.argv)
    app.setApplicationName("CHRONO AI")
    app.setStyle("Fusion")
    # High DPI
    if hasattr(Qt,"AA_EnableHighDpiScaling"):
        app.setAttribute(Qt.AA_EnableHighDpiScaling,True)
    if hasattr(Qt,"AA_UseHighDpiPixmaps"):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps,True)
    # Splash (optional quick check)
    if not HAS_PYTZ:
        QMessageBox.information(None,"Gợi ý",
            "Để có đầy đủ tính năng múi giờ, hãy cài pytz:\n\npip install pytz\n\nỨng dụng vẫn chạy được với tính năng cơ bản.")
    win=MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()