# Why PTP?
Is the easier of the 3 options (PTP,GPS or PPS)
The guide says:
`When Livox LiDAR or Hub is connected to a network with a ptp master clock, the device will automatically synchronize its time to the master clock.`

# Installing ptp
http://linuxptp.sourceforge.net/
check status
```batch
ethtool -T eth0
```

Another option is PTP:
## PTP in Jetson
https://msadowski.github.io/pps-support-jetson-nano/

- We are suppose to add this in `tegra194-gpio.h`, not in te
```bash
pps {
    gpios = <&gpio TEGRA_GPIO(B, 7) 0>;

    compatible = "pps-gpio";
    status = "okay";
};
```
The forumla to calculate the gpiopin Sysfs is the following
TEGRA_GPIO(BB, 0)
BB = 27
27 * 8 + 0 (no offset) = 216
So in my case if we want to use pin 15 (gpio268) we have to write:
424/8 = 53

```python3
import string
list(string.ascii_lowercase + string.ascii_lowercase)

``` 

# Check Jetpack version
```bash
cat /etc/nv_tegra_release
sudo apt-cache show nvidia-jetpack
```

## Host PC
# Installing toolchain
https://docs.nvidia.com/jetson/l4t/index.html#page/Tegra%20Linux%20Driver%20Package%20Development%20Guide/xavier_toolchain.html
```bash
cd $HOME
mkdir $HOME/l4t-gcc
cd $HOME/l4t-gcc
wget -c http://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/aarch64-linux-gnu/gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz
tar xf gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz
rm gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz
export CROSS_COMPILE=$HOME/l4t-gcc/gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-
```

# Installing SDK manager
