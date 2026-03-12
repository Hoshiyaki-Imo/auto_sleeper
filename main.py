import pystray, time, threading, os
from PIL import Image

SLEEPTIME = 10

image = Image.open("digital_detox_auto_sleeper.png")
running = True
timer = None
first = None

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

def setSleepTime():
    global timer, sleep_at
    if timer:
        timer.cancel()
    sleep_at = time.time() + SLEEPTIME * 60
    timer = threading.Timer((SLEEPTIME + 0.5) * 60, sleep) #+0.5は一応の時間
    timer.start()

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

    if timer:
        timer.cancel()

    timer = threading.Timer(new_time, sleep) #+0.5は一応の時間
    timer.start()
    print("extended"+ str(extend_minutes) + "min")

def after_click(icon, query):
    if str(query) == "":
        pass
    elif str(query) == "Exit":
        running = False
        if timer:
            timer.cancel()
        icon.stop()

def main():
    sleepReturn = threading.Thread(target=sleepReturnCheck)
    sleepReturn.start()
    icon = pystray.Icon("auto_sleeper", image, "auto_sleeper", menu=pystray.Menu(pystray.MenuItem("Extend time", pystray.Menu(pystray.MenuItem("5min", extendSleepTimer), pystray.MenuItem("10min", extendSleepTimer))), pystray.MenuItem("Exit", after_click)))
    icon.run()

if __name__ == "__main__":
    first = True
    main()