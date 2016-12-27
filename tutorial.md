# TUTORIAL DRAFT
## How to code one of these crazy scraper things.

### Introduction
A lot of people like to code Python from the command line, and that's okay, if you know how to do that. A lot of other people code from an IDE, which is great, because it's pretty much like every other IDE out there. For beginners and experts alike, I would recommend PyCharm as an IDE for coding Python.

Of course, other than an IDE, you will need Python itself. Because what we will be working with today requires multiple different libraries/packages/etc., I like to use [Anaconda](https://www.continuum.io/downloads). It has more than we need, but, it's a lot easier than trying to figure out how to install things into python itself. These scrapers are written in Python 3, so make sure you get Python 3.

Once you have both Anaconda and your favorite IDE installed, you'll likely need to change the project's interpreter. The IDE will usually ask you do this, or you can change it from File ` Settings ` Project ` Project Interpreter. You can then navigate to python from your Anaconda installation folder. For those who understand how to use the console, python can be accessed from the Anaconda folder.

The code we reference today are `sallustDB.py` and `0_template.py`. We will be mostly focusing on prose. The very last section references `phaedrusDB.py`, but focuses on the poetry portion of that code.

### But first, the database schema.
Before we actually do any coding, it's important to know what you want from the code. In this section, we'll describe the database schema, which is just a table full of things we'll have the code scrape for us. Later on, when the code is finished, you'll want to check the database table to make sure nothing is in the wrong place and no cells are left empty. I use SQLBrowser, but there are a handful of other similar applications that will do the job.

That database we will be working with is called `texts.db` and the table inside of it is called `texts`. The former is just a file, and the latter can be created with the statement 
```python
curs.execute('CREATE TABLE texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
            ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
            ' link TEXT, documentType TEXT`)
```
Some of the python files in the repository already create tables. This statement will not work if a table has already been created, so, typically, we will have a 'CREATE TABLE IF NOT EXISTS` instead. However, much of the code in the repository does not include a create statement as it assumes a table exists.

The table includes the following:
`id` is a unique integer assigned to each entry in the table.
`title` is the name of the collection.
`book` is the name of the work inside the collection.
`language` is the self-explanatory, but, for this project, it is generally always Latin.
`author` is the author's name, which is usually similar to the collection title.
`date` is the time period in which the author lived.
`chapter` is usually the chapter number, but, sometimes, it may also be a string.
`verse` is similar to chapter, except it is more likely to be a number.
`passage` is the actual line -- the main content with text in the entry.
`link` is simply a URL to the work in which the entry can be located.
`documentType` is either prose or poetry. The focus of this tutorial is prose.

### Well, once that's sorted out, it's time to start coding.
There are a few things you'll need to import first.
```python
import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
```
sqlite3 is what we use for our SQL commands, but don't let it bother you if you don't know SQL -- it's not used very often for this project. SQL, however, is very easy to learn, and [w3schools](http://www.w3schools.com/sql/default.asp) provides a decent tutorial. urllib and urlopen deal with getting content from webpages.
re deals with string manipulation and regular expressions, which we will mostly use for splitting strings. Regular expressions are very important to know, so you might need some [documentation](https://docs.python.org/3/library/re.html) on how it works.
BeautifulSoup is fairly important -- there are two versions, 3 and 4, but we will be using version 4. Most of these imports don't particular require much knowledge to use since we only take two or three statements from them, but knowledge of Beautiful Soup is fairly important for HTML navigation. The documentation Beautiful Soup is found [here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

#### main(), part 1
It is apparently good practice to encapsulate your main code in its own function, often with `def main():`. The last two lines below that are outside of the function block allow the program to execute the code in main().
```python
# main code
def main():
    # The collection URL below. In this example, we have a link to Sallust.
    collURL = 'http://thelatinlibrary.com/sall.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

if __name__ == '__main__':
    main()
```
As you can tell, our first few lines in the main function are where we're going to see lots of BeautifulSoup and string manipulation. It might be a lot to take in, so we'll break it down step by step. Especially since Sallust isn't going to be the collection you're scraping, probably.

`collURL` is the variable I use for the the collection's website, which is generally reachable from the main page, `http://www.thelatinlibrary.com/`. Usually, it will list a set of literary works that the author of that collection has made.

`collOpen` stores the website once it has been opened by urllib. This is going to be the only place we'll ever see urllib and urlopen.

`collSOUP` is where we finally use BeautifulSoup to obtain the source HTML and store it all in one variable. Granted, it's not just a text of the source; it's a BeautifulSoup object with BeautifulSoup functions, allowing us to navigate the HTML. The second argument in that line, `html5lib`, is the parser I decided to use. It seems to work.

As for navigation via BeautifulSoup, `author`, `colltitle`, and `date` display this well. Respectively, they can be found in `title` tags, `h1` tags, and `h2` tags. The people who originally wrote the HTML for these collections did not always follow the same patterns, however, so it may be useful to look at the site's HTML source to find what you need. Notice that these values are not strings until we append `.string` to the end; we also append `.strip()` to get rid of any extra whitespace characters or newlines.

The last line of our main function is a variable that stores the return value of another function, `getBooks()`.

#### getBooks()
Of course, when calling the following function, one needs to pass in a BeautifulSoup object. Preferably, this object would be the collSOUP object, which is the soup of the collection we are working with.
```python
def getBooks(soup):
    siteURL = 'http://www.thelatinlibrary.com'
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))
    return textsURL
```
The main purpose of this function lies within the for loop. What it does is find links in the passed in BeautifulSoup object via `a` tags with attribute 'href'. It is then appended to the `siteURL` using `.format()`  and stored in the list `textsURL`.

The next part of the function removes unnecessary links from the list. Often times, it will be those two listed in the code block above, but other times it may include /medieval.html or some other site. Regardless of what it may be, the ones we want to remove are links that do not lead to written works of the author. Typically, the loop originally adds these links in because the bottom of the page has hyperlinks directing towards other parts of the site.

#### main(), part 2
After we store that list of URLs, we will need a loop to run through each link. Keep in mind that we have moved back to the inside of the main() function.
```python
    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='Sallust'")
```
Firstly, we have a `with ... as` statement. What this statement does is create a connection via sqlite3 to the database stored in 'texts.db', a database file, and name the connection object `db`. Using `with` will automatically close the db when it reaches the end of what it encapsulates, so we don't need to worry about closing it.

Next, we have a cursor() object named `c`. This cursor is important as it will assist in executing SQL statements, as displayed in the next line. `.execute()` runs an SQL statement, and it is always a string. Wrap it with double-quotes, because you will need to use single-quotes for strings inside the SQL statement. In this example, what we execute is deleting everything in our table that has been called `texts` with the author "Sallust." Take note that the name of the table is important.

I mentioned a loop before. It needs to be contained within the with statement:
```python
	for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            # finally, pick ONE case to parse with.
```
The loop takes each URL inside the list and performs a similar task to what we saw in main() part 1, where we opened a URL with urlopen and turn it into a BeautifulSoup object. The next couple lines attempt to discern where the title is located, as it sometimes varies from URL to URL. Sometimes, the `title` tag will contain the author's name, a colon, and then the title, rather than just the title itself. If it's not so, the except statement will catch the title name by just ripping out the title tag.

`getp` is our go-to variable where we store everything `p` tags. Naturally, this is a list.

The last comment states that we can pick one case to parse everything with. This is due to the fact that nearly every HTML is written differently, so it must be parsed differently; however, there are enough similarities that they generally fall within three cases.

### The Different Styles Produced By The Guys Who Did The HTML Stuff
We'll move away from code and programming to discuss the most common formats of the websites we will scrape. In this tutorial, we'll discuss the two formats that are dealt with in the template.
It's important to know that the template cases are only for works in prose -- that is, things written out in paragraphs with little to no line breaks. Additionally, know that prose is split into sections and subsections. These are generally equivalent to poetry's chapters and verses, respectively. In prose, these are sometimes preceded by bracketed numbers or Roman numerals, but not all the time.
You'll notice that there are actually three cases in the template. Case 3 is more of a variant of Case 2, and are very similar in practice. Once you start coding, you'll realize that you might need to alter one of these cases to properly sort out the information in the database.

#### Case 1
Case 1 deals with sections that have a number or Roman numeral followed by a period or are bracketed, and subsections follow in separate `p` tags. For example, take Cicero's [In Verrem I](http://www.thelatinlibrary.com/cicero/ver1.shtml). Each "chapter" or section begins with a bracketed number. While they are usually broken off into separate `p` tags, there are some paragraphs that are not preceded by a bracketed number. This is because it still belongs to the previous paragraph's section, but is a different subsection. It would be denoted as subsection two.

Often times, something that looks like Case 1 won't have any extra subsections. When this happens, it might be the right decision to declare that each sentence is a subsection (other cases will usually enumerate each sentence as a subsection), but it's probably best left alone.

#### Case 2
Case 2 deals with sections that are split by `p` tags and each subsection is preceded by either a bracketed or unbracketed number or Roman numeral. Take, for example, Cicero's [Pro Caecina](http://www.thelatinlibrary.com/cicero/caecina.shtml), which shows how each sentence starts with a bracketed number. Additionally, if you take a look at the source HTML, you can see that each section is in its own paragraph tags. It's rather simple in practice.

Additionally, there may be times when a section will be preceded by bold text, which is the section name. Certainly, this name should go under chapter, despite not being a number.

### Let's Start Coding Again
Let's discuss the ins and outs of the code in cases 1 and 2.
Each case has the following parameters, which are passed in from main():
```python
def parsecase1(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all p tags. c is the cursor object.
    chapter = '-1'
    verse = 1
```
We also have some default values in case there aren't any technical chapters or verses. While the chapter here is a string of negative one, the data type does not really matter here. Additionally, while the default should be "1", there are times where this makes for a bad default value, so I have stuck with -1 instead. On the other hand, verses will generally always be numbered.

#### Case 1
```python
    for p in ptags:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
```
We then transition into a loop. For this case, the rest of the code will be inside this loop as we will be dealing with paragraph tags one-by-one. This bit of code is an all-purpose try-except block that generally skips irrelevant text that are found in `p` tags but do not go in the database. If it does find an attribute in the list, it will restart the loop at the next `p` tag. If it does not, then it is likely part of the main text, and it continues through the loop.

```python
        passage = ''
        text = p.get_text().strip()
        # Skip empty paragraphs. and skip the last part with the collection link.
        if len(text) `= 0 or text.startswith('Cicero\n'):
            continue
        text = re.split('^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', text)
```
We then create a default empty string for passage inside the loop. This helps up generally find bugs if an empty string ends up in the database. We then use get_text() on our BeautifulSoup object `p` and store it in `text`. get_text() generally just takes all of the text inside the `p` tag (because we are calling it on p) and becomes a string.
The if statement that follows helps us remove unnecessary empty paragraphs, and the second portion of the condition is not always found. However, when it is found, it is completely useless -- it's the text of the hyperlinks at the bottom of the page, usually starting with the collection name, "The Latin Library," etc. As a result, we skip it with a continue statement (and generally end the loop).
This last line is a little trickier. It is a regular expression meant to split apart the text in the paragraph by a variety of things. The short story is that this regular expression splits up the text by a Roman Numeral or number that starts at the beginning, which would generally be the section/chapter value. The variable `text` then becomes a list, as we use parenthesis to keep what we are splitting.

```python
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
```
Continuing on, we have another loop which mainly checks for things that don't belong -- empty strings and whatnot. We remove these. Sometimes, re.split() adds in some unnecessary None values which ruin ... pretty much everything.

```python
        if len(text) > 1:
            i = 0
            while text[i] is None:
                i+=1
            chapter = text[i]
            i+=1
            while text[i] is None:
                i+=1
            passage = text[i].strip()
            verse = 1
        else:
            passage = text[0]
            verse+=1
```
This particular block could probably be written better, but it generally works. What it does is make doubly sure we don't use Nonetypes, while parsing the list. The first item in the list is normally the chapter, and the rest is generally the verse. This may need to be altered if your subsections are enumerated differently. We also set the verse count or add to it depending on where we are in the if-else block.

```python
        if passage.startswith('Florus'):
            continue
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))
```
This is the final stretch. This first conditional is what we've seen before earlier, and is probably unnecessary, but we just want to make extra sure. The problem is that sometimes I'll change only one or the other -- it'll still work, but they generally need to be the same, or it's just a waste of a statement, even though it is not really needed.
Lastly, we have our cursor and our execute statement. This is where we insert everything we found into the table we call "texts". The first value we input None because the table will enumerate the first item, id, automatically. Do not attempt to make it something else, as each id needs to be unique.

And with that, case 1 is done.

#### Other Cases
Case 2's code is generally similar enough to Case 1 that I don't believe an explanation is necessary. Realistically, it is just an alteration of Case 1 to better suit a different HTML organization, just like how Case 3 is just an alteration of Case 2. Changing the code is no doubt necessary for plenty of these collections.
Poetry, on the other hand, is a completely different monster. It generally uses line breaks, and sometimes has line numbers. Using code for prose will generally not function properly when used on poetry.

#### Poetry
Poetry is a lot different than prose since it is composed more of line breaks than anything. Instead of sections (chapters) and subsections (verses), they are simply chapters and verses. Some poems do not even have chapters, and some poems scramble their line numbers. In this topic, we will assume that line numbers are either unlisted or unscrambled.

For the most part, scrapers for poetry are the same as scrapers for prose, except the content of the for loop that iterates over paragraph tags. That is, until the `for p in ptags:` portion.
```python
for p in getp:
    try:
        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
            'internal_navigation']:  # these are not part of the main t
            continue
    except:
        pass
