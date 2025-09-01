# rpi-led-controller
Python code that controls the LED sign in the SCE room

We rely on sce_sign.exe, which is complied from a separate repo,
 https://github.com/kammce/sce-led-sign/

the current os of the pi in the room is
```
# uname -a
Linux raspberrypi 5.10.103-v7+ #1529 SMP Tue Mar 8 12:21:37 GMT 2022 armv7l GNU/Linux
```

docker version
```
# docker --version
Docker version 20.10.17, build 100c701

# docker-compose --version
docker-compose version 1.21.0, build unknown
```

### Setting up pi from scratch
- [ ] download this raspbian version from
 https://ftp.jaist.ac.jp/pub/raspberrypi/raspios_armhf/images/raspios_armhf-2022-01-28/
- [ ] write os to sd card, turn on pi + connect, enable ssh, verify os
```
# uname -a
Linux raspberrypi 5.10.92-v7+ #1514 SMP Mon Jan 17 17:36:39 GMT 2022 armv7l GNU/Linux
```
- [ ] install docker with https://get.docker.com/, run the command with
```
sudo sh install-docker.sh --version 5:20.10.17~3-0~raspbian-bullseye

# add user to docker group
sudo usermod -aG docker pi

# log out or reboot, so the change applies
sudo reboot
```
- [ ] install docker-compose
- [ ] verify docker with
```
$ docker --version
Docker version 20.10.17, build 100c701
$ docker compose version
Docker Compose version v2.39.1
```
- [ ] follow the below sound module steps
- [ ] clone this repo, do `docker compose up --build`

### disabling sound module for rpi-rgb-led-matrix
```sh
# check if sound module is loaded
lsmod | grep snd_bcm2835

# edit these files, reboot after:

# add `isolcpus=3` on its own line in
/boot/cmdline.txt

# add `blacklist snd_bcm2835` on its own line in
/etc/modprobe.d/blacklist-rgb-led-matrix.conf

# comment out dtparam=audio=on, add dtparam=audio=off to
/boot/config.txt
```

### Compiling text-scroller
This is just to test if your hardware is connected properly.
```sh
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
make all

# go to where text scroller is
cd rpi-rgb-led-matrix/utils/

# you may need to install this
sudo apt-get install libgraphicsmagick++-dev

make all; make make text-scroller

# test it out
sudo ./text-scroller \
    --led-chain=2 \
    --led-rows=32 \
    --led-cols=64 \
    --led-gpio-mapping=adafruit-hat-pwm \
    --led-slowdown-gpio=2 \
    -s 10 \
    -B 0,255,0 \
    -C 255,0,0 \
    -O 0,0,255 \
    --led-brightness=48 \
    -f ../fonts/10x20.bdf \
    -y 5 test
```

