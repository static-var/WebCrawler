from bs4 import BeautifulSoup
from urllib import parse
from urllib import robotparser
import requests

from urllib.parse import urlsplit

class Crawl:
    main_URL = ""          # base URL given by the user
    pageList = []          # list which will contain all the links in the end
    toCrawl = []           # list of pages which are to be crawled
    crawled = []           # list of pages which are already crawled
    blackList = 0          # if robots.txt file is there. then 0 else 1
    blackListedLinks = []  # list of all the black listed links
    logs=[]                # keep track of all the fetching activities
    rp = robotparser.RobotFileParser()  #robotParser

    def __init__(self,main_URL):
        self.main_URL = main_URL
        if self.check_Link(self.main_URL):
            self.robotParser(self.main_URL)
            self.toCrawl.append(self.main_URL)
            self.fetch_Links(self.main_URL)

    # returns all the unique values from the list
    def giveSets(self,lists):
        lists = set(lists)
        return list(lists)

    # return the name of the website with domain
    def domainName (self, dName):
        domain = "{0.scheme}://{0.netloc}/".format(urlsplit(dName))

    # function to check if the link exists or not
    def check_Link(self,URL):
        conn = requests.get(URL)
        if conn.status_code == 200 :
            conn.close()
            return True
        else :
            conn.close()
            return False

    # a Function to make a list of all pages which are not allowed to crawl using robots.txt
    def robotParser(self, URL):
        URL = parse.urljoin(URL,"robots.txt")
        conn = requests.get(URL)

        if conn.status_code == 200:
            self.rp.set_url(URL)
            conn.close()
            return True
        else:
            conn.close()
            self.blackList = 1
            return False

    # Function which fetches links from the page and puts those links in dictionary
    def fetch_Links(self,URL):
        ''' Find all the links and pass it to a dictionary with title of page and URL. '''
        # If the link is already fetched then don't repeat this process
        conn = requests.get(URL)
        if URL in self.crawled and conn.status_code != 200:
            conn.close()
            self.toCrawl.remove(URL)
            return
        conn.close()
        # looking out for run time errors due to consistent requests being made
        try:
            sourceCode = requests.get(URL)
        except TimeoutError:
            self.logs.append("Connection Time Out "+URL)
            return
        except requests.exceptions.ConnectionError:
            self.logs.append("Connection Error "+URL)
            return
        except ConnectionResetError:
            self.logs.append("Connection reset")
            return


        pageLinks = []

        packets = sourceCode.text
        soup = BeautifulSoup(packets,"html.parser")
        run = 0

        # find all the links (anchor tag with href attribute) in the page
        for a in soup.find_all('a',href=True):
            links = str(a['href'])
            if run == 0:
                print("Found links on page : "+URL)
            run += 1
            # check if the link belongs to the same domain
            if links.startswith(self.main_URL):
                pageLinks.append(a['href'])
                # Check all the links in the page are already crawled or not
                if a['href'] not in self.toCrawl and a['href'] not in self.crawled:
                    self.toCrawl.append(a['href'])


                print(run)
        # get title of the page
        title = soup.find('title')

        # make a API
        self.make_dictionary(URL,title.string,pageLinks)

        # Put the current link in crawled list as it has been processed.
        self.crawled.append(URL)

        # remove the page URL from toCrawl.
        self.toCrawl.remove(URL)

        # remove redundant entries from toCrawl -- just in case
        self.toCrawl = set(self.toCrawl)
        self.toCrawl = list(self.toCrawl)

        # for getting logs
        print(self.pageList)
        print(self.toCrawl)
        print(len(self.toCrawl))

        # Always close all sorts of connections
        sourceCode.close()

        #TODO : put it in a loop so that the program can become a complete crawler
        exit(0)

    def make_dictionary(self,URL,title,listOfLinks):
        d={
            "URL": URL,
            'Title' : title,
            'Links' : listOfLinks
        }
        self.pageList.append(d)


    #TODO : Convert list of dictionaries into NEO4J nodes and relation format
    #TODO : Look out for more RUNTIME errors - Run on more than one website
    #TODO : Close each and every connection which is opened.
christ = Crawl("https://christuniversity.in/")