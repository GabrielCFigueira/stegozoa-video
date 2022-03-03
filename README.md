# Stegozoa

## Build

1 - Launch the VMs in the vagrant/stegozoa folder by running `vagrant up`: cloning the chromium repo may take several hours, and requires more that 4GB of RAM (at least 8?) and at least 60 GB disk space.

2 - Compile chromium by running the following command in the scripts folder `ansible-playbook compile.yml --extra-vars "build=regular_build"`, where build variable should be the name of the macros file to use.

3 - Set resolution and camera configs by running `ansible-playbook setup.yml`

Stegozoa is now ready to go!

## Run
In both VMs:

Stegozoa: `python3 src/stegozoaClient.py <peerId>`

Video camera: `sudo ffmpeg -nostats -re -i SharedFolder/some_video.mp4 -r 30 -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video0`

Chromium: `DISPLAY=:0.0 chromium_builds/regular_build/chrome --no-sandbox https://whereby.com/<chatroomId> > output.log`

Warning: You may need to access the graphical interface of the VM on the first time launching chromium with that chatroom link. If the website supports it (whereby does), enable automatic entrance in the video room, so that next time this isn't necessary.

## Code

In `src/stegozoa_hooks` you will find the code that is bundled with Chromium, which implements the embedding and extraction functions. The set of files present in `libvpx_patches` replaces key libvpx files in order to call this code (likewise for webrtc in `webrtc_patches`). The stegozoa library (`src/libstegozoa.py`) communicates with these hooks through named pipes, exposing an API in order to support communication.

## Tests

For normal usage and tests, use the regular\_build and no\_stegozoa\_build macro files. For steganalysis and psnr/ssim tests, use stats\_stegozoa and stats\_no\_stegozoa macro files.

### Throughput

Run the test/upload.py file in one VM and test/download.py in the other VM. Press Ctrl+C to obtain the average throughput.

### Steganalysis

For jitsi, we need a dropbox account: https://www.dropbox.com/install-linux

`cd ~ && wget -O - "https://www.dropbox.com/download?plat=lnx.x86_64" | tar xzf -`
`~/.dropbox-dist/dropboxd`

Whereby can also be used for recording, but you may need a premium account.

Adjust the file test/sender\_image\_quality.py for recording videos. After recording the videos, you will need to train a steganalysis classifier based on features extracted from the videos, and compute its accuracy.

Adjust the test/automate.py file in order to correctly record video calls (coordinates of mouse clicks can become outdated).

### PSNR

Two symlinks are needed in each VM in other to share frames (and compute the PSNR/SSIM). For example, create two folders in the `SharedFolder` of vagrant, `1to2` and `2to1`. In VM1, run:

`ln -sf ~/SharedFolder/1to2 writing`

`ln -sf ~/SharedFolder/2t01 reading`

VM2:

`ln -sf ~/SharedFolder/1to2 reading`

`ln -sf ~/SharedFolder/2t01 writing`

Computing the PSNR/SSIM only works in P2P calls (for example, whereby in small room mode), because we require the sequential sending and receiving of frames (calls not in p2p can suffer from simulcast where encoded frames are not obligatory sent to the other endpoint)
