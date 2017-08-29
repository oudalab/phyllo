# phyllo
PHilologicallY Linguistic LegwOrk. 

## To run the application:

__Initial build__:
1) docker for linux (https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/) OR docker-toolbox for windows(https://www.docker.com/products/docker-toolbox) is required
2) clone or download the files from the github repository
![giphy 1](https://user-images.githubusercontent.com/22301958/29801507-95345a9a-8c35-11e7-8f58-e87db341ad66.gif)
3) unzip the zip file (if downloaded the file)
4) In linux: open terminal and navigate to the unzipped directory with _cd_ command OR
   In Windows: open up the _docker quickstart terminal_ and navigate to the unzipped directory with _cd_ command
5) run _docker-compose up_

![giphy 2](https://user-images.githubusercontent.com/22301958/29801558-db012f6c-8c35-11e7-8e3f-b4ef46c94145.gif)
6) A new or initial build is gonna take the longest of around 20 - 30 mins, since the build downloads the data from the http://www.thelatinlibrary.com/ and then generate FTS tables for them
7) The build will be done once the terminal says __debugger is active!__
![giphy 3](https://user-images.githubusercontent.com/22301958/29801720-c4fef3ce-8c36-11e7-91db-ae42c0889bf0.gif)

## To access the search engine:

8) open a browser and enter the url: http://192.168.99.100:5000/