```
Except this part, this part is the same too. However, the rest of the loop is different.

```python
		brtags = p.findAll('br')
                verses = []
                try:
                    try:
                        firstline = brtags[0].previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
                    verses.append(firstline)
                except:
                    pass
```
As you can see, for each paragraph tag, we also need each `br` line break tag since poetry is composed of `br` tags. We also initialize a list to put verses in -- unlike prose, in poetry we accumulate a list of lines instead of executing an INSERT statement for each line.
The nested try-except blocks are a little tricky. Since `br` tags are usually placed after a line, going through the list of `br` tags normally would skip the first line (as it wouldn't be preceded by `br`). Thus, we look for the previous sibling (or the previous sibling of the previous sibling) in hopes of finding the first line, and we append it to the list.

```python
                    ptext = '\n'.join(verses)
                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        verse = 0
                        testchapter = chapter_f.find(text=True)
                        if testchapter.isspace() or testchapter == '':
                            pass
                        else:
                            chapter = testchapter
                        ptext = ptext.replace(chapter,'')
                        if ptext != '' or not ptext.isspace():
                            ptext = re.split('\n', ptext)
                        else:
                            continue
		    else:
			ptext = re.split('\n', ptext)
```
There's actually no real reason to join the list, since we later (seen at the end of the above block) split it anyways for most cases in poetry. Leaving it in instead of removing it reduces the chance of springing up bugs, however.
We also look for the chapter in this instance, if there is one, and we reset the verse counter if we find one. Sometimes, `chapter_f` will do something ridiculous and find an empty string or something, which is why we have `testchapter` in this particular instance instead of directly assigning it to our chapter variable.
The end of the first nested if statement is where we take advantage of the `join()` and remove the chapter from the text. This is only necessary in rare cases when a chapter name ends up in the first line or something. Then, we convert it back into a list with `split()`.

```python
                    for line in ptext:
                        if line == '' or line.isspace() or line is None:
                            continue
                        elif line.startswith("Phaedrus\n"):
                            continue
                        else:
                            verse += 1
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, line, url, 'poetry'))
```
We then go through each line in the list. Of course, empty strings, spaces, and null values are skipped. We also skip the very last line, similarly to prose. We also increment verse number every time we insert a line.

And that's about it.
