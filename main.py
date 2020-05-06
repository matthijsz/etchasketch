from pointerclass import *
from functions import *

Options_master = tkinter_Run()
StartTime = time.time()
img = Reformat_image(Options_master['Targetfile'])
strt = start(img, method=Options_master['method'])
pntr = pointer(strt.x, strt.y, img, print_process=Options_master['Print_process'],
               Directory=Options_master['Directory'], Target=Options_master['Targetfile'])
if img[strt.y, strt.x] != 1:
    nearest_one = find_nearest_one(img, strt.x, strt.y)
    pntr.moveto(nearest_one[0], nearest_one[1])
_ = pntr.move_one_step(img)
while _:
    _ = pntr.move_one_step(img)
if 0 in pntr.visited[np.where(img == 1)]:
    while 0 in pntr.visited[np.where(img == 1)]:
        returnto_target = pntr.returnto_fast(img)
        if returnto_target:
            _ = pntr.move_one_step(img)
            while _:
                _ = pntr.move_one_step(img)
        else:
            pntr.go_to_next_block(img)
            _ = pntr.move_one_step(img)
            while _:
                _ = pntr.move_one_step(img)
pntr.finish(strt, img)
proctime = time.time() - StartTime
print('Path tracing finished in: {0}'.format(str(datetime.timedelta(seconds=proctime))))
# If requested all steps will be printed in ./Steps as png files
# Combine them with ffmpeg using the following command:
# cd ./Steps
# ffmpeg -framerate 60 -i step_%d.png -c:v libx264 out.mp4
# To rotate counterclockwise:
# ffmpeg -i out.mp4 -vf "transpose=2" out_rot.mp4
# Speed up video 5X with:
# ffmpeg -i out.mp4 -filter:v "setpts=0.2*PTS"  -c:v libx264 out_x4.mp4
