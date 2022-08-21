
import time

sec = 0
cnt_frame = 0
PER_FRAME = 33
while True:
    sec = cnt_frame / PER_FRAME
    time.sleep(1 / 30)

    print(f'Sec : {sec}')
    if sec < 3:
        cnt_frame += 1
        continue
    
    print("OVER 3")
    break

