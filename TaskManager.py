# New Project ( Task Scheduler )

import os

#os.environ["KIVY_NO_FILELOG"] = "1"
#os.environ["KIVY_NO_ARGS"] = "1"
#os.environ["KIVY_NO_CONSOLELOG"] = "1"
os.environ["KIVY_CAMERA"] = "opencv"

import weakref
import traceback
import pickle
import time
import socket
import requests
import json
import sqlite3 as sql
from functools import partial
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
import plyer
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.spinner import Spinner
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.screenmanager import Screen,ScreenManager,SlideTransition,FallOutTransition,SwapTransition,RiseInTransition
from kivy.clock import Clock
from kivy.uix.actionbar import ActionButton
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color,Rectangle
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.config import  Config
from kivy.storage.jsonstore import JsonStore
from kivy.lang import Builder
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.garden.navigationdrawer import NavigationDrawer
from kivy.properties import ObjectProperty,ListProperty,StringProperty
from kivy.config import Config

def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

def win_notification(app_name="Task Manager",message="",duration=3):
    plyer.notification.notify(title="{}".format(app_name), message="{}".format(message))

def daily_quote():

    if is_connected():
        pass
    else:
        return "Always believe something wonderful is about to happen"

    local_storage_quote = JsonStore("./AppData/quote.json")
    if local_storage_quote.exists("data"):
        last_updated = local_storage_quote.get("data")["last_updated"]
        last_updated_dt_object = dt.strptime(last_updated,"%d-%m-%Y")

        if last_updated_dt_object < app_ref.current_date_dt_object:
            pass
        else:
            quote = local_storage_quote.get("data")["quote"]
            if quote=="":
                quote="Always believe something wonderful is about to happen"
            return quote
    else:
        return
    request_object = requests.get("http://quotes.rest/qod.json?category=inspire")
    container = json.loads(request_object.text)
    c1 = container["contents"]
    c2 = c1["quotes"]
    c3 = c2[0]
    c4 = c3["quote"]
    local_storage_quote.put("data",last_updated=str(app_ref.current_date),quote=c4)
    return c4


local_storage = JsonStore("./AppData/theme.json")
theme_fg=local_storage.get('theme_list')['theme_fg']


#******************************************************************** SQL CONNECTION ******************************************************************************************

def sql_connection():
    
    global a
    a = sql.connect("./AppData/local_data")
    global cur
    cur=a.cursor()
        

#******************************************************************************************************************************************************************************


#******************************************************************** KV ( DESIGN CODE ) **************************************************************************************

