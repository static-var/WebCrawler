'''
August 2017

Author : Shreyansh Lodha <slodha96@gmail.com>

The aim of this script is to convert the API like structure to a Neo4j Graph data.
'''

from Basics import Crawl
from neo4j.v1 import GraphDatabase
import authDetails
import progressbar
import time

# List of variables required
_property_URL = []
_property_title = []
all_links = []
# neo4j connection string
driver = GraphDatabase.driver(authDetails.uri, auth=(authDetails.user, authDetails.password))
# Create nodes and insert data with property
def insertNodes(website):
    # Crawl the website
    obj = Crawl(website)
    # Empty the database before inserting new data
    emptyDB()
    bar = progressbar.ProgressBar(max_value=len(obj.pageList))
    counter = 0
    # Start session
    session = driver.session()

    for all_items in obj.pageList:
        counter += 1
        # Fetch the details of the current page we are working with
        tempTitle = all_items['Title']
        tempURL = all_items['URL']

        # Create a node or Match it on basis of URL,
        # if it exists and append the Title Property
        session.run("MERGE (n:Link {URL : {url}})"
                    "ON MATCH SET n.Title = {title}"
                    "ON CREATE SET n.Title = {title}",
                    {"url":tempURL, "title":tempTitle, "title":tempTitle})

        # print("Creating Graph for Page: ",tempTitle,"URL:",tempURL)
        for individual_links in all_items['Links']:
            session.run("MERGE (n:Link {URL : {url}})",
                        {"url":individual_links})

            # Create a relation between between the parent link and child link
            session.run("MATCH (a:Link), (b:Link)"
                        "WHERE a.URL = {parent} AND b.URL = {child}"
                        "CREATE (a)-[r:LINKS_TO]->(b)",
                        {"parent":tempURL, "child":individual_links})
        time.sleep(0.1)
        bar.update(counter)

    session.close()

# Clean existing content in DB
def emptyDB():
    session = driver.session()
    delete = session.run("MATCH (n) DETACH DELETE n")
    session.close()

# Call the Program
name = "http://www.vidhyashram.edu.in/"
insertNodes(name)