#!/bin/bash

cd ../stegozoa;
tmux new-session -d -s 'stegozoa' \; \
	split-window -h -p 50 \; \
	split-window -v -p 80 \; \
	select-pane -t 0 \; \
	split-window -v -p 80 \; \
	select-pane -t 0 \; \
	send-keys 'vagrant ssh stegozoa1' C-m \; \
	select-pane -t 2 \; \
	send-keys 'vagrant ssh stegozoa2' C-m \;
sleep 4;
tmux attach-session -d -t 'stegozoa' \; \
	select-pane -t 1 \; \
	send-keys 'vagrant ssh stegozoa1' C-m \; \
	select-pane -t 3 \; \
	send-keys 'vagrant ssh stegozoa2' C-m \; \
	select-pane -t 0 \; \
	send-keys 'sudo ffmpeg -nostats -re -i SharedFolder/SCDEEC\ 2020-11-23\ 16-16-58.mkv -r 30 -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video0' \; \
	select-pane -t 2 \; \
	send-keys 'sudo ffmpeg -nostats -re -i SharedFolder/SCDEEC\ 2020-11-23\ 16-16-58.mkv -r 30 -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video0' \; \
	select-pane -t 1 \; \
	send-keys 'DISPLAY=:0.0 chromium_builds/regular_build/chrome --no-sandbox $1 > output.log' \; \
	select-pane -t 3 \; \
	send-keys 'DISPLAY=:0.0 chromium_builds/regular_build/chrome --no-sandbox $1 > output.log' \; \
	detach \;
sleep 4;
tmux attach-session -d -t 'stegozoa' \; \
	new-window \; \
	split-window -h -p 50 \; \
	split-window -v -p 80 \; \
	select-pane -t 0 \; \
	split-window -v -p 80 \; \
	select-pane -t 0 \; \
	send-keys 'vagrant ssh stegozoa1' C-m \; \
	send-keys 'cd ~/stegozoa/test' C-m \; \
	select-pane -t 2 \; \
	send-keys 'vagrant ssh stegozoa2' C-m \; \
	send-keys 'cd ~/stegozoa/test' C-m \; \
	detach \;
sleep 4;
tmux attach-session -d -t 'stegozoa' \; \
	select-pane -t 1 \; \
	send-keys 'vagrant ssh stegozoa1' C-m \; \
	send-keys 'cd ~/stegozoa' C-m \; \
	send-keys 'python3 src/stegozoaClient.py 1' \; \
	select-pane -t 3 \; \
	send-keys 'vagrant ssh stegozoa2' C-m \; \
	send-keys 'cd ~/stegozoa' C-m \; \
	send-keys 'python3 src/stegozoaClient.py 2' \;
