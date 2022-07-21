# Sony camera connection
The camera is connected to the system in three diferent ways:
- Battery: The default battery is quite small and force us to remove the camera out of the system all the time. To avoid this we use a 5V voltage regulator to be able to keep the camera on for longer time and keep it fix in the system
- Hotshoe: Allow us to detect the exact moment when a picture has been captured
- USB trigger: Allow us to trigger an event

# Battery:
We use a [dummy battery](https://www.amazon.de/dp/B07DMXX9W6/ref=pe_27091401_487024491_TE_item) that we connect to a voltage regulator

# Hotshoe
The hotshoe has three connections: 
- Voltage
- GND
- SIGN
Every time that we capture a picture there is a shortcut that produce a small voltage in the SIGN. To avoid multiple detections from the GPIO, we use a a 1k resistance between SIGN and VOLTAGE for the camera as the XAVIER NX do not have internal resistance 

# USB trigger
The USB trigger has three connections:
- Voltage
- Focus
- Trigger
At difference of other connections the camera expect a lower impedance (less voltage) when a picture want to be captured. It also requiered to happens in both focus and trigger at the same time. To do this we use GPIO pins at HIGH level and set to LOW when a picture want to be captured. Additionaly similar to the hotshoe a 1k resistance was set in the focus (green cable) and trigger (red cable). This avoid malfunctioning.

# Usefull links:
