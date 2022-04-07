1. Configure GPIO:
```bash
sudo /opt/nvidia/jetson-io/jetson-io.py
```

2. Install GPIO

```bash
python3 -m pip install --upgrade pip
python3 -m pip install Jetson.GPIO
```


sudo groupadd -f -r gpio
sudo usermod -a -G gpio aspen
sudo cp /home/aspen/Agroscope/Python_venvironments/YOLO_v5_DeepSort_venv/lib/python3.8/site-packages/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger


3. **Copy new rules**
```bash
sudo cp lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d/
```