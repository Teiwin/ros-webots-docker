# ros-webots-docker
Docker config to run both webots and ros 

This will create a docker image for Webots and the package for it to work with ROS
You can access the Webots interface on `localhost:1234`.
If you want to modify the simulation environment, it is in the SIMU/ folder.

This will also create a docker image you can access as a terminal to run your ros project.
The folders catkin_ws and pyenv are mounted on the ros_it image so you can edit those with your favourite text editor.

Of course the controller and the name of the topics are specific to my project, as well as the simulation environment.

## create docker images

build Dockerfile_rospackage and Dockerfile_webots_ros  
`docker build -t ros_wd -f Dockerfile_rospackage .`  
`docker build -t webots_ros -f Dockerfile_webots_ros .`


## run
launch docker-compose and attach to ros_it (ros_interactive)
`docker compose up`
`docker attach ros_it`

This runs a ros master, webots, and creates and environment for you to create your packages.

If you want to run some graphical packages in the ros_it image, you just need to run the folowing comand to give the permission to write on you device screen:
`xhost +local:root`
it is a good practice to remove this permission when you're done
`xhost -local:root`


## Special for my project
you may want to publish only the topics you use for performance. You can do so by adding in the docker-compose file, line 14, the environment variable as shown in the example:
```
- LIDAR=0
- CAMERA=1
- TOF=0
```


