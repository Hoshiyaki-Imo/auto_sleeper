import pystray, time, threading, os, tomllib, subprocess
from PIL import Image
from plyer import notification

SLEEPTIME = 10 #default value

default_image = Image.open("default.png")
not_started_image = Image.open("not_started.png")
three_min_image = Image.open("3min.png")
running = True
timer = None
first = None
sleepReturn = None
icon = None
settingFilePath = None

def notify(titles : str,messages : str, icon = "icon.ico"):
    notification.notify(title=titles,
                        message=messages,
                        app_name="Auto Sleeper",
                        app_icon=icon,
                        timeout=5
                    )

def sleepReturnCheck():
    global first, icon, three_min_notification, notified
    if first:
        setSleepTime()
        first = False
    last = time.time()
    while running:
        now = time.time()
        if now - last > 10:
            notify("Welcome back!", f"Start timer and sleep in {SLEEPTIME} minutes")
            setSleepTime(saved_time)
        last = now
        time.sleep(1)
        if timer and timer.is_alive():
            remaining = int((sleep_at - time.time())/60)
            icon.title = f"Auto Sleeper({remaining}min left)"
            if remaining < 4:
                icon.icon = three_min_image
                if three_min_notification and not(notified):
                    notify("Sleep in 3 minutes", "if you extend time, please push \"Extend time\" button.", "3min.ico")
                    notified = True
        else:
            icon.title = f"Auto Sleeper(push me!)"

def setSleepTime(icon = 0, query = None):
    global timer, sleep_at
    if "Start" in str(query) and timer.is_alive():
        notify(f"Sleep in {int((sleep_at - time.time())/60)}minutes", "Do your best lol")
        return
    if "Start timer" in str(query) or query == None:
        long = SLEEPTIME * 60
        if not "Start timer" in str(query):
            long += icon
            if long >= SLEEPTIME * 60 *2:
                long = SLEEPTIME * 60 *2
        sleep_at = time.time() + long
        new_time = (SLEEPTIME + 0.5) * 60
    else:
        selected_time = int(str(query)[:-3])
        long = selected_time * 60
        sleep_at = time.time() + long
        new_time = (selected_time + 0.5) * 60
    if new_time > 90:
        makeTimer(new_time)

    else:
        notify("Too short to set!", "You have to set from two minutes", "not_started.ico")

def sleep(icon = None, query = None):
    global saved_time
    if str(query) == "Sleep right now":
        print(sleep_at - time.time())
        saved_time = sleep_at - time.time()
    subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

def extendSleepTimer(icon, extend_minutes_item):
    extend_minutes = int(extend_minutes_item.text[1:-3])
    global timer, sleep_at
    if not sleep_at:
        return
    last_timer_time = sleep_at - time.time()
    new_time = last_timer_time + extend_minutes * 60
    sleep_at = time.time() + new_time
    notify("Extend time", f"extend {extend_minutes} minutes, so sleep in {int(new_time/60)} minutes")

    makeTimer(new_time)

def makeTimer(sleep_time):
    global timer, notified
    if timer:
        timer.cancel()
    timer = threading.Timer(sleep_time, sleep)
    timer.start()
    icon.icon = default_image
    icon.menu = makeIcon()
    notified = False

def exit(icon = None, query = None):
    global running
    running = False
    sleepReturn.join()
    if timer:
        timer.cancel()
    icon.stop()

def cancelTimer(icon, query):
    if timer:
        timer.cancel()
    icon.icon = not_started_image
    icon.menu = makeIcon()

def openSettingFile(icon, query):
    if not os.path.exists(settingFilePath):
        with open(settingFilePath, "w") as f:
            f.write("# default sleeping time\nsleeping_time = 10\n# selection of extend time\nextend_time = [5]\n# selection of timer time\ntimer_time = [5]\n# yes/no three minutes notification(true/false)\nthree_min_notification = false\n")
    os.startfile(settingFilePath)

def getSettingPath():
    appdata = os.environ.get("APPDATA")
    app_dir = os.path.join(appdata, "AutoSleeper")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return os.path.join(app_dir, "setting.toml")

def makeIcon():
    global SLEEPTIME, settingFilePath, three_min_notification
    extendTime = None
    timerTime = None
    settingFilePath = getSettingPath()
    try:
        with open(settingFilePath, mode="rb") as f:
           dic = tomllib.load(f)
        SLEEPTIME = dic["sleeping_time"]
        extendTime = dic["extend_time"]
        timerTime = dic["timer_time"]
        three_min_notification = dic["three_min_notification"]
    except:
        SLEEPTIME = 10
        extendTime = []
        timerTime = []
        three_min_notification = False
        print("not found setting file")
    
    new_menu = pystray.Menu(pystray.MenuItem("Wanna exit", pystray.Menu(pystray.MenuItem("Really?", pystray.Menu(pystray.MenuItem("No", None), pystray.MenuItem("Exit", exit), pystray.MenuItem("Sleep right now", sleep))))),
                                          pystray.MenuItem("Open setting file", openSettingFile),
                                          pystray.MenuItem("Scan", scan),
                                          pystray.MenuItem("Cancel timer", cancelTimer, enabled= lambda _: timer and timer.is_alive()),
                                          pystray.MenuItem(f"Start timer({SLEEPTIME} min)", setSleepTime, default=True, enabled= lambda _: not (timer and timer.is_alive())),
                                          pystray.MenuItem("Start timer(select time)", pystray.Menu(*[pystray.MenuItem(f"{i}min", setSleepTime) for i in timerTime]), enabled = True if (len(timerTime) != 0 and not(timer and timer.is_alive())) else False, visible=True if len(timerTime) != 0 else False),
                                          pystray.MenuItem("Extend time", pystray.Menu(*[pystray.MenuItem(f"+{i}min", extendSleepTimer) for i in extendTime]), enabled=True if(len(extendTime) != 0 and timer and timer.is_alive()) else False, visible=True if len(extendTime) != 0 else False),
    )
    return new_menu

def scan(icon):
    icon.menu = makeIcon()

def main():
    global sleepReturn, icon
    icon = pystray.Icon("auto_sleeper", default_image, "Auto Sleeper",
                        menu=None
    )
    sleepReturn = threading.Thread(target=sleepReturnCheck, daemon=True)
    sleepReturn.start()
    icon.menu = makeIcon()
    icon.run()

if __name__ == "__main__":
    first = True
    sleep_at = None
    saved_time = 0
    main()