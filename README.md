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

![giphy 4](https://user-images.githubusercontent.com/22301958/29802172-5289c988-8c39-11e7-985d-7823ba5134d8.gif)

## Type of searches that can be performed:

1) The search engine works for any number of words and sentences
2) __word*__: in the search gets all the documents where the '__word__' is a _prefix_. __*__ can be used multiple times like __word1* word2* word3*__
3) __^word__: this search gets all the documents with sentences where '__word__' is the first word. can only be used once in a search
4) __^word*__: this gets all the documents where is '__word__' is a _prefix_ of the first word in a sentence
5) to search author names or book titles:
   __author:name__ or  __title:name__ should be used
6) the search __author:name word__ searches for the documents where the authored by the specified author and contains the specified word
7) __word1 OR word2__:
this kind of search results all the documents which contain either word1 or word2
<more to be updated...> 





