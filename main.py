import pystray, time, threading, os, tomllib, sys
from PIL import Image

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

def sleepReturnCheck():
    global first, icon
    if first:
        setSleepTime()
        first = False
    last = time.time()
    while running:
        now = time.time()
        if now - last > 10:
            setSleepTime()
            print("returned")
        last = now
        time.sleep(1)
        if timer and timer.is_alive():
            remaining = int((sleep_at - time.time())/60)
            icon.title = f"Auto Sleeper({remaining}min left)"
            if remaining < 4:
                icon.icon = three_min_image
        else:
            icon.title = f"Auto Sleeper(push start button)"

def setSleepTime(icon = None, query = None):
    global timer, sleep_at
    if str(query) == "Start timer" and timer.is_alive():
        return
    if str(query) == "Start timer" or query == None:
        long = SLEEPTIME * 60
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
        print("too short")

def sleep():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def extendSleepTimer(icon, extend_minutes_item):
    extend_minutes = int(extend_minutes_item.text[1:-3])
    global timer, sleep_at
    if not sleep_at:
        return
    last_timer_time = sleep_at - time.time()
    new_time = last_timer_time + extend_minutes * 60
    sleep_at = time.time() + new_time

    makeTimer(new_time)

    print("extended"+ str(extend_minutes) + "min")

def makeTimer(sleep_time):
    global timer
    if timer:
        timer.cancel()
        print()
    timer = threading.Timer(sleep_time, sleep)
    timer.start()
    icon.icon = default_image
    print("make new timer")

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
        print(timer)
    icon.icon = not_started_image

def openSettingFile(icon, query):
    if not os.path.exists(settingFilePath):
        with open(settingFilePath, "w") as f:
            f.write("sleeping_time = 10\nextend_time = [5,10]\ntimer_time = [5]\n")
    os.startfile(settingFilePath)

def restart():
    os.execv(sys.executable, ['python'] + sys.argv)

def getSettingPath():
    appdata = os.environ.get("APPDATA")
    app_dir = os.path.join(appdata, "AutoSleeper")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return os.path.join(app_dir, "setting.toml")

def main():
    global sleepReturn, SLEEPTIME, icon, settingFilePath
    settingFilePath = getSettingPath()
    try:
        with open(settingFilePath, mode="rb") as f:
           dic = tomllib.load(f)
        SLEEPTIME = dic["sleeping_time"]
        extendTime = dic["extend_time"]
        timerTime = dic["timer_time"]
    except:
        SLEEPTIME = 10
        extendTime = [5]
        timerTime = []
        print("not found setting file")
    print("sleeping time set " + str(SLEEPTIME))
    extendTimeMenuItems = [pystray.MenuItem(f"+{i}min", extendSleepTimer) for i in extendTime]
    icon = pystray.Icon("auto_sleeper", default_image, "Auto Sleeper",
                        menu=pystray.Menu(pystray.MenuItem("Wanna exit", pystray.Menu(pystray.MenuItem("Really?", pystray.Menu(pystray.MenuItem("No", None), pystray.MenuItem("Exit", exit))))),
                                          pystray.MenuItem("Open setting file", openSettingFile),
                                          pystray.MenuItem("Restart", restart),
                                          pystray.MenuItem("Cancel timer", cancelTimer, enabled= lambda _: timer and timer.is_alive()),
                                          pystray.MenuItem("Start timer", setSleepTime, default=True, enabled= lambda _: not (timer and timer.is_alive())),
                                          pystray.MenuItem("Start timer(select time)", pystray.Menu(*[pystray.MenuItem(f"{i}min", setSleepTime) for i in timerTime]), enabled = True if (len(timerTime) != 0 and not(timer and timer.is_alive())) else False),
                                          pystray.MenuItem("Extend time", pystray.Menu(*extendTimeMenuItems)), 
                                          )
    )
    sleepReturn = threading.Thread(target=sleepReturnCheck, daemon=True)
    sleepReturn.start()
    icon.run()

if __name__ == "__main__":
    first = True
    sleep_at = None
    main()