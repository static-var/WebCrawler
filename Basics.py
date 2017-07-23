from bs4 import BeautifulSoup
from urllib import parse
from urllib import robotparser
from urllib.parse import urljoin
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
    # A list of common file type which should not be crawled (as per the current needs of this research)
    # also an attempt to avoid any sort of form
    isAFileLink = ['.pdf',      # .pdf files
                   '.doc',      # documents files
                   '.docx',     # modern document files
                   '.jpg',      # image files
                   '.jpge',     # image files
                   '#',         # multiple page like structuring on same page or sometimes for form/javascript purpose
                   '.txt',      # for text files (unusual but still) / robots.txt
                   '.py',       # for any py file connected to form
                   '.c',        # for any .c server side files
                   '.cpp',      # for any .cpp server side files
                   '.zip',      # for any zip (usually a download)
                   '?',         # used in get method of HTML while passing values to another page from a form
                   'js',        # for javascript files
                   'css',       # for style script file
                   'asp',       # for server side asp files
                   'aspx',      # for server side aspx files
                   'javascript:',     # for javascript popups
                   '=',         # for any form values or query passing
                   'mailto'     # for avoiding Mail links
     ]

    def __init__(self,main_URL):
        self.main_URL = main_URL
        if self.check_Link(self.main_URL):
            self.robotParser(self.main_URL)
            self.toCrawl.append(self.main_URL)
            self.looper_Function()
            print(" All links fetched ")
            exit(0)

    # returns all the unique values from the list
    def giveSets(self,lists):
        lists = set(lists)
        return list(lists)

    # Check if a link is actully a file or a web page.
    def fileLinksCheck(self,URL):
        if any(x in URL for x in self.isAFileLink):
            return True
        else:
            return False

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

    # This function finds all the links and passes it to a dictionary with title of page and URL.
    def fetch_Links(self,URL):
        # If the link is already fetched then don't repeat this process
        try:
            conn = requests.get(URL)
            if URL in self.crawled and conn.status_code != 200 :
                conn.close()
                self.toCrawl.remove(URL)
                self.logs.append(URL+"Not a URL")
                return
            conn.close()
        except requests.exceptions.MissingSchema:
            self.toCrawl.remove(URL)
            self.logs.append(URL + "Not a URL")
            return

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

        # A check to see the number of links in page are not zero.
        # If they are 0 then remove link from the toCrawl list and exit
        if len(soup.find_all('a',href=True)) == 0:
            if URL in self.toCrawl:
                self.toCrawl.remove(URL)
            if URL not in self.crawled:
                self.crawled.append(URL)
            self.logs.append(URL + " Crawled, Single Link Page")
            return

        # find all the links (anchor tag with href attribute) in the page
        for a in soup.find_all('a',href=True):
            links = str(a['href'])
            if run == 0:
                print("Found links on page : "+URL)
            run += 1

            # checking every link with the file list we have
            if self.fileLinksCheck(links):
                continue

            # check for relative URL and convert them to Absolute URL
            if not links.startswith('http'):
                links = urljoin(URL,links)
                print(links)

            # check if the link belongs to the same domain
            if links.startswith(self.main_URL):

                # Check all the links in the page are already crawled or not
                if links in self.crawled:
                    continue
                else:
                    if not links in self.toCrawl:
                        self.toCrawl.append(links)


        # get title of the page &
        # if title is not there then use URL as page title to avoid empty values from getting passed
        title = soup.find('title')
        try:
            if title.string and not title.string.isspace():
                title = title.string
        except:
            title = str(URL)

        # convert to JSON
        self.make_dictionary(URL,title,pageLinks)

        # Put the current link in crawled list as it has been processed.
        if URL not in self.crawled:
            self.crawled.append(URL)

        # remove the page URL from toCrawl.
        if URL in self.toCrawl:
            self.toCrawl.remove(URL)

        # for getting logs in terminal
        print("Total links found",len(self.pageList))
        print("Links are",self.toCrawl)
        print("Total number of links to be fetched ",len(self.toCrawl))

        # Always close all sorts of connections
        sourceCode.close()

        # write all the information in the file
        fileWriting = open('linkstocrawl.txt', 'w')
        for items in self.toCrawl:
            fileWriting.write("%s\n" % items)
        fileWriting.close()

        fileWriting = open('crawled.txt', 'w')
        for items in self.crawled:
            fileWriting.write("%s\n" % items)
        fileWriting.close()

        fileWriting = open('logs.txt', 'w')
        for items in self.logs:
            fileWriting.write("%s\n" % items)
        fileWriting.close()

    def make_dictionary(self,URL,title,listOfLinks):
        d = {
            "URL": URL,
            'Title' : title,
            'Links' : listOfLinks
        }
        self.pageList.append(d.copy())


    def looper_Function(self):
        for links in self.toCrawl:
            self.fetch_Links(links)

        if len(self.toCrawl) != 0:
            self.looper_Function()

    #TODO : Convert list of dictionaries into NEO4J nodes and relation format
    #TODO : Look out for more RUNTIME errors - Run on more than one website

OBJ = Crawl("Some website URL")
