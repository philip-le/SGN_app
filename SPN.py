# RSS Feed Filter

import feedparser
import requests
import string
import time
from project_util import translate_html
from news_gui import Popup
import readability
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from joblib import Parallel, delayed

#======================
'''
ToDO:
1. Multi-thread running the code
2. Why we query the page quite slowly?
3. Build an interface
'''
#======================
#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing Google and Yahoo News feeds
#======================
def fprocess(entry):
    guid = entry.guid
    title = entry.title.split(" - ")[0]
    published = entry.published
    source = entry.source.title
    link = entry.link

    web_content = readability.Document(requests.get(link).text)
    summary = translate_html(web_content.summary())

    newsStory = NewsStory(guid, title, summary, published, source, link)
    return newsStory



def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = Parallel(n_jobs=7)(delayed(fprocess)(entry) for entry in entries)
    return ret

#======================
# Part 1
# Data structure design
#======================

# Problem 1

class NewsStory(object):
    def __init__(self, guid, title, summary, published, source, link):
        self.string = [guid, title, summary, published, source, link]
        self.score = {}
    def get_guid(self):
        return self.string[0]
    def get_title(self):
        return  self.string[1]
    def get_summary(self):
        return  self.string[2]
    def get_published(self):
        return self.string[3]
    def get_source(self):
        return self.string[4]
    def get_link(self):
        return self.string[5]
    def set_score(self, news_score):
        self.score = news_score



# Triggers class
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        raise NotImplementedError

# Whole Word Triggers
class WordTrigger(Trigger):
    def __init__(self, word):
        self.word = word.lower()

    def isWordIn(self, text):
        array = "".join((char if char.isalpha() else " ") for char in text).split()
        for i in range(len(array)):
            if self.word == array[i].lower():
                return True
        return False

class TitleTrigger(WordTrigger):
    def evaluate(self, story):        
        return self.isWordIn(story.get_title())

class SubjectTrigger(WordTrigger):
    def evaluate(self, story):        
        return self.isWordIn(story.get_subject())

class SummaryTrigger(WordTrigger):
    def evaluate(self, story):        
        return self.isWordIn(story.get_summary())

class NotTrigger(Trigger):
    def __init__(self, T):
        self.T = T

    def evaluate(self, x):
        return not self.T.evaluate(x)

class AndTrigger(Trigger):
    def __init__(self, T1, T2):
        self.T1 = T1
        self.T2 = T2
    def evaluate(self, x):
        return self.T1.evaluate(x) & self.T2.evaluate(x)

class OrTrigger(Trigger):
    def __init__(self, T1, T2):
        self.T1 = T1
        self.T2 = T2
    def evaluate(self, x):
        return self.T1.evaluate(x) | self.T2.evaluate(x)

class PhraseTrigger(Trigger):
    def __init__(self, astring):
        self.astring = astring
    
    def evaluate(self, story):
        return (self.astring in story.get_title()) | (self.astring in story.get_summary())
    

def filter_stories(stories, triggerlist):
    res_list = []
    for story in stories:
        testval = False
        for trigger in triggerlist:
            if trigger.evaluate(story):
                testval = True
                break
        if testval:
            res_list.append(story)
    return res_list

#======================

def makeTrigger(triggerMap, triggerType, params, name):
    if triggerType=='SUBJECT':
        triggerMap[name]=SubjectTrigger(params[0])
    if triggerType=='TITLE':
        triggerMap[name]=TitleTrigger(params[0])
    if triggerType=='SUMMARY':
        triggerMap[name]=SummaryTrigger(params[0])  
    if triggerType=='PHRASE':
        triggerMap[name]=PhraseTrigger(' '.join(str(param) for param in params))
    if triggerType=='AND':
        triggerMap[name] = AndTrigger(triggerMap[params[0]], triggerMap[params[1]])
    if triggerType=='OR':
        triggerMap[name] = OrTrigger(triggerMap[params[0]], triggerMap[params[1]])
    if triggerType=='NOT':
        triggerMap[name] = NotTrigger(triggerMap[params[0]])
    return triggerMap[name]

def readTriggerConfig(filename):
    """
    Returns a list of trigger objects
    that correspond to the rules set
    in the file filename
    """

    triggerfile = open(filename, "r")
    all = [line.rstrip() for line in triggerfile.readlines()]
    lines = []
    for line in all:
        if len(line) == 0 or line[0] == '#':
            continue
        lines.append(line)

    triggers = []
    triggerMap = {}

    for line in lines:

        linesplit = line.split(" ")

        # Making a new trigger
        if linesplit[0] != "ADD":
            trigger = makeTrigger(triggerMap, linesplit[1],
                                  linesplit[2:], linesplit[0])

        # Add the triggers to the list
        else:
            for name in linesplit[1:]:
                triggers.append(triggerMap[name])

    return triggers

  
import _thread as thread

def main_thread(popup):
    # A sample trigger list - you'll replace
    # t1 = SubjectTrigger("world")
    # t2 = SummaryTrigger("good")
    # t3 = PhraseTrigger("positive")
    # t4 = OrTrigger(t2, t3)
    # triggerlist = [t1, t4]
    
    # # TODO: Problem 11
    # # After implementing readTriggerConfig, uncomment this line 
    triggerlist = readTriggerConfig("triggers.txt")

    guidShown = []
    
    while True:
        print("Polling...")
        start = time.time()

        # Get stories from Google's Top Stories RSS news feed
        stories = process("http://news.google.com/?output=rss")
        # Get stories from Yahoo's Top Stories RSS news feed
        stories.extend(process("http://rss.news.yahoo.com/rss/topstories"))

        print(f'Loading web data took {time.time()-start} seconds')

        # Only select stories we're interested in
        stories = filter_stories(stories, triggerlist)
    
        # Don't print a story if we have already printed it before
        newstories = []

        # Let's do some sentiment analysis
        sia = SIA()

        for story in stories:
            # generate the news_score: 'compound', 'headline', 'neg', 'neu', 'pos'
            pol_score = sia.polarity_scores(story.get_summary())
            pol_score['headline'] = story.get_title()
            story.set_score(pol_score)
            if (story.get_guid() not in guidShown) & (pol_score['compound'] > 0.5)\
                & (pol_score['pos'] > 0.1) & (pol_score['neg'] < 0.07) :
                newstories.append(story)

        
        for story in newstories:
            guidShown.append(story.get_guid())
            print(f'***************{story.get_title()}**{story.score}****************')
            print(story.get_summary())
            popup.newWindow(story)

        print("Sleeping...")
        time.sleep(SLEEPTIME)

SLEEPTIME = 300 #seconds -- how often we poll
if __name__ == '__main__':
    popup = Popup()
    thread.start_new_thread(main_thread, (popup,))
    popup.start()

