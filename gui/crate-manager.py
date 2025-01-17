 #!/usr/bin/env python3
 # -*- coding: utf-8 -*-

__author__ = "seanwlk"
__copyright__ = "Copyright 2019"
__license__ = "GPL"
__version__ = "1.9"

import sys, os
import datetime,time
import requests
import json
import steam.webauth as wa
import steam.steamid as sid
import steam.util.web as sweb
from collections import OrderedDict
from io import StringIO
import lxml.html
from tkinter import *
from tkinter import ttk,simpledialog,messagebox

s = requests.Session()

def check_for_updates(silent=False):
    def latest_ver():
        ver = requests.get("https://api.github.com/repos/seanwlk/warface-crate-manager/releases/latest").json()
        return ver['tag_name']
    print("Looking for udpates")
    if __version__ < latest_ver():
        messagebox.showwarning("New version available!","You are currently running a different version than the latest release available. Please update.")
    else:
        if not silent:
            messagebox.showinfo("No updates available","You are currently running the latest version of the project.")

def resources():
    print("Opening available resources window")
    resources_window = Tk()
    resources_window.title("Resources")
    resources_window.resizable(False, False)
    resources_window.geometry("225x130")
    main_json = s.get("https://{}/minigames/craft/api/user-info".format(base_url)).json()
    level1=main_json['data']['user_resources'][0]['amount']
    level2=main_json['data']['user_resources'][1]['amount']
    level3=main_json['data']['user_resources'][2]['amount']
    level4=main_json['data']['user_resources'][3]['amount']
    level5=main_json['data']['user_resources'][4]['amount']

    current_res_labels = ttk.Labelframe(resources_window, text='Current Resources')
    current_res_labels.grid(row=0,column=0,sticky = W)
    Label(current_res_labels, text="Level 1: {}".format(level1)).grid(row=0,column=0,sticky = W)
    Label(current_res_labels, text="Level 2: {}".format(level2)).grid(row=1,column=0,sticky = W)
    Label(current_res_labels, text="Level 3: {}".format(level3)).grid(row=2,column=0,sticky = W)
    Label(current_res_labels, text="Level 4: {}".format(level4)).grid(row=3,column=0,sticky = W)
    Label(current_res_labels, text="Level 5: {}".format(level5)).grid(row=4,column=0,sticky = W)

    Label(resources_window).grid(row=0,column=1,sticky = W) #Space

    converted_res = ttk.Labelframe(resources_window, text='If all converted')
    converted_res.grid(row=0,column=2,sticky = W)
    Label(converted_res, text="Level 1: {}".format(level1%50)).grid(row=0,column=0,sticky = W)
    level2 = level2 + int(level1/50)
    Label(converted_res, text="Level 2: {}".format(level2%50)).grid(row=1,column=0,sticky = W)
    level3 = level3 + int(level2/50)
    Label(converted_res, text="Level 3: {}".format(level3%35)).grid(row=2,column=0,sticky = W)
    level4 = level4 + int(level3/35)
    Label(converted_res, text="Level 4: {}".format(level4%25)).grid(row=3,column=0,sticky = W)
    level5 = level5 + int(level4/25)
    Label(converted_res, text="Level 5: {}".format(level5)).grid(row=4,column=0,sticky = W)

def crate_date(end_at):
    if end_at > 0:
        return "Opens in {}".format(str(datetime.timedelta(seconds=end_at)))
    else:
        return "Crate Open"

def crates():
    print("Opening available crates window")
    crates_window = Tk()
    crates_window.title("Crates")
    crates_window.resizable(False, False)
    crates_window.geometry("250x200")
    main_json = s.get("https://{}/minigames/craft/api/user-info".format(base_url)).json()
    Label(crates_window).grid(row=0,column=1,sticky = W)
    Label(crates_window, text="Type").grid(row=0,column=1,sticky = N)
    Label(crates_window, text="Status").grid(row=0,column=2,sticky = N)
    for index,crate in enumerate(main_json['data']['user_chests']):
        square_icon = Canvas(crates_window, width=15, height=15)
        square_icon.grid(row=index+1,column=0,sticky = W)
        if crate['type'] == "platinum":
            square_icon.create_rectangle(0, 0, 15, 15, fill="black")
        elif crate['type'] == "gold":
            square_icon.create_rectangle(0, 0, 15, 15, fill="yellow")
        elif crate['type'] == "silver":
            square_icon.create_rectangle(0, 0, 15, 15, fill="silver")
        elif crate['type'] == "common":
            square_icon.create_rectangle(0, 0, 15, 15, fill="white")
        Label(crates_window, text="{}".format(crate['type'].capitalize())).grid(row=index+1,column=1,sticky = W)
        Label(crates_window, text="{}".format("New" if crate['state'] == "new" else crate_date(crate['ended_at']))).grid(row=index+1,column=2,sticky = W)

