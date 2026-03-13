import pystray, time, threading, os, tomllib
from PIL import Image

SLEEPTIME = 10 #default value

image = Image.open("digital_detox_auto_sleeper.png")
running = True
timer = None
first = None
sleepReturn = None

def sleepReturnCheck():
    global first
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

def setSleepTime(icon = None, query = None):
    global timer, sleep_at
    sleep_at = time.time() + SLEEPTIME * 60
    new_time = (SLEEPTIME + 0.5) * 60
    makeTimer(new_time)

def sleep():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def extendSleepTimer(icon, extend_minutes_item):
    extend_minutes = 0
    if str(extend_minutes_item) == "5min":
        extend_minutes = 5
    elif str(extend_minutes_item) == "10min":
        extend_minutes = 10
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
    timer = threading.Timer(sleep_time, sleep)
    timer.start()
    print("make new timer")

def exit(icon = None, query = None):
    global running
    running = False
    sleepReturn.join()
    if timer:
        timer.cancel()
    icon.stop()

def ignoreTimer(icon, query):
    if timer:
        timer.cancel()
        print(timer)
    print(timer)

def main():
    global sleepReturn, SLEEPTIME
    sleepReturn = threading.Thread(target=sleepReturnCheck, daemon=True)
    sleepReturn.start()
    try:
        with open("setting.toml", mode="rb") as f:
           dic = tomllib.load(f)
           SLEEPTIME = dic["sleeping_time"]
    except:
        SLEEPTIME = 10
        print("not found setting file")
    print("sleeping time seted " + str(SLEEPTIME))
    icon = pystray.Icon("auto_sleeper", image, "auto_sleeper", 
                        menu=pystray.Menu(pystray.MenuItem("Ignore", ignoreTimer, enabled= lambda _: timer and timer.is_alive()),
                                          pystray.MenuItem("Start timer", setSleepTime, enabled= lambda _: not (timer and timer.is_alive())),
                                          pystray.MenuItem("Extend time", pystray.Menu(pystray.MenuItem("5min", extendSleepTimer), pystray.MenuItem("10min", extendSleepTimer))), 
                                          pystray.MenuItem("Wanna exit", pystray.Menu(pystray.MenuItem("Really?", pystray.Menu(pystray.MenuItem("No", None), pystray.MenuItem("Exit", exit))))))
                                          )
    icon.run()

if __name__ == "__main__":
    first = True
    sleep_at = None
    main()