## What is Anubis?
Anubis is an application created as a part of a bachelor thesis. The application allows user to connect GenICam compliant devices from various vendors without need to use multiple applications. The cameras can be used to acquire images and save them to the hard drive. Cameras can also be configured using GenICam nodes. The application also implements a Tensorflow library which allows user to load up their ANN models and use them for training as well as for classification.

![alt text](./Help/whole_app.png "Application preview")

## How to run
To run this application you need to install all the dependencies specified in the requirements.txt file. To ease things up you can use the conda_environment.yml file which will import the environment automatically. For this to work you should use Anaconda navigator application. Bear in mind that you might still need to insatll Vimba manually.

When you have everything prepared you can run the anubis.py script or you can proceed to building the app for it to be executable without a need for a Python environment on the host computer.

## Building the app
The application is diustributed in a form of source files and can be run from any IDE or via console by running the anubis.py file. In case you want to create executable that is not dependent on any external libraries, you can follow this short tutorial. Please note that the application was tested mainly by running it inside of a python environment and the executable can contain some unforeseen bugs.

NAVOD

## Development
The application will most likely not be further developed, however if it is used in some classes, the bugs that will arise will be fixed. Whole application is written to be modular and as such anyone can develop it further and create forks of this project.

## Documentation
Documentation is written using Doxygen and can be generated using doxygen command inside root directory. The html version of the documentation can be found here. More information about the project, used tools etc. Can be found in the bachelor thesis itself which is accessible in the czech language on this [link](https://www.vutbr.cz).
