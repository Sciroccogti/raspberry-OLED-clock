# raspberry-OLED-clock

使用了 2.42寸 OLED（128*64）+ 树莓派 zero w

## I2C

要使用 `i2c-0`，需在 `raspi-config` 中关闭 *camera* ，然后在 `/boot/config.txt` 中加一行 `dtparam=i2c_vc=on`。
重启后 `sudo i2cdetect -y 0` 就能读到连接的设备。

## Reference

- [luma.oled](https://github.com/rm-hull/luma.oled)
- [FontChinese7x7](https://github.com/Angelic47/FontChinese7x7)
- [Raspberry Pi Pinout](https://pinout.xyz/pinout/i2c)