class VerticalScrolledFrame:
    def __init__(self, master, **kwargs):
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        bg = kwargs.pop('bg', kwargs.pop('background', None))
        self.outer = Frame(master, **kwargs)

        self.vsb = Scrollbar(self.outer, orient=VERTICAL)
        self.vsb.pack(fill=Y, side=RIGHT)
        self.canvas = Canvas(self.outer, highlightthickness=0, width=width, height=height, bg=bg)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vsb.set
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vsb['command'] = self.canvas.yview

        self.inner = Frame(self.canvas, bg=bg)
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            return getattr(self.outer, item)
        else:
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion = (0,0, x2, max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units" )
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units" )

def weekly_challenges():
    print("Opening weekly challenges window")
    weekly_challenges_window = Tk()
    weekly_challenges_window.title("Berserk missions to complete")
    weekly_challenges_window.resizable(False, True)
    weekly_challenges_window.geometry("800x550")

    tabDisplayer = ttk.Notebook(weekly_challenges_window)
    tabDisplayer.pack(fill="x", expand=True)
    for i in range(1,20):
        req = s.get("https://{url}/minigames/bp5/tasks/week-tasks?week={week}".format(url=base_url,week=i)).json()
        if len(req['data']) == 0:
            break
        weekFrame = Frame(tabDisplayer)
        weekFrame.pack(fill="x", expand=True)
        Label(weekFrame,text="Available from {}".format(time.ctime(req['data'][0]['started_at']))).pack()
        for task in req['data']:
            taskFrame = Frame(weekFrame,borderwidth=2,relief=GROOVE,highlightthickness=1,highlightcolor="light grey")
            taskFrame.pack(fill="x", expand=True)
            Label(taskFrame,text="{}".format(task['descr'])).grid(row=0,sticky = W)
            Label(taskFrame,text="Progress: {progress}/{target} | EXP: {exp} | Skip cost: {skip} | To do in one game: {one_game}".format(progress=task['progress'],target=task['target_count'],exp=task['exp'], skip=task['skip_cost'], one_game = "YES" if task['is_one_game'] == 1 else "NO")).grid(row=1,sticky = W)
            if task['status'] == "completed":
                Label(taskFrame,text="\u2713",fg="green",font=("Arial", 18)).grid(row=0,rowspan=2, column=1,sticky = E)
        tabDisplayer.add(weekFrame,text="Week {}".format(i))


def undone_missions():
    print("Opening undone missions window")
    todo_missions = Tk()
    todo_missions.title("Berserk missions to complete")
    todo_missions.geometry("800x400")
    # main frame that contains multiple generated mission frames
    missionList = VerticalScrolledFrame(todo_missions)
    missionList.pack(fill="x", expand=True)
    for i in range(1,20):
        req = s.get("https://{url}/minigames/bp5/tasks/week-tasks?week={week}".format(url=base_url,week=i)).json()
        if len(req['data']) == 0:
            break
        for task in req['data']:
            if task['status'] == "progress" and time.time() > task['started_at']:
                missionFrame = Frame(missionList,borderwidth=2,relief=GROOVE,highlightthickness=1,highlightcolor="light grey")
                missionFrame.pack(fill="x", expand=True)
                Label(missionFrame,text="Week {}".format(i)).grid(row=0,sticky = W)
                Label(missionFrame,text="{}".format(task['descr'])).grid(row=1,sticky = W)
                Label(missionFrame,text="Progress: {progress}/{target} | EXP: {exp} | Skip cost: {skip} | To do in one game: {one_game}".format(exp=task['exp'], skip=task['skip_cost'], progress=task['progress'],target=task['target_count'], one_game = "YES" if task['is_one_game'] == 1 else "NO")).grid(row=2,sticky = W)

    missionList.pack(side = LEFT, fill = BOTH)

def go_profile():
    def level_progress(exp,prev,next):
        next -= prev
        exp -= prev
        # next : 200 = exp : x
        return int((200*exp) / next)
    def open_crates():
        personal_crates =  Tk()
        personal_crates.title("Opening Personal Crates")
        personal_crates.resizable(False, True)
        personal_crates.geometry("400x200")
        cratescroll = VerticalScrolledFrame(personal_crates)
        cratescroll.pack(fill="x", expand=True)
        uprofile = s.get("https://{}/minigames/bp5/user/info".format(base_url)).json()
        get_mg_token()
        response = s.post("https://{}/minigames/personal_box/api/open".format(base_url), data={'count' : uprofile['data']['personal_boxes']}).json()
        for item in response['data']['rewards']:
            itemFrame = Frame(cratescroll,borderwidth=2,relief=GROOVE,highlightthickness=1,highlightcolor="light grey")
            itemFrame.pack(fill="x", expand=True)
            Label(itemFrame,text="{}".format(item['title'])).grid(row=0,sticky = W)
            try:
                Label(itemFrame,text="{}".format("Permanent" if 'permanent' in item['item'] else ("Amount: {}".format(item['item']['count']) if 'consumable' in item['item'] else "{0} {1}".format(item['item']['duration'],item['item']['duration_type']) ))).grid(row=1,sticky = W) # Assuming that duration_type can be permanet. Untested.
            except:
                print(str(item)) # Mainly for debug since it was failing with Armageddon under  certain conditions
                pass

    def start_mission(missionType,which_mission,energy):
        get_mg_token()
        for research in which_mission['data']:
            if research['type'] == missionType:
                if energy >= research['requirements']['energy']:
                    req = s.post("https://{}/minigames/bp6/research/start".format(base_url),data={"research_id":research['id']}).json()
                    messagebox.showinfo("Starting {} research".format(missionType), "{} starting.".format(req['state']))
                else:
                    messagebox.showinfo("Starting {} research".format(missionType), "Not enough energy to start this mission. \nYour energy: {energy}\nRequired: {required}".format(energy=energy,required=research['requirements']['energy']))
        go_profile_wind.destroy()
        go_profile()

    def upgrade_base():
        to_upgrade = s.get("https://{}/minigames/bp6/colony/upgrades".format(base_url)).json()
        user_response = messagebox.askquestion('Base upgrade','Are you sure you want to upgrade base?\nRequirements\n{bp} BP\n{res} Resources'.format(bp=to_upgrade['data']['next_level']['battle_points'],res=to_upgrade['data']['next_level']['resources']),icon = 'warning')
        if user_response == "yes":
            get_mg_token()
            req = s.post("https://{}/minigames/bp6/colony/unlock-level".format(base_url)).json()
            print(str(req))
            messagebox.showinfo("Base upgrade", "{} upgrading.".format(req['state']))
        go_profile_wind.destroy()
        go_profile()

    def get_research_reward(missionType):
        get_mg_token()
        req = s.post("https://{}/minigames/bp6/research/take-rewards".format(base_url),data={"research_id":missionType}).json()
        rewards = {
            "currency" : "Resources",
            "experience" : "Experience",
            "chest_key" : "Crate key",
            "personal_box" : "Personal crate"
        }
        if not len(req['data']) == 0:
            for reward in req['data']:
                if "reward" in reward and (reward['reward']['type'] == "currency" or reward['reward']['type'] == "experience"):
                    messagebox.showinfo("Collecting research rewards", "You got {amount} {what}".format(amount=reward['reward']['count'],what=rewards[reward['reward']['type']]))
                elif "reward" in reward and (reward['reward']['type'] == "chest_key" or reward['reward']['type'] == "personal_box"):
                    messagebox.showinfo("Collecting research rewards", "You got a {what}".format(what=rewards[reward['reward']['type']]))
            go_profile_wind.destroy()
            go_profile()
        else:
            messagebox.showinfo("Collecting research rewards", "Mission Failed.")
            go_profile_wind.destroy()
            go_profile()
    print("Opening global operation profile")
    go_profile_wind = Tk()
    go_profile_wind.title("Berserk Profile")

    go_profile_wind.geometry("400x360")
    uprofile = s.get("https://{}/minigames/bp5/user/info".format(base_url)).json()
    daily_task = s.get("https://{}/minigames/bp5/daily/user-task".format(base_url)).json()
    Label(go_profile_wind, text="Level: {}".format(uprofile['data']['level'])).grid(row=0,sticky = W)
    progressFrame = Frame(go_profile_wind)
    progressFrame.grid(row=1,sticky = W)
    levelup = ttk.Progressbar(progressFrame,orient=HORIZONTAL,length=200,mode='determinate')
    levelup.grid(row=0,column=0,sticky = W)
    levelup['value'] = level_progress(uprofile['data']['exp'],uprofile['data']['prev_exp'],uprofile['data']['next_exp'])
    Label(progressFrame, text="{exp} / {next}".format(exp=uprofile['data']['exp'],next=uprofile['data']['next_exp'])).grid(row=0,column=1,sticky = W)

    Label(go_profile_wind, text="Battlepoints: {}".format(uprofile['data']['points'])).grid(row=2,sticky = W)
    Label(go_profile_wind, text="Total missions completed: {}".format(uprofile['data']['progress'])).grid(row=3,sticky = W)

    perboxes = Frame(go_profile_wind)
    perboxes.grid(row=4,sticky = W)
    Label(perboxes, text="Personal crates: {}".format(uprofile['data']['personal_boxes'])).grid(row=0,sticky = W)
    if uprofile['data']['personal_boxes'] > 0:
        Button(perboxes, bd =2,text='Open all crates',command=open_crates).grid(row=1,sticky=W)

    Label(go_profile_wind, text="Colony resources: {}".format(uprofile['data']['colony_resources'])).grid(row=5,sticky = W)
    baseFrame = Frame(go_profile_wind)
    baseFrame.grid(row=6,sticky = W)
    Label(baseFrame, text="Base level: {}".format(uprofile['data']['base_level'])).grid(row=0,sticky = W)
    Button(baseFrame, bd=1,text='Upgrade base',command=upgrade_base).grid(row=1,sticky=W)

    base_mission = Frame(go_profile_wind)
    base_mission.grid(row=7,sticky = W)
    which_mission = s.get("https://{}/minigames/bp6/research/list".format(base_url)).json()
    if "time_left" not in str(which_mission['data']): # No hate for this pls
        energy_req=s.get("https://{}/minigames/bp6/colony/upgrades".format(base_url)).json()
        Label(base_mission,text="No research in progress").grid(row=0,sticky=W)
        Label(base_mission,text="Energy: {energy}/{max_energy}".format(energy=energy_req['data']['energy']['energy'],max_energy=energy_req['data']['energy']['energy_limit'])).grid(row=1,sticky=W)
        Button(base_mission, bd =2,text='Start short research',command=lambda: start_mission("short",which_mission,energy_req['data']['energy']['energy'])).grid(row=2,column=0,sticky=W)
        Button(base_mission, bd =2,text='Start long research',command=lambda: start_mission("long",which_mission,energy_req['data']['energy']['energy'])).grid(row=2,column=1,sticky=W)
    else:
        for research in which_mission['data']:
            if 'time_left' in research:
                if research['time_left'] == 0:
                    Label(base_mission,text="Your research finished, collect reward.").grid(row=0,sticky=W)
                    missionType = research['id']
                    Button(base_mission, bd =2,text='Collect',command=lambda: get_research_reward(missionType)).grid(row=1,sticky=W)
                elif research['time_left'] != 0:
                    Label(base_mission,text="Base missions ends in: {}".format(datetime.timedelta(seconds=uprofile['data']['base_mission']))).grid(row=0,sticky=W)

    Label(go_profile_wind).grid(row=8,sticky = W) # Free line
    Label(go_profile_wind, text="Daily mission").grid(row=9,sticky = W)
    missionFrame = Frame(go_profile_wind,borderwidth=2,relief=GROOVE,highlightthickness=1,highlightcolor="light grey")
    missionFrame.grid(row=10,sticky = W)
    Label(missionFrame,text="{}".format(daily_task['data']['descr'])).grid(row=1,sticky = W)
    Label(missionFrame,text="Progress: {progress}/{target} | EXP: {exp} | To do in one game: {one_game}".format(exp=daily_task['data']['exp'], progress=daily_task['data']['progress'],target=daily_task['data']['target_count'], one_game = "YES" if daily_task['data']['is_one_game'] == 1 else "NO")).grid(row=2,sticky = W)
    if daily_task['data']['progress'] >= daily_task['data']['target_count']:
        Label(missionFrame,text="\u2713",fg="green",font=("Arial", 18)).grid(row=1,rowspan=2, column=1,sticky = E)

def main_app():
    check_for_updates(silent=True)
    def append_out_text(text):
        out_text.configure(state='normal')
        out_text.insert(END,"\n{}".format(text))
        out_text.configure(state='disabled')
    def check_crates():
        main_json = s.get("https://{}/minigames/craft/api/user-info".format(base_url)).json()
        if len(main_json['data']['user_chests']) != 0:
            for chest in main_json['data']['user_chests']:
                if str(chest['state']) == 'new':
                    get_mg_token()
                    url = "https://{}/minigames/craft/api/start".format(base_url)
                    data_start_opening = {
                        'chest_id':chest['id']
                        }
                    req = s.post(url,data=data_start_opening).json()
                    if req['state'] == "Success":
                        append_out_text("[{actiontime}] New {chest_type} crate available! {start_result} opening, ID: {chestid}".format(actiontime=time.strftime('%b %d %T'),chest_type=chest['type'],start_result=req['state'],chestid=req['data']['id']))
                elif chest['ended_at'] < 0:
                    get_mg_token()
                    data_to_open = {
                        'chest_id':chest['id'],
                        'paid':0
                        }
                    url = "https://{}/minigames/craft/api/open".format(base_url)
                    req = s.post(url,data=data_to_open)
                    to_open_json = json.loads(req.text)
                    append_out_text("[{actiontime}] {chest_type} crate opening...\n    Content -> Level: {level} | Amount: {amount}".format(actiontime=time.strftime('%b %d %T'),chest_type=chest['type'],level=to_open_json['data']['resource']['level'],amount=to_open_json['data']['resource']['amount']))
        app.after(30000,check_crates)

    def check_mission(missionType):
        which_mission = s.get("https://{}/minigames/bp6/research/list".format(base_url)).json()
        if "time_left" not in str(which_mission['data']): # No hate for this pls
            energy_req=s.get("https://{}/minigames/bp6/colony/upgrades".format(base_url)).json()
            energy = energy_req['data']['energy']['energy']
            for research in which_mission['data']:
                if research['id'] == missionType:
                    print(research['id'])
                    if energy >= research['requirements']['energy']:
                        get_mg_token()
                        req = s.post("https://{}/minigames/bp6/research/start".format(base_url),data={"research_id":research['id']}).json()
                        append_out_text(
                            "[{actiontime}] Starting research ({mission})"
                            .format(actiontime=str(time.strftime('%b %d %X')),
                                    mission=research['type']))
                        check_mission(missionType)
                    else:
                        append_out_text(
                            "[{actiontime}] Not enough energy ({energy}) to start this mission"
                            .format(actiontime=str(time.strftime('%b %d %X')),
                                    energy=energy))
                        app.after(1800000, check_mission, missionType)
        else:
            for research in which_mission['data']:
                if 'time_left' in research:
                    if research['time_left'] == 0:
                        get_mg_token()
                        req = s.post("https://{}/minigames/bp6/research/take-rewards".format(base_url),data={"research_id":research['id']}).json()
                        rewards = {
                            "currency" : "Resources",
                            "experience" : "Experience",
                            "chest_key" : "Crate key",
                            "personal_box" : "Personal crate"
                        }
                        if not len(req['data']) == 0:
                            for reward in req['data']:
                                if "reward" in reward and (reward['reward']['type'] == "currency" or reward['reward']['type'] == "experience"):
                                    append_out_text("[{actiontime}] Collecting research rewards: You got {amount} {what}".format(
                                            actiontime=str(
                                                time.strftime('%b %d %X')),
                                            amount=reward['reward']['count'],
                                            what=rewards[reward['reward']['type']]))
                                elif "reward" in reward and (reward['reward']['type'] == "chest_key" or reward['reward']['type'] == "personal_box"):
                                    append_out_text("[{actiontime}] Collecting research rewards: You got a {what}".format(
                                            actiontime=str(
                                                time.strftime('%b %d %X')),
                                            what=rewards[reward['reward']['type']]))
                                check_mission(missionType)
                        else:
                            append_out_text("[{actiontime}] Collecting research rewards: No rewards".format(
                                    actiontime=str(time.strftime('%b %d %X'))))
                            check_mission(missionType)
                    elif research['time_left'] != 0:
                        uprofile = s.get(
                            "https://{}/minigames/bp5/user/info".format(
                                base_url)).json()
                        append_out_text(
                            "[{actiontime}] Mission ending in {seconds}"
                            .format(
                                actiontime=str(time.strftime('%b %d %X')),
                                seconds=datetime.timedelta(
                                    seconds=uprofile['data']['base_mission'])))
                        app.after(uprofile['data']['base_mission'] * 1000, check_mission, missionType)
                        #Label(base_mission,text="Base missions ends in: {}".format(datetime.timedelta(seconds=uprofile['data']['base_mission']))).grid(row=0,sticky=W)
    global task_history
    task_history = {}
    def check_tasks():
        temp = {}
        get_mg_token()
        for i in range(1,12):
            req = s.get("https://{url}/minigames/bp5/tasks/week-tasks?week={week}".format(url=base_url,week=i)).json()
            if len(req['data']) == 0:
                break
            temp[i] = {}
            for j, task in enumerate(req['data']):
                temp[i][j] = (task['status'] == "progress")
                global task_history
                if task_history == {}:
                    continue
                if temp[i][j] != task_history[i][j]:
                    append_out_text(
                        "[{actiontime}] Task Completed : Week {week} / Task {task}. {description}"
                        .format(
                            actiontime=str(time.strftime('%b %d %X')),
                            week=i,
                            task=j+1,
                            description=task['descr'] if not LoginType.get() == "mailru" else translator.translate(task['descr']).text))

        task_history = temp
        #append_out_text(
        #    "[{actiontime}] Task List updated"
        #    .format(actiontime=str(time.strftime('%b %d %X'))))
        app.after(60000, check_tasks)


    print("Opening Main app")
    login_window.destroy()
    user_check_json = s.get('https://{}/minigames/bp/user-info'.format(base_url)).json()
    app = Tk()
    app.title("Warface Crate Manager - {}".format(user_check_json['data']['username']))
    app.resizable(False, False)
    app.geometry("700x400")
    menubar = Menu(app)
    goOp = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Berserk", menu=goOp)
    goOp.add_command(label="Profile", command=go_profile)
    goOp.add_command(label="Weekly Challenges", command=weekly_challenges)
    goOp.add_command(label="Undone missions", command=undone_missions)
    menubar.add_command(label="Resources", command=resources)
    menubar.add_command(label="Crates", command=crates)
    menubar.add_command(label="About", command=about_window)
    menubar.add_command(label="Update", command=check_for_updates)
    menubar.add_command(label="Config", command=config_window)
    # display the menu
    app.config(menu=menubar)

    out_text = Text(app,  width=85)
    out_text.pack()
    user_check_json = s.get('https://{}/minigames/bp/user-info'.format(base_url)).json()
    out_text.insert(END,"Logged in as {}".format(user_check_json['data']['username']))
    app.after(30000,check_crates)

    try:
        if CREDS[CREDS['LoginType']]['missiontype'] == "0":
            append_out_text(
            "[{actiontime}] Automatic mission starting is disabled".format(
                actiontime=str(time.strftime('%b %d %X'))))
        else:
            mType = "short" if CREDS[CREDS['LoginType']]['missiontype'] == "1" else "long"
            which_mission = s.get(
                "https://{}/minigames/bp6/research/list".format(
                    base_url)).json()
            for research in which_mission['data']:
                if research['type'] == mType:
                    append_out_text(
                        "[{actiontime}] Automatically starting {mType} missions"
                        .format(actiontime=str(time.strftime('%b %d %X')),
                                mType=mType))
                    app.after(5000,check_mission,research['id'])
    except KeyError:
        append_out_text(
            "[{actiontime}] Automatic mission starting is disabled".format(
                actiontime=str(time.strftime('%b %d %X'))))
    task_history = {}
    app.after(20000, check_tasks)
    app.mainloop()

def config_window():
    print("Opening Config window")

    config_app = Tk()
    config_app.title("Config")
    config_app.resizable(False, False)
    config_app.geometry("250x100")
    uprofile = s.get(
        "https://{}/minigames/bp5/user/info".format(base_url)).json()
    base_level = uprofile['data']['base_level']
    Label(config_app, text="\nMission to start automatically").grid(row=0, column=0, sticky=W)
    MissionType = StringVar(master=config_app)

    def save_config():
        config_app.destroy()
        CREDS[CREDS['LoginType']]['missiontype'] = MissionType.get()
        with open('creds.json','w') as json_file:
            json.dump(CREDS, json_file, indent=4, sort_keys=True)
        messagebox.showinfo(
            "Config Saved",
            "You need to restart the app in order to enable the new config"
        )

    try:
        MissionType.set(CREDS[CREDS['LoginType']]['missiontype'])
    except KeyError:
        MissionType.set("0")

    mission_selector = Frame(config_app)
    mission_selector.grid(row=1, columnspan=3,sticky = W)
    Radiobutton(mission_selector,
                text="None",
                variable=MissionType,
                value="0").grid(row=1, column=0, sticky=W)

    if base_level>=1:
        Radiobutton(mission_selector,
                    text="Short",
                    variable=MissionType,
                    value="1").grid(row=1, column=1, sticky=W)

    if base_level>=2:
        Radiobutton(mission_selector,
                    text="Long",
                    variable=MissionType,
                    value="2").grid(row=1, column=2, sticky=W)

    submit = Button(config_app,
                    bd=2,
                    text='Save',
                    command=save_config).grid(row=3, column=1)



def about_window():
    print("Opening About window")
    about_app = Tk()
    about_app.title("About")
    about_app.resizable(False, False)
    about_app.geometry("400x200")
    Label(about_app, text="\nDesigned by").pack()
    Label(about_app, text="seanwlk",fg="Light sky blue", font=("Helvetica", 16)).pack()
    Label(about_app, text="Version: {}".format(__version__)).pack()
    Label(about_app, text="Email: seanwlk@my.com").pack()
    Label(about_app, text="\nPowered by Python 3",font=("Calibri", 10)).pack()

def get_mg_token():
    get_token = s.get('https://{}/minigames/user/info'.format(base_url)).json()
    s.cookies['mg_token'] = get_token['data']['token']

def steam_oAuthLogin(steamguard, token):
    steamguard = steamguard.split("||")
    steamid = sid.SteamID(steamguard[0])

    response = s.post('https://api.steampowered.com/IMobileAuthService/GetWGToken/v1/', data={'access_token': token}).json()['response']

    # No token in response
    if not 'token' in response or not 'token_secure' in response:
        return False

    # Build cookie list
    cookies = {
        'steamLogin': str("{id}||{token}".format(id=steamid, token=response['token'])),
        'steamLoginSecure': str("{id}||{token}".format(id=steamid, token=response['token_secure'])),
        'steamMachineAuth' + str(steamid): steamguard[1],
        'sessionid': sweb.generate_session_id()
    }

    # Create cookie jar
    jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies:
        jar.set(cookie, cookies[cookie], domain='steamcommunity.com', path='/')

    return jar

def steam_login():
    # Steam login process by sumfun4WF & Harmdhast
    if 'steam' in CREDS:
        # Relog using saved tokens
        if 'auth_token' in CREDS["steam"] and 'steamguard_token' in CREDS["steam"]:
            authcookies = steam_oAuthLogin(CREDS['steam']['steamguard_token'], CREDS['steam']['auth_token'])
            s.cookies.update(authcookies)

    if not 'sessionid' in s.cookies.get_dict():
        user = wa.MobileWebAuth(email.get(), password.get()) #MobileAuth should keep session alive
        try:
            user.login()
        except wa.CaptchaRequired:
            captcha_code = simpledialog.askstring("Captcha Code", "{}".format(user.captcha_url),parent=login_window)
            user.login(captcha=captcha_code)
        except wa.EmailCodeRequired:
            email_code = simpledialog.askstring("Email Code", "CODE",parent=login_window)
            user.login(email_code=email_code)
        except wa.TwoFactorCodeRequired:
            tfa_code = simpledialog.askstring("2 Factor", "CODE",parent=login_window)
            user.login(twofactor_code=tfa_code)
        # Save auth token for later session restore
        with open('creds.json','w') as json_file:
            CREDS['steam']['auth_token'] = user.oauth_token
            CREDS['steam']['steamguard_token'] = "{id}||{token}".format(id=user.steam_id.as_64, token=user.session.cookies.get_dict()["steamMachineAuth{id}".format(id=user.steam_id.as_64)])
            json.dump(CREDS, json_file, indent=4, sort_keys=True)
        # Copy cookies to session
        s.cookies.update(user.session.cookies)

    while True:
        try:
            entrance=s.get('https://auth-ac.my.com/social/steam?continue=https://account.my.com/social_back/?continue=https://wf.my.com/en/&failure=https://account.my.com/social_back/?soc_error=1&continue=https://wf.my.com/en/')
            openid_login={}
            html = StringIO(entrance.content.decode())
            tree = lxml.html.parse(html)
            root = tree.getroot()
            for form in root.xpath('//form[@name="loginForm"]'):
                for field in form.getchildren():
                    if 'name' in field.keys():
                        openid_login[field.get('name')]=field.get('value')
            s.headers.update({'referer': entrance.url})
            steam_redir=s.post('https://steamcommunity.com/openid/login', data=openid_login)
            s.get('https://auth-ac.my.com/sdc?from=https%3A%2F%2Fwf.my.com')
            get_token = s.get('https://wf.my.com/minigames/user/info').json()
            s.cookies['mg_token'] = get_token['data']['token']
            s.cookies['cur_language'] = op_lang()
        except:
            continue
        break
    main_app()

def mycom_login():
    payload = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.9,it;q=0.8',
        'Connection':'keep-alive',
        'Content-Type':'application/x-www-form-urlencoded',
        'Cookie':'s=dpr=1; amc_lang=en_US; t_0=1; _ym_isad=1',
        'DNT':'1',
        'Origin':'https://wf.my.com',
        'Referer':'https://wf.my.com/battlepass',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
    login_data = {
        'email':email.get(),
        'password':password.get(),
        'continue':'https://account.my.com/login_continue/?continue=https%3A%2F%2Faccount.my.com%2Fprofile%2Fuserinfo%2F',
        'failure':'https://account.my.com/login/?continue=https%3A%2F%2Faccount.my.com%2Fprofile%2Fuserinfo%2F',
        'nosavelogin':'0'
        }
    while True:
        try:
            s.post('https://auth-ac.my.com/auth',headers=payload,data=login_data)
            s.get('https://auth-ac.my.com/sdc?from=https%3A%2F%2Fwf.my.com')
            s.get('https://wf.my.com/')
            get_token = s.get('https://wf.my.com/minigames/user/info').json()
            s.cookies['mg_token'] = get_token['data']['token']
            s.cookies['cur_language'] = op_lang()
        except:
            continue
        break
    main_app()

def mailru_login():
    # <3 Harmdhast
    payload = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.9,it;q=0.8',
        'Connection':'keep-alive',
        'Content-Type':'application/x-www-form-urlencoded',
        'Cookie':'s=dpr=1; amc_lang=en_US; t_0=1; _ym_isad=1',
        'DNT':'1',
        'Origin':'https://wf.mail.ru',
        'Referer':'https://wf.mail.ru/battlepass',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
    s.get('https://auth.mail.ru/cgi-bin/auth?Login={mail}&Password={pwd}&FakeAuthPage=https%3A%2F%2Fwf.mail.ru%2Fauth'.format(mail=email.get(),pwd=password.get()))
    main_app()

def op_lang(*args):
    langs={
        "English" : "en",
        "Français" : "fr",
        "Deutsch" : "de",
        "Polski" : "pl",
        "Russian" : "ru",
        "中文" : "cn"
    }
    return langs[go_language.get()]

### LOGIN WINDOW
def login(event=None):
    global base_url
    CREDS['LoginType'] = LoginType.get()
    # Create LoginType key if it doesn't exist
    if not LoginType.get() in CREDS:
        CREDS[LoginType.get()] = {}
    # Reset saved tokens if username changes
    if LoginType.get() == "steam" and 'email' in CREDS['steam']:
        if not CREDS['steam']['email'] == email.get():
            CREDS[LoginType.get()] = {}
    CREDS[LoginType.get()]['email'] = email.get()
    CREDS[LoginType.get()]['password'] = password.get()
    with open('creds.json','w') as json_file:
        json.dump(CREDS, json_file, indent=4, sort_keys=True)
    if LoginType.get() == "mycom":
        print ("Login as My.com")
        base_url = "wf.my.com"
        mycom_login()
    elif LoginType.get() == "steam":
        print ("Login as Steam")
        base_url = "wf.my.com"
        steam_login()
    elif LoginType.get() == "mailru":
        print ("Login as Mail.ru")
        base_url = "wf.mail.ru"
        mailru_login()

def loginSelected(*args):
    try:
        email.set(CREDS[LoginType.get()]['email'])
    except KeyError:
        email.set("")
    try:
        password.set(CREDS[LoginType.get()]['password'])
    except KeyError:
        password.set("")

login_window = Tk()
login_window.resizable(False, False)
login_window.geometry("350x120")
login_window.title("Login")

email = StringVar() #Email variable
password = StringVar() #Password variable
LoginType = StringVar() # select login service, at the time only steam, mycom and mailru

if os.path.isfile('./creds.json'):
    with open('creds.json','r') as json_file:
        CREDS = json.load(json_file)
    try:
        LoginType.set(CREDS['LoginType'])
    except KeyError:
        LoginType.set("mycom")
    try:
        email.set(CREDS[CREDS['LoginType']]['email'])
    except KeyError:
        email.set("")
    try:
        password.set(CREDS[CREDS['LoginType']]['password'])
    except KeyError:
        password.set("")
else:
    CREDS = {}
    LoginType.set("mycom")

login_selector = Frame(login_window)
login_selector.grid(row=0, columnspan=3,sticky = W)
# Mycom true/false
Radiobutton(login_selector, text="My.com", variable=LoginType, value="mycom", command=loginSelected).grid(row=0,column=0,sticky = W)
# Steam true/false
Radiobutton(login_selector, text="Steam", variable=LoginType, value="steam", command=loginSelected).grid(row=0,column=1,sticky = W)
# Mail.ru true/false
Radiobutton(login_selector, text="Mail.ru", variable=LoginType, value="mailru", command=loginSelected).grid(row=0,column=2,sticky = W)

# Email field
Label(login_window, text="Email").grid(row=1,column=0,sticky = W)
emailEntry = Entry(login_window, textvariable=email, width=40)
emailEntry.grid(row=1,column=1,sticky = W)
emailEntry.focus()

# Password field
Label(login_window, text="Password").grid(row=2,column=0,sticky = W)
passEntry = Entry(login_window, textvariable=password, show='*')
passEntry.grid(row=2,column=1,sticky = W)

Label(login_window, text="Language").grid(row=3,column=0,sticky = W)
go_language=ttk.Combobox(login_window, width=10, values=["English","Français","Deutsch","Polski","Russian","中文"],state='readonly')
go_language.current(0)
go_language.grid(row=3,column=1,sticky = W) # Global operation language

# Login button
submit = Button(login_window, bd =2,text='Login',command=login).grid(row=4,column=1)
login_window.bind('<Return>',login)

login_window.mainloop()

### END LOGIN WINDOW
