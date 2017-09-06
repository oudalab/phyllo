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
![giphy](https://user-images.githubusercontent.com/22301958/30137061-46749e12-9327-11e7-87e5-48f787393130.gif)
![giphy 1](https://user-images.githubusercontent.com/22301958/30137090-5c4deafe-9327-11e7-84ba-8f56c176d75b.gif)
2) __word*__: in the search gets all the documents where the '__word__' is a _prefix_. __*__ can be used multiple times like __word1* word2* word3*__
![multi star](https://user-images.githubusercontent.com/22301958/30137112-7a5edaa8-9327-11e7-9a7e-7d97face3e1f.gif)
![star](https://user-images.githubusercontent.com/22301958/30137113-7a61ad8c-9327-11e7-905e-dbfc26903e22.gif)
3) __^word__: this search gets all the documents with sentences where '__word__' is the first word. can only be used once in a search and 
__^word*__: this gets all the documents where is '__word__' is a _prefix_ of the first word in a sentence
![star with start](https://user-images.githubusercontent.com/22301958/30137152-ae64009e-9327-11e7-9498-a7b00ace9f81.gif)
![multi star with start](https://user-images.githubusercontent.com/22301958/30137155-b1278030-9327-11e7-997e-c151cbbb5de9.gif)
4) to search author names or book titles:
   __author:name__ or  __title:name__ should be used
![author](https://user-images.githubusercontent.com/22301958/30137208-e75fc900-9327-11e7-9a85-bbecb19b36e8.gif)

![book](https://user-images.githubusercontent.com/22301958/30137309-53e41018-9328-11e7-84c0-9921384b1919.gif)
5) the search __author:name word__ searches for the documents where the authored by the specified author and contains the specified word
![author-word](https://user-images.githubusercontent.com/22301958/30137257-15ef0b78-9328-11e7-897b-ee6afe8999c5.gif)

![book-word](https://user-images.githubusercontent.com/22301958/30137308-53e372a2-9328-11e7-80c4-cabd8e1cb4cb.gif)
6) __author:name word*__ can also be used
![author star](https://user-images.githubusercontent.com/22301958/30137354-85b9d38e-9328-11e7-9be9-e405614e2d34.gif)
7) Also __author:name ^word*__ can also be searched
![author](https://user-images.githubusercontent.com/22301958/30137389-b227b6e8-9328-11e7-8c88-7a191612f431.gif)
8) __word1 OR word2__:
this kind of search results all the documents which contain either word1 or word2
![or](https://user-images.githubusercontent.com/22301958/30137268-28bfc44a-9328-11e7-90fc-a71f916b6ef3.gif)
9) The NEAR clause can be used to search for non continous words. For example, two words can have any number of words and characters between them an estimate of that number can be used to perform searches as well. __word1 NEAR/estimated number of characters word2__
![nearsingle](https://user-images.githubusercontent.com/22301958/30137417-d267d104-9328-11e7-8f85-f1cad38f2728.gif)
NEAR clause can be used multiple times through the query.






