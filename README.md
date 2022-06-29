# ASPEN
 AgroScope PhENotyping tool

ASPEN project has as main goal to create a tool that can be used along diferent domains of agriculture (*i.e.* greenhouses, orchards, field, etc.) as a phenotyping tool for identify, quantify and measure diferent topics of agricultural interestes as for example yield, pest and diseases presence, stress, etc. For this, a group of diferent sensors are used to create a 3D reconstruction of the scanned environment what allow to obtain relevant data in two different configurations (Real time and postprocessing).

## UML
<div align="center">
<img src="https://github.com/Camilochiang/ASPEN/blob/main/Software/Images/20220419_UML_diagram.png" width="100%" />
</div>


## Acknowledge
ASPEN project rely in several other works, here mentioned:
- [Yolov5](https://github.com/ultralytics/yolov5)
- [R3Live](https://github.com/hku-mars/r3live)
- [Pixloc](https://github.com/cvg/pixloc)
- [Sort](https://github.com/abewley/sort)

## Warning:
This repository is research in process!

## ToDO:
Several improvements are in the pipeline of the project. Either contributions or personal work from the author can implement them in the near future
- [ ] Allow diferent objet detection algorithms
- [ ] Implement [YOLOv6](https://github.com/meituan/YOLOv6)
- [ ] Speed calculator for optimal high resolution cover
- [ ] Expose LiDAR intensity values
- [ ] Point cloud colorizing using multispectral values (radiance)
- [ ] Point cloud correction using DSL2 light sensor for radiance to reflectance transformation
- [ ] Implement SLAM loop closure using [A-LOAM](https://github.com/gisbi-kim/FAST_LIO_SLAM) or similar
- [ ] GPS integration for point cloud alignment as postprocesing
- [ ] Tool transference to rover car for automatic data adquisition