kv="""
#:import Factory kivy.factory.Factory
#: import Window kivy.core.window.Window        
#: import DropDown kivy.uix.dropdown
        
<CircularProgressBar@FloatLayout>:

    size:(120,120)
    thickness:20
    segments:360
    progress_color:(0,1,0,1)
    progress_label_color:(0,1,0,1) if root.progress*100//root.max_value > 90 else root.progress_color
    background_color:(1,1,1,1)
    min_value:0
    max_value:100
    progress:0
    angle_start:0
    angle_end:360
    
    FloatLayout:
        canvas:
            Color:
                rgba:(210/255, 215/255, 211/255, 1)
            Ellipse:
                segments:root.segments
                size:root.size
                pos:root.pos
    
    FloatLayout:
        canvas:
            Color:
                rgba:(0,1,0,1) if root.progress*100//root.max_value > 90 else root.progress_color
            Ellipse:
                segments:root.segments
                size:root.size
                pos:root.pos
                angle_start:root.angle_start
                angle_end:(root.progress*root.angle_end)//root.max_value
                                
    FloatLayout:
        canvas:
            Color:
                rgba:root.background_color
            Ellipse:
                size:(root.size[0]-root.thickness,root.size[1]-root.thickness)
                pos:(root.pos[0]+(root.thickness//2),root.pos[1]+(root.thickness//2))

        Label:
            size:(30,30)
            pos:(root.pos[0],root.pos[1])
            text:" {} %".format(str(root.progress))
            color:root.progress_label_color
            font_size:21
            bold:True
            halign:'center'
            valign:'middle'


<StrokeLabel@Label>:

    background_color:(0,0,0,0)
    background_normal:""

    canvas.before:
        Color:
            rgba:app.fnt_fg_color
        Line:
            rounded_rectangle: (self.pos[0],self.pos[1],self.size[0],self.size[1],21)
            width: 1.4

<StrokeButton@Button>:

    background_color:(0,0,0,0)
    background_normal:""

    canvas.before:
        Color:
            rgba:app.fnt_fg_color
        Line:
            rounded_rectangle: (self.pos[0],self.pos[1],self.size[0],self.size[1],21)
            width: 1.4

<EllipseButton@Button>:

    background_color:(0,0,0,0)
    background_normal:""
    border:[16,16,16,16]
    canvas.before:
        Color:
            rgba:app.fnt_fg_color
        Ellipse:
            size:self.size
            pos:self.pos

<RoundedButton@Button>:

    background_color:(0,0,0,0)
    background_normal:""
    canvas.before:
        Color:
            rgba:app.fnt_fg_color
        RoundedRectangle:
            pos:self.pos
            size:self.size
            radius:[21]

<CustomDropDownChild@SpinnerOption>:

    background_color:(1,1,1,1)
    background_normal:""
    color:(0,0,0,1)
    canvas.before:
        Color:
            rgba:app.fnt_fg_color
        Line:
            rectangle: (self.pos[0],self.pos[1],self.size[0],self.size[1])
            width:1.5

<ConfirmationPage@BoxLayout>:

    orientation:"vertical"
    size_hint:(None,None)
    width:400
    height:350
    padding:[0,0,0,20]
    
    title:title
    confirm_btn:confirm_btn
    cancel_btn:cancel_btn
    
    canvas.before:
        Color:
            rgba:(218/255, 223/255, 225/255, 1)
        RoundedRectangle:
            pos:self.pos
            size:self.size
            radius:[21]
    
    
    Label:
        id:title
        font_size:18
        size_hint_y:None
        height:20
        color:(0,0,0,1)
    
    Label:
        size_hint_y:None
        height:100
    
    Label:
        size_hint_y:None
        height:40
        bold:True
        text:"Are you sure ?"
        font_size:22
        color:(0,0,0,1)
    
    Label:  
        size_hint_y:None
        height:80
    
    BoxLayout:
        size_hint_y:None
        height:50
        padding:[50,0,50,0]
        
        RoundedButton:
            id:confirm_btn
            text:"Confirm"
            size_hint_x:None
            width:110
        
        Label:
            size_hint_x:None
            width:90
        
        StrokeButton:
            id:cancel_btn
            text:"Cancel"
            color:app.fnt_fg_color
            size_hint_x:None
            width:110
            on_release:root.parent.dismiss()
    
    Label:
        size_hint_y:None
        height:20
        

<RectangleCardLayout@BoxLayout>:
    size_hint:(None,None)
    width:1275
    height:180
    padding:[0,0,20,0]
    spacing:[20,0]
    
    date_label:date_label
    day_label:day_label
    bxlayout:bxlayout
    total_tasks_label:total_tasks_label
    tasks_completed_label:tasks_completed_label
    task_progress_bar:task_progress_bar
    
    canvas.before:
        Color:
            rgba:(218/255, 223/255, 225/255, 1)
        RoundedRectangle:
            pos:self.pos
            size:self.size
            radius:[20]
            
    BoxLayout:
        orientation:"vertical"
        size_hint_x:None
        width:270
        spacing:[0,10]
        padding:[0,40]
        
        Label:
            id:date_label
            size_hint_y:None
            height:70
            font_size:22
            color:(0,0,0,1)
        
        Label:
            id:day_label
            size_hint_y:None
            height:40
            font_size:18
            color:(0,0,0,1)
    
    Label:
        size_hint_x:None
        width:1
        
        canvas:
            Color:
                rgba:(0,0,0,0.4)
            Rectangle:
                size:self.size
                pos:self.pos
    Label:
        size_hint_x:None
        width:30
        
    BoxLayout:
        id:bxlayout
        size_hint_x:None
        width:770
        
        Label:
            size_hint_x:None
            width:40
            
        GridLayout:
            size_hint_x:None
            width:150
            cols:2
            padding:[0,45]
            spacing:[0,20]
            
            Label:
                text:"Total Tasks"
                color:(0,0,0,1)
                font_size:16
            
            Label:
                id:total_tasks_label
                color:(0,0,0,1)
                font_size:16
            
            Label:
                text:"Tasks Completed"
                color:(0,0,0,1)
                font_size:16
            
            Label:
                id:tasks_completed_label
                color:(0,0,0,1)
                font_size:16
            
    
    BoxLayout:
        size_hint_x:None
        width:130
        padding:[0,25]

        CircularProgressBar:
            id:task_progress_bar
            size:(130,130)
         

<SquareCardLayout@BoxLayout>:

    size_hint:(None,None)
    width:260
    height:260
    padding:[5,5]
    
    task_label:task_label
    view_btn:view_btn
    complete_btn:complete_btn
    border_color:(236/255, 240/255, 241/255,1)
    
    canvas:
        Color:
            rgba:root.border_color
        RoundedRectangle:
            pos:self.pos
            size:self.size
            radius:[21]
            
    BoxLayout:
        orientation:"vertical"
        size_hint:(None,None)
        width:250
        height:250
        padding:[50,0,50,0]
        
        canvas.before:
            Color:
                rgba:(218/255, 223/255, 225/255, 1)
            RoundedRectangle:
                pos:self.pos
                size:self.size
                radius:[21]
                
        BoxLayout:
            orientation:"vertical"
            size_hint:(1,1)
            padding:[0,30,0,30]
        
            canvas.before:
                Color:
                    rgba:(218/255, 223/255, 225/255, 1)
                RoundedRectangle:
                    pos:self.pos
                    size:self.size
                    radius:[21]
        
            Label:  
                id:task_label
                color:(0,0,0,1)
                size_hint_y:None
                height:70
            
            Label:
                size_hint_y:None
                height:30
            
            BoxLayout:
                padding:[15,0]
                size_hint_y:None
                height:40
                
                StrokeButton:
                    id:view_btn
                    text:"View"
                    bold:True
                    color:app.fnt_fg_color
                    size_hint_x:None
                    width:120
            
            Label:
                size_hint_y:None
                height:10
            
            BoxLayout:
                padding:[15,0]
                size_hint_y:None
                height:40
                
                RoundedButton:
                    id:complete_btn
                    text:"Complete"
                    size_hint_x:None
                    width:120
        

<CardLayout@BoxLayout>:
    orientation:"vertical"
    spacing:[0,30]
    size_hint:(None,None)
    width:300
    height:650
    
    task_label_btn:task_label_btn
    description_label_btn:description_label_btn
    start_time_label_btn:start_time_label_btn
    end_time_label_btn:end_time_label_btn
    complete_btn:complete_btn
    bxlayout:bxlayout
    
    canvas.before:
        Color:
            rgba:[1,1,1,1]
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:[21]
    
    Button:
        id:task_label_btn
        size_hint_y:None
        height:70
        font_size:20
        bold:True
        background_color:[1,1,1,1]
        background_normal:""
        color:(0,0,0,1)
    
    ScrollView:
        size_hint_y:None
        height:380
        do_scroll_x: False
        do_scroll_y: True
        bar_width:5
        bar_color:app.fnt_fg_color
        bar_inactive_color:[136/255,136/255,136/255,1]
        padding:[10,0]
        
        BoxLayout:
            id:bxlayout
            orientation:"vertical"
            spacing:[0,20]
            
            Button:
                id:description_label_btn
                color:(0,0,0,1)
                size_hint_y:None
                height:230
                background_color:[1,1,1,1]
                background_normal:""
            
            GridLayout:
                id:gdlayout
                size_hint_y:None
                height:120
                cols:2
                
                Label:
                    text:"Start Time"
                    color:(0,0,0,1)
                    size_hint:(None,None)
                    width:gdlayout.size[0]/2
                    height:50
                
                Label:
                    text:"End Time"
                    color:(0,0,0,1)
                    size_hint:(None,None)
                    width:gdlayout.size[0]/2
                    height:50
                
                Button:
                    id:start_time_label_btn
                    color:(0,0,0,1)
                    background_color:[1,1,1,1]
                    background_normal:""
                
                Button:
                    id:end_time_label_btn
                    color:(0,0,0,1)
                    background_color:[1,1,1,1]
                    background_normal:""
    
    Label:
        size_hint_y:None
        height:50

    BoxLayout:
        size_hint_y:None
        height:50
        padding:[90,0]
        
        RoundedButton:
            id:complete_btn
            text:"Complete"
            size_hint_x:None
            width:120
    
    Label:
        size_hint_y:None
        height:10

<CustomPopup@BoxLayout>:
    
    size_hint:(1,1)
    bg_opacity:(0,0,0,0.75)
    canvas.before:
        Color:
            rgba:root.bg_opacity
        Rectangle:
            size:self.size
            pos:self.pos
        
<Welcome>:

    canvas.before:

        Color:
            rgba:app.fnt_fg_color
        Rectangle:
            size:self.size
            pos:self.pos

    Label:

        text:"WELCOME"
        font_size:35
        bold:True
        font_color:(1,1,1,1)


<Main>:

    id:main_win
    space_x:self.size[0]/3
    orientation:"vertical"
    todolist_btn:todolist_btn
    more_window_btn:more_window_btn
    exit_btn:exit_btn

    canvas.before:

        Color:
            rgba:app.fnt_bg_color
        Rectangle:
            size:self.size
            pos:self.pos
            
    Label:
        size_hint_y:None
        height:20
        
    BoxLayout:

        orientation:"horizontal"
        size_hint_y:None
        height:80
        padding:[0,10]
        
        Label:
            size_hint_x:0.91
            
        EllipseButton:
            id:exit_btn
            text:'X'
            font_size:30
            size_hint_x:0.04
            on_release:app.exit()

        Label:
            size_hint_x:0.05

    Label:
        size_hint_y:None
        height:50
        
    BoxLayout:
        
        orientation:'vertical'
        padding:[main_win.space_x + 120,0,main_win.space_x + 120,0]

        RoundedButton:

            id:todolist_btn
            text:'To Do List'
            font_size:25
            size_hint_y:None
            height:50
            on_press:root.todolist()
        
        Label:
            size_hint_y:None
            height:30

        RoundedButton:

            id:more_window_btn
            text:'More'
            font_size:25
            size_hint_y:None
            height:50
            on_press:root.more_window()
        
    Label:
        size_hint_y:None
        height:350


<MoreWindow>:

    id:main_win
    space_x:self.size[0]/3
    orientation:"vertical"
    
    back_btn:back_btn
    
    canvas.before:
        Color:
            rgba:(236/255, 240/255, 241/255,1)
        Rectangle:
            size:self.size
            pos:self.pos

    Label:
        size_hint_y:None
        height:20
        
    BoxLayout:

        orientation:"horizontal"
        size_hint_y:None
        height:80
        padding:[0,10]
        
        Label:
            size_hint_x:0.05
        
        EllipseButton:
            id:back_btn
            text:'<'
            font_size:30
            size_hint_x:0.04
            on_release:root.back()
        
        Label:
            size_hint_x:0.91
    
    Label:
        size_hint_y:None
        height:125
        
    BoxLayout:
        
        orientation:'vertical'
        padding:[main_win.space_x + 120,0,main_win.space_x + 120,0]

        RoundedButton:

            id:todolist_btn
            text:'Performance History'
            font_size:25
            size_hint_y:None
            height:50
            on_press:root.performance_history()
        
        Label:
            size_hint_y:None
            height:30

        RoundedButton:

            id:change_theme_btn
            text:'Change Theme'
            font_size:25
            size_hint_y:None
            height:50
            on_press:root.change_theme()

    Label:
        size_hint_y:None
        height:325

<OverviewPopup_PerformanceHistory>:
    orientation:"vertical"
    size_hint:(None,None)
    width:800
    height:640
    padding:[0,30,0,20]
    
    back_btn:back_btn
    bxlayout_scrollview:bxlayout_scrollview
    bxlayout:bxlayout
    
    canvas.before:
        Color:
            rgba:app.fnt_bg_color
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:[21]
            
    ScrollView:
        id:bxlayout_scrollview
        size_hint_y:None
        height:550
        do_scroll_x:False
        do_scroll_y:True
        bar_width:5
            
        GridLayout:
            id:bxlayout
            cols:1
            size_hint_y:None
            minimum_height:600
            padding:(0,0,0,30)
            spacing:(0,20)

            
    BoxLayout:
        size_hint_y:None
        height:40
        padding:[360,0]
            
        RoundedButton:
            id:back_btn
            text:"<"
            bold:True
            font_size:25
            on_release:root.back()
            

<AdditionalOptionsPopup_PerformanceHistory>:
    orientation:"vertical"
    id:main_win
    size_hint:(None,None)
    width:240
    height:110
    padding:[30,30]
        
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        RoundedRectangle:
            pos:self.pos
            size:self.size
            radius:[21]
    
    RoundedButton:
        disabled:True
        text:"Overview"
        size_hint:(None,None)
        width:180
        height:50
        on_release:root.overview()
    

<PerformanceHistory>:
    orientation:"vertical"
    id:main_win
    space_x:self.size[0]/3
    padding:[0,10,0,30]
    
    back_btn:back_btn
    bxlayout_scrollview:bxlayout_scrollview
    bxlayout:bxlayout
    dropdown:dropdown
    additional_optn_btn:additional_optn_btn
    
    canvas.before:
        Color:
            rgba:(236/255, 240/255, 241/255,1)
        Rectangle:
            size:self.size
            pos:self.pos
    
    BoxLayout:
        size_hint_y:None
        height:40
        
        Label:
            size_hint_x:0.45
        
        Spinner:
            id:dropdown
            size_hint_x:0.078
            size_hint_y:None
            height:40
            background_color:(0,0,0,0)
            background_normal:""
            color:(0,0,0,1)
            canvas.before:
                Color:
                    rgba:app.fnt_fg_color
                Line:
                    rounded_rectangle: (self.pos[0],self.pos[1],self.size[0],self.size[1],21)
                    width: 1.4
            option_cls:Factory.get('CustomDropDownChild')
            values:root.dropdown_options
            text:root.dropdown_options[1]
            on_text:root.update_view(self)
        
        Label:
            size_hint_x:0.43
            
        EllipseButton:
            size_hint_x:0.025
            id:additional_optn_btn
            text:"..."
            font_size:25
            on_release:root.additionaloptions()
            size_hint_y:None
            height:40

        Label:
            size_hint_x:0.01
    
    Label:  
        size_hint_y:None
        height:30
    
    ScrollView:
        id:bxlayout_scrollview
        size_hint_y:None
        height:660
        do_scroll_x:False
        do_scroll_y:True
        bar_width:0
        padding:(0,40,0,40)
        
        GridLayout:
            id:bxlayout
            cols:1
            size_hint_y:None
            minimum_height:600
            padding:(130,0,130,0)
            spacing:30
        
    Label:
        size_hint_y:None
        height:30
        
    BoxLayout:

        size_hint_y:None
        height:40
        padding:[main_win.space_x+210,0]
            
        RoundedButton:
            id:back_btn
            text:"<"
            bold:True
            font_size:25
            on_release:root.back()
        
<ToDoListNav>:
    
    current_time:current_time
    task_progress_bar:task_progress_bar
    main_win:main_win
    
    ScrollView:
        id:main_win
        do_scroll_x:False
        do_scroll_y:True
        bar_width:0
        size_hint_y:None
        height:Window.size[1]
        
        BoxLayout:
            orientation:"vertical"
            spacing:[0,10]
            size_hint_y:None
            height:Window.size[1]+200
            
            canvas.before:
                Color:
                    rgba:app.fnt_bg_color
                Rectangle:
                    size:self.size
                    pos:self.pos

            Label:
                size_hnit_y:None
                height:40
                
            BoxLayout:

                padding:[60,0]
                size_hint_y:None
                height:140
                    
                BoxLayout:
                    
                    orientation:"vertical"
                    
                    canvas.before:

                        Color:
                            rgba:app.fnt_fg_color
                        RoundedRectangle:
                            size:self.size
                            pos:self.pos
                            radius:[15]
                    
                    Label:
                        text:app.current_dateonly
                        font_size:40
                        bold:True
                        color:(1,1,1,1)
                        size_hint_y:None
                        height:50
                    
                    Label:
                        text:app.current_monthyearonly
                        font_size:21
                        color:(1,1,1,1)
                        size_hint_y:None
                        height:60
                
            Label:
                size_hint_y:None
                height:40

            BoxLayout:

                padding:[50,0,50,0]
                
                Label:

                    canvas.before:
                        Color:
                            rgba:app.fnt_fg_color
                        RoundedRectangle:
                            size:self.size
                            pos:self.pos
                            radius:[20]
                    
                    id:current_time
                    text:app.current_time
                    font_size:20
                    bold:True
                    size_hint_y:None
                    height:50

            Label:
                size_hint_y:None
                height:70

            Label:
                padding:[50,0]
                size_hint_y:None
                height:1
                
                canvas.before:

                    Color:
                        rgba:(0,0,0,1)
                    RoundedRectangle:
                        size:self.size
                        pos:self.pos
                        radius:[120]
                
            Label:
                size_hint_y:None
                height:50
                text:"Quote of the Day"
                font_size:20
                color:(0,0,0,1)

            Label:
                padding:[50,0]
                size_hint_y:None
                height:1
                
                canvas.before:

                    Color:
                        rgba:(0,0,0,1)
                    RoundedRectangle:
                        size:self.size
                        pos:self.pos
                        radius:[120]
                        
            
            BoxLayout:

                padding:[15,0,5,0]
                size_hint_y:None
                height:200
                    
                Label:
                    
                    text:app.daily_quote
                    text_size:self.size
                    font_size:16
                    color:(0,0,0,1)
            
            Label:
                size_hint_y:None
                height:260

            BoxLayout:
                size_hint_y:None
                height:180
                padding:[50,20]

                CircularProgressBar:
                    id:task_progress_bar
                    progress_color:app.fnt_fg_color
                    thickness:30
                    size:(130,130)
                    background_color:app.fnt_bg_color

            Label:
                size_hint_y:None
                height:20
                


<ChangeTimePopup>:

    orientation:"vertical"
    id:change_time_popup
    size_hint:(None,None)
    size:(490,490)
    padding:[20,20]
    
    new_time_textbox:new_time_textbox
    title:title    
    update_btn:update_btn
    cancel_btn:cancel_btn

    canvas.before:
        Color:
            rgba:(1,1,1,1)
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:[20]

    Label:
        size_hint_y:None
        height:30
        id:title
        color:(0,0,0,1)
        font_size:22
        
    Label:
        size_hint_y:None
        height:80

    GridLayout:

        size_hint_y:None
        height:90
        cols:2
        padding:[20,0,20,0]

        Label:
            text:"New Time"
            color:(0,0,0,1)

        TextInput:
            hint_text:"24hr format ( e.g. 13:36 )"
            id:new_time_textbox

    Label:
        size_hint_y:None
        height:150

    BoxLayout:
       
        id:bxlayout
        size_hint_y:None
        height:50
        
        Label:
            size_hint_x:None
            width:70

        RoundedButton:
            size_hint_x:None
            width:120
            id:update_btn
            text:'Update'
            bold:True
            on_press:root.update_time()

        Label:
            size_hint_x:None
            width:70

        RoundedButton:
            id:cancel_btn
            size_hint_x:None
            width:120
            text:'Cancel'
            bold:True
            on_release:root.cancel()

        Label:
            size_hint_x:None
            width:70

    Label:
        size_hint_y:None
        height:18


<ChangeDescPopup>:

    orientation:"vertical"
    id:change_desc_popup
    size_hint:(None,None)
    size:(490,490)
    padding:[20,20]
    
    new_desc_textbox:new_desc_textbox
        
    update_btn:update_btn
    cancel_btn:cancel_btn

    canvas.before:
        Color:
            rgba:(1,1,1,1)
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:[20]

    Label:
        size_hint_y:None
        height:30
        text:"Change Description"
        color:(0,0,0,1)
        font_size:22
        
    Label:
        size_hint_y:None
        height:80

    GridLayout:

        size_hint_y:None
        height:150
        cols:2
        padding:[10,0,10,0]

        Label:
            text:"Change Description"
            color:(0,0,0,1)

        TextInput:
            hint_text:"Description"
            id:new_desc_textbox

    Label:
        size_hint_y:None
        height:80

    BoxLayout:
       
        id:bxlayout
        size_hint_y:None
        height:50
        
        Label:
            size_hint_x:None
            width:70

        RoundedButton:
            size_hint_x:None
            width:120
            id:update_btn
            text:'Update'
            bold:True
            on_press:root.update_desc()

        Label:
            size_hint_x:None
            width:70

        RoundedButton:
            id:cancel_btn
            size_hint_x:None
            width:120
            text:'Cancel'
            bold:True
            on_release:root.cancel()

        Label:
            size_hint_x:None
            width:70

    Label:
        size_hint_y:None
        height:18


<TaskPropertyPopup>:

    orientation:"vertical"
    id:task_property_popup
    size_hint:(None,None)
    size:(490,510)
    padding:[20,20]
    
    delete_btn:delete_btn

    pp_10_min:pp_10_min
    pp_15_min:pp_15_min
    pp_30_min:pp_30_min
    pp_1_hr:pp_1_hr
    pp_2_hr:pp_2_hr
    pp_3_hr:pp_3_hr
    
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:[20]

    Label:
        size_hint_y:None
        height:30
        text:"Task"
        color:(0,0,0,1)
        font_size:22


    Label:
        size_hint_y:None
        height:80

    BoxLayout:
        size_hint_y:None
        height:50
        padding:[140,0,140,0]
        
        RoundedButton:
        
            id:delete_btn
            text:'Delete Task'
            font_size:18
            on_release:root.delete_task()

    Label:
        size_hint_y:None
        height:60

    GridLayout:

        cols:3
        size_hint_y:None
        height:45
        
        Label:
            text:"---------------------------------"
            color:app.fnt_fg_color

        Label:
            text:"Postpone"
            font_size:20
            color:(0,0,0,1)

        Label:
            text:"---------------------------------"
            color:app.fnt_fg_color

    Label:
        size_hint_y:None
        height:60
    
    GridLayout:

        cols:3
        size_hint_y:None
        height:135
        spacing:[60,20]
        padding:[60,0,60,0]
        
        EllipseButton:
            text:"10 MNS"
            id:pp_10_min
            size_hint_x:None
            width:60

        EllipseButton:
            text:"15 MNS"
            id:pp_15_min
            size_hint_x:None
            width:60

        EllipseButton:
            text:"30 MNS"
            id:pp_30_min
            size_hint_x:None
            width:60

        EllipseButton:
            text:"1 HR"
            id:pp_1_hr
            size_hint_x:None
            width:60

        EllipseButton:
            text:"2 HR"
            id:pp_2_hr
            size_hint_x:None
            width:60

        EllipseButton:
            text:"3 HR"
            id:pp_3_hr
            size_hint_x:None
            width:60
            
    
    Label:
        size_hint_y:None
        height:15

            
<AdditionalOptionsPopup_ToDoList>:
    orientation:"vertical"
    id:main_win
    size_hint:(None,None)
    width:240
    height:270
    padding:[20,40]
        
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        RoundedRectangle:
            pos:self.pos
            size:self.size
            radius:[21]
    
    del_unf_tsk_btn:del_unf_tsk_btn
    del_compltd_tsk_btn:del_compltd_tsk_btn
    del_all_tsk_btn:del_all_tsk_btn
    
    RoundedButton:
        id:del_compltd_tsk_btn
        text:"Remove Completed Task(s)"
        size_hint:(None,None)
        width:200
        height:50
        on_release:root.del_completed_tasks(show_popup=True)
    
    Label:
        size_hint_y:None
        height:20

    RoundedButton:
        id:del_unf_tsk_btn
        text:"Delete Unfinished Task(s)"
        size_hint:(None,None)
        width:200
        height:50
        on_release:root.del_unfinished_tasks(show_popup=True)
    
    Label:
        size_hint_y:None
        height:20
    
    RoundedButton:
        id:del_all_tsk_btn
        text:"Delete All Task(s)"
        size_hint:(None,None)
        width:200
        height:50
        on_release:root.del_all_tasks(show_popup=True)


<JumpDatePopup@BoxLayout>:
    orientation:"vertical"
    size_hint:(None,None)
    width:600
    height:500
    padding:[15,0,25,40]
    
    date_btn_gdlayout:date_btn_gdlayout
    
    canvas.before:
        Color:
            rgba:(218/255, 223/255, 225/255, 1)
        RoundedRectangle:
            pos:self.pos
            size:self.size
            radius:[21]
    
    Label:
        text:"Jump To"
        font_size:18
        size_hint_y:None
        height:20
        color:(0,0,0,1)
    
    Label:
        size_hint_y:None
        height:70
    
    ScrollView:
        size_hint_y:None
        height:340
        do_scroll_x:False
        do_scroll_y:True
        bar_width:0
        
        GridLayout:
            id:date_btn_gdlayout
            cols:4
            minimum_height:350
            padding:(20,20)
            spacing:(30,25)


<ToDoList>:

    orientation:"vertical"
    id:main_win
    space_x:self.size[0]/3

    main_box:main_box
    gdlayout:gdlayout
    arrow_label:arrow_label
    add_btn:add_btn
    additional_optn_btn:additional_optn_btn

    date_btn_gdlayout:date_btn_gdlayout
    jump_date_bxlayout:jump_date_bxlayout
    upcoming_date_btn_label:upcoming_date_btn_label
    
    canvas.before:

        Color:
            rgba:app.fnt_bg_color
        Rectangle:
            size:self.size
            pos:self.pos
            

    BoxLayout:
        
        size_hint_y:None
        height:100
        padding:[0,25]

        Label:
            size_hint_x:0.01
        
        Button:
        
            size_hint_x:0.02
            id:arrow_label
            text:">"
            bold:True
            font_size:22
            color:app.fnt_fg_color
            background_color:(0,0,0,0)
            background_normal:""
            on_release:app.todolistnav_page.toggle_state()
        
        Label:
            size_hint_x:0.45

        BoxLayout:
            padding:[0,10,0,0]
            size_hint_x:0.04
            
            Label:
                id:upcoming_date_btn_label
                color:app.fnt_fg_color
                bold:True
                font_size:25
        
        Label:
            size_hint_x:0.51

        EllipseButton:
            size_hint_x:0.03
            id:add_btn
            text:"+"
            font_size:25
            on_release:root.add()
            size_hint_y:None
            height:40
            
        Label:
            size_hint_x:0.02
        
        EllipseButton:
            size_hint_x:0.03
            id:additional_optn_btn
            text:"..."
            font_size:25
            on_release:root.additionaloptions()
            size_hint_y:None
            height:40

        Label:
            size_hint_x:0.01

    Label:
        size_hint_y:None
        height:40

    BoxLayout:
        size_hint_y:None
        height:40
        
        GridLayout:
            id:date_btn_gdlayout
            rows:1
            spacing:[40,0]
            padding:[40,0]
            size_hint_x:0.96
        
        BoxLayout:
            id:jump_date_bxlayout
            size_hint_x:0.04
            
    
    Label:
        size_hint_y:None
        height:60

        
    ScrollView:
        id:main_box
        size_hint_y:0.57
        do_scroll_x: False
        do_scroll_y: True
        bar_width:5
        bar_color:app.fnt_fg_color
        bar_inactive_color:[136/255,136/255,136/255,1]
        padding:[5,0]

        GridLayout:
            id:gdlayout
            cols:4
            size_hint_y:None
            minimum_height:700
            padding:[100,0,115,0]
            spacing:[100,30]

    Label:
        size_hint_y:None
        height:25

    BoxLayout:

        size_hint_y:None
        height:40
        padding:[main_win.space_x+210,0]
            
        RoundedButton:
            text:"<"
            bold:True
            font_size:25
            on_release:root.back()

    Label:
        size_hint_y:None
        height:15


<AddTaskPopup>:

    orientation:"vertical"
    id:main_win
    size_hint:(None,None)
    size:(540,530)
    padding:[20,20]
     
    date:date
    task:task
    description:description
    start_time:start_time
    end_time:end_time
    cancel_btn:cancel_btn
    
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:[20]
            

    Label:
        size_hint_y:None
        height:30
        text:"Add Task"
        font_size:22
        color:(0,0,0,1)
        halign:"center"
    
    Label:  
        size_hint_y:None
        height:50

    GridLayout:
        size_hint_y:None
        height:250
        padding:[10,0,20,0]
        spacing:[5,10]
        cols:2
        
        Label:
            size_hint_y:None
            height:40
            text:"Date"
            color:(0,0,0,1)

        TextInput:
            id:date
            multiline:False
            write_tab:False
            text:app.current_date

        Label:
            size_hint_y:None
            height:40
            text:"Task"
            color:(0,0,0,1)

        TextInput:
            id:task
            multiline:False
            write_tab:False

        Label:
            size_hint_y:None
            height:70
            text:"Description"
            color:(0,0,0,1)

        TextInput:
            id:description
            multiline:True
            write_tab:False

        Label:
            size_hint_y:None
            height:40
            text:"Start Time"
            color:(0,0,0,1)

        TextInput:
            id:start_time
            multiline:False
            write_tab:False
            hint_text:"e.g. 09:30"

        Label:
            size_hint_y:None
            height:40
            text:"End Time"
            color:(0,0,0,1)

        TextInput:
            id:end_time
            multiline:False
            write_tab:False
            hint_text:"e.g. 14:30"
            
    
    Label:
        size_hint_y:None
        height:60

    BoxLayout:

        padding:[80,0]
        size_hint_y:None
        height:50

        RoundedButton:
            text:"Add"
            size_hint_x:None
            width:110
            on_release:root.add()
            
        Label:
            size_hint_x:None
            width:120

        RoundedButton:
            text:"Cancel"
            id:cancel_btn
            size_hint_x:None
            width:110
            on_release:root.back()

        Label:
            size_hint_x:None
            width:20

    Label:
        size_hint_y:None
        height:30

<Reminderpopup>:

    orientation:"vertical"
    id:main_win
    size_hint:(None,None)
    size:(540,490)
    padding:[20,20]

    canvas.before:
        Color:
            rgba:(1,1,1,1)
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius:[20]
            
    text_box:text_box
    snooze_btn:snooze_btn
    complete_btn:complete_btn
    

    Label:
        size_hint_y:None
        height:30
        text:"Reminder"
        font_size:22
        color:(0,0,0,1)

    Label:
        size_hint_y:None
        height:20
        
    Label:
        size_hint_y:None
        height:350
        id:text_box
        color:(0,0,0,1)
        font_size:20

    BoxLayout:
    
        padding:[80,0]
        size_hint_y:None
        height:50

        RoundedButton:
            id:complete_btn
            text:"Complete"
            size_hint_x:None
            width:110
            on_release:root.complete()

        Label:
            size_hint_x:None
            width:120
        
        RoundedButton:
            id:snooze_btn
            text:"Snooze"
            size_hint_x:None
            width:110
            on_release:root.snooze()
            
        Label:
            size_hint_x:None
            width:20


<ChangeTheme>:

    orientation:"vertical"

    clr_picker_bxlayout:clr_picker_bxlayout
    change_btn:change_btn
    cancel_btn:cancel_btn
    
    canvas.before:
        Color:
            rgba:(236/255, 240/255, 241/255,1)
        Rectangle:
            size:self.size
            pos:self.pos

        
    BoxLayout:

        orientation:"horizontal"
        size_hint_y:None
        height:80
        padding:[0,10]
        
        Label:
            size_hint_x:0.9
            
        EllipseButton:
            id:exit_btn
            text:'X'
            font_size:30
            size_hint_x:0.04
            on_release:app.exit()

        Label:
            size_hint_x:0.05
    
    Label:
        size_hint_y:None
        height:225

    BoxLayout:
        
        size_hint_y:None
        height:200
        id:clr_picker_bxlayout

        Label:
            size_hint_x:None
            width:100
        
    Label:
        size_hint_y:None
        height:190
    
    BoxLayout:

        size_hint_y:None
        height:50
        
        Label:
            size_hint_x:0.32

        BoxLayout:
            size_hint_x:0.4

            RoundedButton:
                size_hint_x:None
                width:140
                id:change_btn
                text:"Change Theme"
                on_release:root.changetheme("pass","btn_press")

            Label:
                size_hint_x:None
                width:200
            
            RoundedButton:
                size_hint_x:None
                width:120
                id:cancel_btn
                text:"Cancel"
                on_release:root.cancel()  
        
        Label:
            size_hint_x:0.25

    Label:
        size_hint_y:None
        height:100


"""

#******************************************************************************************************************************************************************************


Builder.load_string(kv)

# to generate stroke labels

class StrokeLabel(Label):
    pass

# to generate stroke buttons

class StrokeButton(Button):
    pass

# to generate ellipse buttons

class EllipseButton(Button):
    pass

# to generate rounded buttons

class RoundedButton(Button):
    pass

# to generate confirmation page with custom title and confirm/cancel buttons

class ConfirmationPage(BoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass

# to generate rectangle tiles showing individual day progress and task completion details

class RectangleCardLayout(BoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass    
       
# to generate square task tiles in to do list

class SquareCardLayout(BoxLayout):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass

# to generate card tiles for individual task embedded in popup 

class CardLayout(BoxLayout):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass

class CustomPopup(BoxLayout):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        if len(self.children)!=0:
            self.clear_widgets()
        
        if len(self.children)>1:
            self.remove_widget(self.children[0])

    def open(self,*_):
        
        Window.add_widget(self)
        Window.bind(on_keyboard=self.handle_keyboard,on_touch_down=self.handle_mouse)
        
    def dismiss(self,*_):
        
        Window.remove_widget(self)
        Window.unbind(on_keyboard=self.handle_keyboard,on_touch_down=self.handle_mouse)
    
    def handle_keyboard(self, window, key, *largs):
        if key == 27:
            self.dismiss()
    
    def handle_mouse(self,*_):
        if len(self.children)==0:
            return
        child = self.children[0]
        if not child.collide_point(Window.mouse_pos[0],Window.mouse_pos[1]):
            self.dismiss()

class SortList():
    
    def __init__(self,**kwargs):
        pass
    
    def sort_by_start_time(lst):
        
        try:
            bfr0 = {element[4]:element for element in lst}
            bfr1 = [element[4] for element in lst]
            bfr2 = [dt.strptime(bfr1[i],"%H:%M") for i in range(len(bfr1))]
            bfr2.sort()
            bfr3 = {bfr1[i]:dt.strptime(bfr1[i],"%H:%M") for i in range(len(bfr1))}
            bfr4 = [list(bfr3.keys())[list(bfr3.values()).index(element)]for element in bfr2]
            bfr5 = [bfr0.get(bfr4[i]) for i in range(len(bfr4))]    
            return bfr5
        except:
            return lst

    def sort_by_end_time(lst):
        
        try:
            bfr0 = {element[5]:element for element in lst}
            bfr1 = [element[5] for element in lst]
            bfr2 = [dt.strptime(bfr1[i],"%H:%M") for i in range(len(bfr1))]
            bfr2.sort()
            bfr2.reverse()
            bfr3 = {bfr1[i]:dt.strptime(bfr1[i],"%H:%M") for i in range(len(bfr1))}
            bfr4 = [list(bfr3.keys())[list(bfr3.values()).index(element)]for element in bfr2]
            bfr5 = [bfr0.get(bfr4[i]) for i in range(len(bfr4))]    
            return bfr5
        except:
            return lst
    
    def sort_by_date(lst,reverse=False):
        
        try:
            bfr0 = {element[0]:element for element in lst}
            bfr1 = [element[0] for element in lst]
            bfr2 = [dt.strptime(bfr1[i],"%d-%m-%Y") for i in range(len(bfr1))]
            bfr2.sort()
            if reverse:
                bfr2.reverse()
            bfr3 = {bfr1[i]:dt.strptime(bfr1[i],"%d-%m-%Y") for i in range(len(bfr1))}
            bfr4 = [list(bfr3.keys())[list(bfr3.values()).index(element)] for element in bfr2]
            bfr5 = [bfr0.get(bfr4[i]) for i in range(len(bfr4))]    
            return bfr5
        except:
            return lst
        
class Welcome(BoxLayout):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.switchnext,1.5)

    def switchnext(self,*_):
        app_ref.scmanager.transition = RiseInTransition()
        app_ref.scmanager.current="main_page"
        app_ref.todolist_page.fetch()
        Clock.schedule_once(self.reminder,1)

    def reminder(self,*_):
        Clock.schedule_once(app_ref.reminder)
        Clock.schedule_interval(app_ref.reminder,3600)

class Main(BoxLayout):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass

                
    def todolist(self,*_):
        app_ref.scmanager.transition = SlideTransition(direction="left")
        app_ref.scmanager.current = "todolistnav_page"
        if app_ref.todolistnav_page_count==0:
            app_ref.todolistnav_page.add_widget(app_ref.todolist_page)
            app_ref.todolistnav_page_count = 1
        else:
            pass
        cur.execute("select * from todolist")
        self.l=cur.fetchall()
        if len(self.l)==0:
            win_notification("To Do List","No Task Available",duration=2)
            return
        
    def more_window(self,*_):
        app_ref.scmanager.transition = SlideTransition(direction="left")
        app_ref.scmanager.current = "morewindow_page"


class MoreWindow(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass
    
    def performance_history(self,*_):
        app_ref.performancehistory_page.show()
        app_ref.scmanager.transition = SlideTransition(direction="left")
        app_ref.scmanager.current = "performancehistory_page"
    
    def change_theme(self,*_):
        app_ref.scmanager.transition = SlideTransition(direction="left")
        app_ref.scmanager.current = "changetheme_page"
        
    def back(self,*_):
        app_ref.scmanager.transition = SlideTransition(direction="right")
        app_ref.scmanager.current = "main_page"


class OverviewPopup_PerformanceHistory(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass
    
    def back(self,*_):
        self.parent.dismiss()

class AdditionalOptionsPopup_PerformanceHistory(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass
    
    def overview(self,*args):
        
        obj = OverviewPopup_PerformanceHistory()
        
        cur.execute('select distinct(task) from todolist')
        distinct_tasks = cur.fetchall() 
        cur.execute('select task from todolist')
        all_tasks = cur.fetchall()
        
        if distinct_tasks and all_tasks:
            distinct_tasks = [element[0] for element in distinct_tasks]
            all_tasks = [element[0] for element in all_tasks]
            task_count = {element:all_tasks.count(element) for element in distinct_tasks}
            '''explode = [0.2 if task_count[element]==max(list(task_count.values())) else 0 for element in distinct_tasks]'''
            obj.bxlayout.height = 700
            obj.bxlayout.add_widget(Label(text="Your Favourite Task(s)",color=(0,0,0,1),font_size=20,size_hint_y=None,height=30))
            fig1, ax1 = plt.subplots()
            ax1.plot(list(task_count.values()))
            '''ax1.pie(task_count.values(),labels=task_count.keys(),autopct='%1.1f%%',shadow=True,explode=explode)
            ax1.axis('equal')
            bfr_bxlayout = BoxLayout()
            bfr_bxlayout.size = (800,500)
            bfr_bxlayout.padding = (150,0)
            bfr_bxlayout.add_widget()'''
            obj.bxlayout.add_widget(FigureCanvasKivyAgg(plt.gcf().get))
        else:
            pass
        self.parent.dismiss()
        popup_overview = CustomPopup()
        popup_overview.padding = [(Window.size[0]-obj.width)/2,(Window.size[1]-obj.height)/2]
        popup_overview.add_widget(obj)
        popup_overview.open()
        
class PerformanceHistory(BoxLayout):
    
    dropdown_options = ['Daily','Weekly','Monthly']
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass
    
    def show(self,view_type='Weekly',*_):
        
        if len(self.bxlayout.children)!=0:
            self.bxlayout.clear_widgets()
            
        cur.execute("select * from task_progress_list")
        bfr = cur.fetchall()
        if bfr:
            bfr = SortList.sort_by_date(bfr,reverse=True)
        else:
            return
        
        if view_type == 'Daily':
            
            if bfr:
                day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
                for element in bfr:
                    date = element[0]
                    date_object = dt.strptime(date,"%d-%m-%Y")
                    if date_object >= app_ref.current_date_dt_object:
                        continue
                    if element[2] <= 0:
                        continue
                    else:
                        progress = element[1]
                        total_tasks = element[2]
                        percentage = progress*100//total_tasks
                        obj = RectangleCardLayout()
                        obj.date_label.text = date
                        obj.day_label.text = day_name[date_object.weekday()]
                        obj.tasks_completed_label.text = str(progress)
                        obj.total_tasks_label.text = str(total_tasks)
                        obj.task_progress_bar.background_color = (218/255, 223/255, 225/255, 1)
                        obj.task_progress_bar.progress_color = app_ref.fnt_fg_color
                        obj.task_progress_bar.progress = percentage
                        self.bxlayout.add_widget(obj)
                        
                        
        elif view_type == 'Weekly':
            
            if bfr:
                bfr1 = []
                for child in bfr:
                    if dt.strptime(child[0],'%d-%m-%Y') < app_ref.current_date_dt_object:
                        bfr1.append(child)
                bfr = bfr1
                week_list = []
                condition = True
                i=0
                while condition:
                    if (i+1)*7 <= len(bfr):
                        week_list.append(bfr[i*7:(i+1)*7])
                        i+=1
                    else:
                        if len(bfr)%7 == 0:
                            break
                        week_list.append(bfr[i*7:len(bfr)])
                        break
                        
                for i in range(len(week_list)):
                    obj = RectangleCardLayout()
                    obj.date_label.text = week_list[i][0][0] + ' -'
                    obj.day_label.text = week_list[i][-1][0]
                    progress=0
                    total_tasks=0
                    for j in week_list[i]:
                        progress += j[1]
                        total_tasks += j[2]
                    if total_tasks==0:
                        continue
                    percentage = progress*100//total_tasks
                    obj.tasks_completed_label.text = str(progress)
                    obj.total_tasks_label.text = str(total_tasks)
                    obj.task_progress_bar.background_color = (218/255, 223/255, 225/255, 1)
                    obj.task_progress_bar.progress_color = app_ref.fnt_fg_color
                    obj.task_progress_bar.progress = percentage
                    self.bxlayout.add_widget(obj)
                    
                    
            
        elif view_type == 'Monthly':
            
            if bfr:
                bfr1 = []
                for child in bfr:
                    if dt.strptime(child[0],'%d-%m-%Y') < app_ref.current_date_dt_object:
                        bfr1.append(child)
                bfr = bfr1
                month_list = []
                condition = True
                i=0
                while condition:
                    if (i+1)*30 <= len(bfr):
                        month_list.append(bfr[i*30:(i+1)*30])
                        i+=1
                    else:
                        if len(bfr)%30 == 0:
                            break
                        month_list.append(bfr[i*30:len(bfr)])
                        break
                        
                for i in range(len(month_list)):
                    
                    obj = RectangleCardLayout()
                    obj.date_label.text = month_list[i][0][0] + ' -'
                    obj.day_label.text = month_list[i][-1][0]
                    progress=0
                    total_tasks=0
                    for j in month_list[i]:
                        progress += j[1]
                        total_tasks += j[2]
                    if total_tasks==0:
                        continue
                    percentage = progress*100//total_tasks
                    obj.tasks_completed_label.text = str(progress)
                    obj.total_tasks_label.text = str(total_tasks)
                    obj.task_progress_bar.background_color = (218/255, 223/255, 225/255, 1)
                    obj.task_progress_bar.progress_color = app_ref.fnt_fg_color
                    obj.task_progress_bar.progress = percentage
                    self.bxlayout.add_widget(obj)
        
        self.bxlayout.height = len(self.bxlayout.children)*210   
    
    def update_view(self,instance,*args):
        self.show(view_type=instance.text)
    
    def additionaloptions(self,*_):
        
        obj = AdditionalOptionsPopup_PerformanceHistory()
        obj_popup = CustomPopup()
        x,y = self.additional_optn_btn.pos
        x1,y1 = Window.size
        obj_popup.padding = [x-obj.width,y1-y,x1-x,y-obj.height]
        obj_popup.add_widget(obj)
        obj_popup.open()
    
    def back(self,*_):
        self.bxlayout_scrollview.scroll_y = 1
        app_ref.scmanager.transition = SlideTransition(direction="right")
        app_ref.scmanager.current = "morewindow_page"

class ToDoListNav(NavigationDrawer):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.anim_type = "slide_above_simple"

class ChangeTimePopup(BoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass

    def cancel(self,*_):
        self.parent.dismiss()
        
    def changetime(self,id_no,tm_type,btn_object,*args):
        self = ChangeTimePopup()
        self.id_no = id_no
        self.tm_type = tm_type
        self.btn_object = btn_object
        if self.tm_type == "start_time":
            self.title.text = "Change Start Time"
        if self.tm_type == "end_time":
            self.title.text = "Change End Time"
        popup_changetime = CustomPopup()
        popup_changetime.add_widget(self)
        popup_changetime.padding = [(Window.size[0]-self.width)/2,(Window.size[1]-self.height)/2]
        popup_changetime.open()

    def update_time(self,*_):
        if len(self.new_time_textbox.text)==0:
            self.new_time_textbox.text = "Invalid Input"
            return
        else:
            
            if self.tm_type == "start_time":
                
                try:
                    complete_task=app_ref.todolist_page.l[self.id_no]
                    cur.execute("update todolist set start_time='{}' where id={}".format(self.new_time_textbox.text,str(complete_task[0])))
                    a.commit()
                    win_notification("To Do List","Start time updated",duration=2)
                except:
                    win_notification("To Do List","Something went wrong")
                    return

            if self.tm_type == "end_time":
                try:
                    complete_task=app_ref.todolist_page.l[self.id_no]
                    cur.execute("update todolist set end_time='{}' where id={}".format(self.new_time_textbox.text,str(complete_task[0])))
                    a.commit()
                    win_notification("To Do List","End time updated",duration=2)
                    
                except:
                    win_notification("To Do List","Something went wrong")
                    return
            self.cancel_btn.text = "Back"
            self.btn_object.text = self.new_time_textbox.text
            app_ref.current_date_dt_object_copy = dt.strptime(complete_task[1],"%d-%m-%Y")
            app_ref.todolist_page.fetch()
            app_ref.current_date_dt_object_copy = app_ref.current_date_dt_object

class ChangeDescPopup(BoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        pass

    def cancel(self,*_):
        self.parent.dismiss()
        
    def changedesc(self,id_no,*args):
        
        self = ChangeDescPopup()
        self.id_no = id_no
        popup_changedesc = CustomPopup()
        popup_changedesc.add_widget(self)
        popup_changedesc.padding = [(Window.size[0]-self.width)/2,(Window.size[1]-self.height)/2]
        popup_changedesc.open()

    def update_desc(self,*_):
        
        if len(self.new_desc_textbox.text)==0:
            self.new_desc_textbox.text = "Invalid Input"
            return
        else:
                
            try:
                complete_task=app_ref.todolist_page.l[self.id_no]
                cur.execute("update todolist set description='{}' where id={}".format(self.new_desc_textbox.text,str(complete_task[0])))
                a.commit()
                win_notification("To Do List","Description updated",duration=2)
                self.cancel_btn.text = "Back"
                app_ref.current_date_dt_object_copy = dt.strptime(complete_task[1],"%d-%m-%Y")
                app_ref.todolist_page.fetch()
                app_ref.current_date_dt_object_copy = app_ref.current_date_dt_object
                
            except:
                win_notification("To Do List","Something went wrong")

class TaskPropertyPopup(BoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.pp_10_min.bind(on_press=partial(self.postpone_task,10))
        self.pp_15_min.bind(on_press=partial(self.postpone_task,15))
        self.pp_30_min.bind(on_press=partial(self.postpone_task,30))
        self.pp_1_hr.bind(on_press=partial(self.postpone_task,60))
        self.pp_2_hr.bind(on_press=partial(self.postpone_task,120))
        self.pp_3_hr.bind(on_press=partial(self.postpone_task,180))
        

    def openpopup(self,id_no):

        self = TaskPropertyPopup()
        self.id_no = id_no
        popup_changedesc = CustomPopup()
        popup_changedesc.add_widget(self)
        popup_changedesc.padding = [(Window.size[0]-self.width)/2,(Window.size[1]-self.height)/2]
        popup_changedesc.open()

    def postpone_task(self,time,*_):

        selected_task=app_ref.todolist_page.l[self.id_no]
        current_start_time = dt.strptime(selected_task[4],"%H:%M")
        current_end_time = dt.strptime(selected_task[5],"%H:%M")
        new_start_time = current_start_time + timedelta(minutes=time)
        new_end_time = current_end_time + timedelta(minutes=time)
        new_start_time_str = dt.strftime(new_start_time,"%H:%M")
        new_end_time_str = dt.strftime(new_end_time,"%H:%M")
        
        if new_start_time >= current_end_time:
            win_notification("To Do List","Start time should be before end time",duration=3)
            return
        try:
            cur.execute("update todolist set start_time='{}' where id={}".format(new_start_time_str,str(selected_task[0])))
            if time>60:
                cur.execute("update todolist set end_time='{}' where id={}".format(new_end_time_str,str(selected_task[0])))
            a.commit()
            win_notification("To Do List","Task postponed by {} minutes".format(str(time)),duration=3)
            app_ref.current_date_dt_object_copy = dt.strptime(selected_task[1],"%d-%m-%Y")
            app_ref.todolist_page.fetch()
            app_ref.current_date_dt_object_copy = app_ref.current_date_dt_object
        except:
            win_notification("To Do List","Cannot postpone task\nSomething went wrong",duration=3)
    
    def delete_task(self,*_):

        try:
            complete_task=app_ref.todolist_page.l[self.id_no]
            cur.execute("delete from todolist where id={}".format(str(complete_task[0])))
            cur.execute("select * from task_progress_list")
            task_progress_list = cur.fetchall()
            if task_progress_list:
                task_progress_list_dates = {i:task_progress_list[i][0] for i in range(len(task_progress_list))}
                if complete_task[1] in task_progress_list_dates.values():
                    key = list(task_progress_list_dates.keys())[list(task_progress_list_dates.values()).index(complete_task[1])]
                    total_tasks = task_progress_list[key][2] - 1
                    cur.execute("update task_progress_list set total_tasks={} where date='{}' ".format(str(total_tasks),complete_task[1]))
            a.commit()
            win_notification("To Do List","Task Deleted",duration=2)
            self.dismiss()
            app_ref.current_date_dt_object_copy = dt.strptime(complete_task[1],"%d-%m-%Y")
            app_ref.todolist_page.fetch()
            app_ref.current_date_dt_object_copy = app_ref.current_date_dt_object
                
        except:
            win_notification("To Do List","Something went wrong")

class AdditionalOptionsPopup_ToDoList(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
    def del_unfinished_tasks(self,show_popup=False,popup_object=None,*_):
        
        if show_popup is True:
            confirmation_popup = CustomPopup()
            obj = ConfirmationPage()
            obj.title.text = "Delete Unfinished Task(s)"
            obj.confirm_btn.bind(on_release=partial(self.del_unfinished_tasks,popup_object=obj))
            confirmation_popup.add_widget(obj)
            confirmation_popup.padding = [(Window.size[0]-obj.width)/2,(Window.size[1]-obj.height)/2]
            confirmation_popup.open()
        
        else:
            if popup_object:
                popup_object.parent.dismiss()
            app_ref.expired_unfinished_task()
    
    def del_completed_tasks(self,show_popup=False,popup_object=None,*_):
        
        if show_popup is True:
            confirmation_popup = CustomPopup()
            obj = ConfirmationPage()
            obj.title.text = "Remove Completed Task(s)"
            obj.confirm_btn.bind(on_release=partial(self.del_completed_tasks,popup_object=obj))
            confirmation_popup.add_widget(obj)
            confirmation_popup.padding = [(Window.size[0]-obj.width)/2,(Window.size[1]-obj.height)/2]
            confirmation_popup.open()
        
        else:
            if popup_object:
                popup_object.parent.dismiss()
            cur.execute("delete from todolist where status=1")
            a.commit()
            app_ref.todolist_page.fetch()
            win_notification("To Do List","Removed Completed Task(s)",duration=2)


    def del_all_tasks(self,show_popup=False,popup_object=None,*_):
        
        if show_popup is True:
            confirmation_popup = CustomPopup()
            obj = ConfirmationPage()
            obj.title.text = "Delete All Task(s)"
            obj.confirm_btn.bind(on_release=partial(self.del_all_tasks,popup_object=obj))
            obj.confirm_btn.disabled = False
            confirmation_popup.add_widget(obj)
            confirmation_popup.padding = [(Window.size[0]-obj.width)/2,(Window.size[1]-obj.height)/2]
            confirmation_popup.open()
            
        else:
            if popup_object:
                popup_object.parent.dismiss()
            cur.execute("delete from todolist")
            app_ref.todolistnav_page.task_progress_bar.progress = 0
            a.commit()
            app_ref.todolist_page.fetch()
            win_notification("To Do List","All Task(s) Deleted",duration=2)


class JumpDatePopup(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
    def upcoming_date_taskview(self,view_date,*_):
        view_date_dt_object = dt.strptime(view_date,"%d-%m-%Y")
        app_ref.current_date_dt_object_copy = view_date_dt_object
        app_ref.todolist_page.fetch()
        app_ref.current_date_dt_object_copy = dt.strptime(app_ref.current_date,"%d-%m-%Y")
        self.parent.dismiss()

    def upcoming_available_task_date(self,*_):

        cur.execute("select distinct(date) from todolist")
        available_task_dates = cur.fetchall()
        if available_task_dates:
            available_task_dates_dt_object = [dt.strptime(element[0],"%d-%m-%Y") for element in available_task_dates]
            available_task_dates_dt_object.sort()
            available_task_dates = [dt.strftime(element,"%d-%m-%Y") for element in available_task_dates_dt_object]
        
            for date in available_task_dates:
                date_dt_object = dt.strptime(date,"%d-%m-%Y")
                if date_dt_object < app_ref.current_date_dt_object or (date_dt_object - app_ref.current_date_dt_object) > timedelta(days=4):
                    self.date_btn_gdlayout.add_widget(StrokeButton(text="{}".format(date),on_release = partial(self.upcoming_date_taskview, date),color = (0,0,0,1),size_hint = (None,None),width = 110,height = 50))
        
        self.date_btn_gdlayout.height = (len(self.date_btn_gdlayout.children)+8)*75/4
  
    
class ToDoList(BoxLayout):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    def fetch(self,*_):

        app_ref.todolistnav_page.main_win.scroll_y = 1
        self.main_box.scroll_y = 1
        self.clearlist()
        self.upcoming_available_task_date()
        self.final_list=[]
        cur.execute("select * from todolist")
        self.l=cur.fetchall()
        if len(self.l)==0:
            return
        else:
            for i in range(len(self.l)):
                lst=self.l[i]
                task_date_dt_object = dt.strptime(lst[1],"%d-%m-%Y")
                if app_ref.current_date_dt_object_copy != task_date_dt_object:
                    continue
                if lst[6]==1:
                    continue
                else:
                    self.final_list.append(lst)
            self.final_list = SortList.sort_by_start_time(self.final_list)
            for i in range(len(self.final_list)):
                lst = self.final_list[i]
                i1 = self.l.index(lst)
                task_card_label = SquareCardLayout()
                delta = app_ref.current_date_dt_object - dt.strptime(lst[1],"%d-%m-%Y")
                if app_ref.current_date_dt_object_copy == app_ref.current_date_dt_object:
                    if dt.strptime(app_ref.current_time,"%H:%M:%S") < dt.strptime(lst[4],"%H:%M"):
                        task_card_label.complete_btn.disabled = True
                    if dt.strptime(app_ref.current_time,"%H:%M:%S") > dt.strptime(lst[4],"%H:%M") and dt.strptime(app_ref.current_time,"%H:%M:%S") < dt.strptime(lst[5],"%H:%M"):
                        task_card_label.border_color = app_ref.fnt_fg_color
                    else:
                        task_card_label.border_color = app_ref.fnt_bg_color
                elif delta > timedelta(days=2) or app_ref.current_date_dt_object_copy > app_ref.current_date_dt_object:
                    task_card_label.complete_btn.disabled = True
                    
                task_card_label.task_label.text = lst[2]
                task_card_label.complete_btn.bind(on_release=partial(self.complete,i,None))
                task_card_label.view_btn.bind(on_release=partial(self.task_card,i1,lst))
                self.gdlayout.add_widget(task_card_label)
                
            self.gdlayout.height = ((len(self.gdlayout.children)/4 + 1)*280)+40

            if app_ref.current_date_dt_object_copy !=app_ref.current_date_dt_object:
                self.upcoming_date_btn_label.text = dt.strftime(app_ref.current_date_dt_object_copy,"%d")
            else:
                self.upcoming_date_btn_label.text=""

            cur.execute("select * from task_progress_list")
            task_progress_list = cur.fetchall()
            if task_progress_list:
                task_progress_list_dates = {i:task_progress_list[i][0] for i in range(len(task_progress_list))}
                local_bfr_date_str = dt.strftime(app_ref.current_date_dt_object_copy,"%d-%m-%Y")
                if local_bfr_date_str in task_progress_list_dates.values():
                    key = list(task_progress_list_dates.keys())[list(task_progress_list_dates.values()).index(local_bfr_date_str)]
                    progress = task_progress_list[key][1]
                    total_tasks = task_progress_list[key][2]
                    app_ref.todolistnav_page.task_progress_bar.progress = int(progress*100//total_tasks)
                    
    def task_card(self,i,lst,*_):
        
        obj_popup = CustomPopup()
        obj = CardLayout()
        obj.task_label_btn.text = lst[2]
        obj.task_label_btn.bind(on_press=partial(self.taskproperty,i))
        obj.description_label_btn.text = lst[3]
        obj.description_label_btn.bind(on_press=partial(self.changedesc,i))
        obj.start_time_label_btn.text = lst[4]
        obj.start_time_label_btn.bind(on_press=partial(self.changetime,i,"start_time",obj.start_time_label_btn))
        obj.end_time_label_btn.text = lst[5]
        obj.end_time_label_btn.bind(on_press=partial(self.changetime,i,"end_time",obj.end_time_label_btn))
        obj.complete_btn.bind(on_press=partial(self.complete,i,obj_popup))
        delta = app_ref.current_date_dt_object - dt.strptime(lst[1],"%d-%m-%Y")
        if dt.strptime(lst[1],"%d-%m-%Y") == app_ref.current_date_dt_object and dt.strptime(app_ref.current_time,"%H:%M:%S") < dt.strptime(lst[4],"%H:%M"):
            obj.complete_btn.disabled = True
        elif delta > timedelta(days=2) or app_ref.current_date_dt_object_copy > app_ref.current_date_dt_object:
            obj.complete_btn.disabled = True
        obj_popup.add_widget(obj)
        obj_popup.padding=[(Window.size[0]-obj.width)/2,(Window.size[1]-obj.height)/2]
        obj_popup.open()
        
            
    def complete(self,i,popup_object,btn_object):
        
        try:
            complete_task=self.final_list[i]
            cur.execute("update todolist set status=1 where id={}".format(str(complete_task[0])))
            cur.execute("select * from task_progress_list")
            task_progress_list = cur.fetchall()
            if task_progress_list:
                task_progress_list_dates = {i:task_progress_list[i][0] for i in range(len(task_progress_list))}
                if complete_task[1] in task_progress_list_dates.values():
                    key = list(task_progress_list_dates.keys())[list(task_progress_list_dates.values()).index(complete_task[1])]
                    progress = task_progress_list[key][1] + 1
                    total_tasks = task_progress_list[key][2]
                    cur.execute("update task_progress_list set progress={} where date='{}' ".format(str(progress),complete_task[1]))
                    app_ref.todolistnav_page.task_progress_bar.progress = int(progress*100//total_tasks)
            a.commit()
            win_notification("To Do List","Task Completed",duration=2)
            btn_object.disabled=True
            app_ref.current_date_dt_object_copy = dt.strptime(complete_task[1],"%d-%m-%Y")
            self.fetch()
            app_ref.current_date_dt_object_copy = app_ref.current_date_dt_object
            if popup_object is None:
                return
            popup_object.dismiss()
              
        except:
            win_notification("To Do List","Something went wrong")
                
        
    def changetime(self,id_no,tm_type,btn_object,*args):

        ChangeTimePopup.changetime(self,id_no,tm_type,btn_object)
    
    def changedesc(self,id_no,*args):

        ChangeDescPopup.changedesc(self,id_no)

    def taskproperty(self,id_no,*args):

        TaskPropertyPopup.openpopup(self,id_no)
    
    def additionaloptions(self,*_):
        
        obj = AdditionalOptionsPopup_ToDoList()
        obj_popup = CustomPopup()
        x,y = self.additional_optn_btn.pos
        x1,y1 = Window.size
        obj_popup.padding = [x-obj.width,y1-y,x1-x,y-obj.height]
        obj_popup.add_widget(obj)
        obj_popup.open()
        
    def clearlist(self,*_):

        if len(self.gdlayout.children)==0:
            pass
        else:
            self.gdlayout.clear_widgets()

        if len(self.date_btn_gdlayout.children)==0:
            pass
        else:
            self.date_btn_gdlayout.clear_widgets()
    
    def add(self,*_):
        
        popup_addtask = CustomPopup()
        obj = AddTaskPopup()
        popup_addtask.add_widget(obj)
        popup_addtask.padding = [(Window.size[0]-obj.width)/2,(Window.size[1]-obj.height)/2]
        popup_addtask.open()
    
    def back(self,*_):

        app_ref.scmanager.transition = SlideTransition(direction="right")
        app_ref.scmanager.current = "main_page"
        app_ref.current_date_dt_object_copy = dt.strptime(app_ref.current_date,"%d-%m-%Y")
        self.fetch()
        self.upcoming_date_btn_label.text=""

    def upcoming_date_taskview(self,view_date,*_):
        view_date_dt_object = dt.strptime(view_date,"%d-%m-%Y")
        app_ref.current_date_dt_object_copy = view_date_dt_object
        self.fetch()
        app_ref.current_date_dt_object_copy = dt.strptime(app_ref.current_date,"%d-%m-%Y")

    def upcoming_available_task_date(self,*_):

        self.clearlist()
        cur.execute("select distinct(date) from todolist")
        available_task_dates = cur.fetchall()
        available_task_dates_dt_object = [dt.strptime(element[0],"%d-%m-%Y") for element in available_task_dates]
        available_task_dates_dt_object.sort()
        available_task_dates = [dt.strftime(element,"%d-%m-%Y") for element in available_task_dates_dt_object]
        i=0
        for date in available_task_dates:
            if i>=5:
                break
               
            date_dt_object = dt.strptime(date,"%d-%m-%Y")
            date_only = dt.strftime(date_dt_object,"%d")
            if date_dt_object >= app_ref.current_date_dt_object:
                self.date_btn_gdlayout.add_widget(EllipseButton(text="{}".format(date_only),on_release = partial(self.upcoming_date_taskview,date),size_hint_x=None,width=40))
                i+=1
        
        if len(available_task_dates)>=6:
            
            if len(self.jump_date_bxlayout.children)!=0:
                self.jump_date_bxlayout.clear_widgets()
            obj = JumpDatePopup()
            obj.upcoming_available_task_date()
            jump_date_popup = CustomPopup()
            jump_date_popup.add_widget(obj)
            jump_date_popup.padding = ((Window.size[0]-obj.width)/2,(Window.size[1]-obj.height)/2)
            self.jump_date_bxlayout.add_widget(Button(text="^",font_size=25,bold=True,color=app_ref.fnt_fg_color,background_color=app_ref.fnt_bg_color,background_normal="",on_release=partial(jump_date_popup.open)))
    
class AddTaskPopup(BoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        pass

    def add(self,*_):

        cur.execute("select * from task_progress_list")
        task_progress_list = cur.fetchall()
        if task_progress_list:
            task_progress_list_dates = {i:task_progress_list[i][0] for i in range(len(task_progress_list))}
        date_list=self.date.text.split(",")
        for i in range(len(date_list)):
            try:
                cur.execute("insert into todolist (date,task,description,start_time,end_time,status) values ('{}','{}','{}','{}','{}',0)".format(date_list[i],self.task.text,self.description.text,self.start_time.text,self.end_time.text))
                if task_progress_list and date_list[i] in task_progress_list_dates.values():
                    key = list(task_progress_list_dates.keys())[list(task_progress_list_dates.values()).index(date_list[i])]
                    total_tasks = task_progress_list[key][2] + 1
                    cur.execute("update task_progress_list set total_tasks={} where date='{}' ".format(str(total_tasks),date_list[i]))
                else:
                    cur.execute("insert into task_progress_list values ('{}',0,1)".format(date_list[i]))
                a.commit()
                win_notification("To Do List","Task added successfully",duration=2)
            except:
                traceback.print_exc()
                win_notification("To Do List","Something went wrong\nCannot add task for\n{}".format(date_list[i]),duration=2)
                error_msg = False
                return
        app_ref.current_date_dt_object_copy = dt.strptime(date_list[0],"%d-%m-%Y")
        app_ref.todolist_page.fetch()
        app_ref.current_date_dt_object_copy = app_ref.current_date_dt_object
        self.cancel_btn.text = "Back"
        
    def back(self,*_):

        self.date.text=''
        self.task.text=''
        self.description.text=''
        self.start_time.text=''
        self.end_time.text=''
        self.parent.dismiss()

class Reminderpopup(BoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.complete_btn.disabled = False
        self.snooze_btn.disabled = False
        self.task_container = []

    def complete(self,*_):

        try:
            cur.execute("update todolist set status=1 where id={}".format(str(self.task_container[0])))
            cur.execute("select * from task_progress_list")
            task_progress_list = cur.fetchall()
            if task_progress_list:
                task_progress_list_dates = {i:task_progress_list[i][0] for i in range(len(task_progress_list))}
                if self.task_container[1] in task_progress_list_dates.values():
                    key = list(task_progress_list_dates.keys())[list(task_progress_list_dates.values()).index(self.task_container[1])]
                    progress = task_progress_list[key][1] + 1
                    total_tasks = task_progress_list[key][2]
                    cur.execute("update task_progress_list set progress={} where date='{}' ".format(str(progress),self.task_container[1]))
                    app_ref.todolistnav_page.task_progress_bar.progress = int(progress*100//total_tasks)
            a.commit()
            self.complete_btn.disabled = True
            self.parent.dismiss()
            app_ref.todolist_page.fetch()
            win_notification("TO Do List","Task Completed",duration=2)
        except:
            win_notification("TO Do List","Cannot update task status\nSomething went wrong",duration=3)
            
    def snooze(self,*args):

        Clock.schedule_once(app_ref.reminder,300)
        self.snooze_btn.disabled = True
        self.dismiss()
        
    def snooze_remind(self,message,*args):

        self.snooze_btn.disabled = False
        self.text_box.text=message
        self.open()
        

class ChangeTheme(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        clr_picker = ColorPicker()
        self.clr_picker_bxlayout.add_widget(clr_picker)
        clr_picker.bind(color=self.changetheme)

        self.theme_color = theme_fg
        self.cancel_btn.text="Cancel"
        
    def changetheme(self,instance,value):

        if value==[1.0,1.0,1.0,1]:
            return
        elif value=="btn_press":
            local_storage.put('theme_list',theme_fg=list(self.theme_color))
            app_ref.fnt_fg_color = self.theme_color
            self.cancel_btn.text="Back"
        else:
            self.theme_color = value
        
    def cancel(self,*_):

        app_ref.scmanager.transition = SlideTransition(direction="right")
        app_ref.scmanager.current = "morewindow_page"
        

class NewProject(App):

    fnt_fg_color = ListProperty()
    fnt_bg_color = ListProperty()
    
    def exit(self,*_):
    
        App.get_running_app().stop()
        Window.close()
    
    def reminder(self,*_):

        # android - slack notification

        final_list = app_ref.todolist_page.final_list
        for i in range(len(final_list)):
            
            lst=final_list[i]
            start_time = lst[4]
            end_time = lst[5]
            start_time_dt_object = dt.strptime(start_time,"%H:%M")
            end_time_dt_object = dt.strptime(end_time,"%H:%M")
            current_time = dt.now().strftime("%H:%M")
            current_time_dt_object = dt.strptime(current_time,"%H:%M")
            
            if current_time_dt_object > start_time_dt_object and current_time_dt_object < end_time_dt_object:
                message="Task: {}\n\nDescription: {}\n\nStart Time: {}\nEnd Time: {}".format(lst[2],lst[3],lst[4],lst[5])
                popup_reminder = CustomPopup()
                obj=Reminderpopup()
                obj.text_box.text = message
                obj.task_container = lst
                popup_reminder.add_widget(obj)
                popup_reminder.padding = [(Window.size[0]-obj.width)/2,(Window.size[1]-obj.height)/2]
                popup_reminder.open()
            
            if current_time_dt_object < start_time_dt_object and current_time_dt_object < end_time_dt_object:
                time_delta = start_time_dt_object - current_time_dt_object
                Clock.schedule_once(self.reminder,time_delta.seconds)
    
    def expired_task(self,*_):

        cur.execute("select * from todolist")
        self.l=cur.fetchall()
        if len(self.l)==0:
            return
        else:
            for i in range(len(self.l)):
                complete_task=self.l[i]
                task_date_dt_object = dt.strptime(complete_task[1],"%d-%m-%Y")
                if app_ref.current_date_dt_object > task_date_dt_object and complete_task[6]==1:
                    cur.execute("delete from todolist where id={}".format(str(complete_task[0])))
            a.commit()
            
    def expired_unfinished_task(self,*_):

        cur.execute("select * from todolist")
        self.l=cur.fetchall()
        if len(self.l)==0:
            win_notification("To Do List","No task available",duration=3)
            return
        else:
            j=0
            for i in range(len(self.l)):
                complete_task=self.l[i]
                task_date_dt_object = dt.strptime(complete_task[1],"%d-%m-%Y")
                if app_ref.current_date_dt_object > task_date_dt_object and complete_task[6]==0:
                    cur.execute("delete from todolist where id={}".format(str(complete_task[0])))
                    j+=1
            a.commit()
            win_notification("To Do List","{} Pending task(s) deleted".format(j),duration=3)
    
    def update_current_time(self,*_):

        self.current_time = dt.now().strftime("%H:%M:%S")
        self.todolistnav_page.current_time.text = self.current_time

    def close_app(self,*_):

        App.get_running_app().stop()
        Window.close()
    
    def build(self):
        
        sql_connection()
        
        #----------------------------------------------------------------

        self.todolistnav_page_count = 0

        #----------------------------------------------------------------
        
        self.fnt_fg_color = theme_fg
        self.fnt_bg_color = [236/255, 240/255, 241/255,1]

        self.current_date = dt.now().strftime("%d-%m-%Y")
        self.current_date_dt_object = dt.strptime(self.current_date,"%d-%m-%Y")
        self.current_date_dt_object_copy = dt.strptime(self.current_date,"%d-%m-%Y")
        
        self.current_dateonly = dt.now().strftime("%d")
        self.current_monthyearonly = dt.now().strftime("%b  %Y")
        
        self.current_time = dt.now().strftime("%H:%M:%S")
        Clock.schedule_interval(self.update_current_time,1)
        
        self.daily_quote = daily_quote()
        
        self.expired_task()
        
        self.scmanager= ScreenManager()
        
        self.welcome_page = Welcome()
        S_welcome_page = Screen(name='welcome_page')
        S_welcome_page.add_widget(self.welcome_page)
        self.scmanager.add_widget(S_welcome_page)

        self.morewindow_page = MoreWindow()
        S_morewindow_page = Screen(name='morewindow_page')
        S_morewindow_page.add_widget(self.morewindow_page)
        self.scmanager.add_widget(S_morewindow_page)
        
        self.performancehistory_page = PerformanceHistory()
        S_performancehistory_page = Screen(name='performancehistory_page')
        S_performancehistory_page.add_widget(self.performancehistory_page)
        self.scmanager.add_widget(S_performancehistory_page)
        
        self.main_page = Main()
        S_main_page = Screen(name='main_page')
        S_main_page.add_widget(self.main_page)
        self.scmanager.add_widget(S_main_page)

        self.todolistnav_page = ToDoListNav()
        S_todolistnav_page = Screen(name="todolistnav_page")
        S_todolistnav_page.add_widget(self.todolistnav_page)
        self.scmanager.add_widget(S_todolistnav_page)
        
        self.todolist_page = ToDoList()
        
        self.changetheme_page = ChangeTheme()
        S_changetheme_page = Screen(name="changetheme_page")
        S_changetheme_page.add_widget(self.changetheme_page)
        self.scmanager.add_widget(S_changetheme_page)
        
        return self.scmanager
    
Config.set('kivy', 'exit_on_escape', '0')
Window.size=(1920,1080)
Window.fullscreen=True
app_ref = NewProject()
app_ref.run()
