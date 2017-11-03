import cookielib 
import urllib2 
import mechanize 
import re
import datetime
import logging
import time
import sys
import traceback

        
class RegistrationException(Exception):
    def __init__(self,output):
        self.output = str(output)
        self.datetime = str(datetime.datetime.today())
        
class AutoRegisterClasses:
    def __init__(self):

        self.baseLink = "https://banweb.cnu.edu:9997"

        self.readFile()

    def readFile(self):
    
        try:
            data = [line.rstrip('\n') for line in open("config.txt")]
        except:
            print 'Error opening file'
            sys.exit(0)

        self.userID = data[0]
        self.Passwd = data[1]
        
        self.altPin = data[2]
        self.semTrm = data[3]
        
        self.crns = []
        
        for x in range(4,len(data)):
            self.crns.append(data[x])

    def setup(self):        
        # Browser 
        self.br = mechanize.Browser() 

        # Enable cookie support for urllib2 
        cookiejar = cookielib.LWPCookieJar() 
        self.br.set_cookiejar( cookiejar )
        self.br.addheaders = [ ( 'User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' ) ]
        self.br.addheaders.append(('Connection', 'keep-alive'))

    def startTime(self):
        self.start = time.time()
        
    def checkForRegistrationException(self):
        #print br.response().geturl()
        output = self.br.response().read()
        if("/wtlgifs/web_stop_cascade.png" in output or "Invalid" in output):
            print "Registration Exception:"
            raise RegistrationException(output)

    def begin(self):
        br = self.br
        
        # authenticate
        br.open(self.baseLink + "/bpdbdad/twbkwbis.P_ValLogin") 
        br.select_form( name="loginform" )

        br[ "sid" ] = self.userID
        br[ "PIN" ] = self.Passwd
        res = br.submit()

        self.checkForRegistrationException()

        # Navigate down chain some
        for link in br.links(url_regex="Stu"):
            br.follow_link(link)
        for link in br.links(url_regex="Reg"):
            br.follow_link(link)
        for link in br.links(url_regex="P_Alt"):
            br.follow_link(link)

        # fill out form for CheckAltPin
        br.select_form( nr=1 )
        br[ "term_in" ] = [self.semTrm]
        res = br.submit()
        
        print "\tSUBMITTED term:",br.geturl()
        
        br.select_form( nr=1 )
        br[ "pin" ] = self.altPin
        res = br.submit()
        
        print "\tSUBMITTED alt-pin:",br.geturl()
        
        self.checkForRegistrationException()

    def reloadPg(self):
        
        br = self.br
        res = br.reload()
        #logging.error(res.read())
        print br.geturl()
        
    def register(self):
        br = self.br

        # select crn form
        br.select_form( nr=1 )

        # fill in crns
        for i in range(0,len(self.crns)):
            field = br.find_control(id="crn_id" + str(i+1))
            field.value = self.crns[i]
        # submit crns
        br.submit(nr=0)

        self.checkForRegistrationException()
        
        self.endTime()

    def endTime(self):
        self.end = time.time()
        return (self.end-self.start)
        
import inspect
def printMsg(e):
##        print "!!!!!!!!!"
        print "\tDate/Time of exception:",e.datetime
##        print "\tA REGISTRATION ERROR WAS THROWN!!!"
##        print "while registering, CNU Live displayed its generic error png"
##            
##        print "--"
##        print "please check AutoReg-Error.html for the html source code that contained the error message"
##        print "try opening in a browser to easily determine error"
##        
        logging.basicConfig(filename='AutoReg-Errors.html', level=logging.ERROR)
        logging.error(e.datetime)
        logging.error(e.output)
        
if __name__ == "__main__":
    
    a = AutoRegisterClasses()
    a.setup()
    a.begin()
    attempts = 2
    times = []
    
    for x in range(attempts):
        print "--", x+1, "--------------------------------------------------------------------------------"
        try:
            a.startTime()
            if x > 0:
                a.reloadPg()
                
            a.register()
            print "--"
            print "Done!"
        except RegistrationException as e:
            printMsg(e)
            
        except Exception as e:
            print "An error was thrown..."
            print e
            traceback.print_exc()

        dt = a.endTime()
        print "Time (seconds):", dt
        times.append(dt)
        print ""
    
    print "\tAverage run time:", sum(times)/len(times)
    
    attempts = 2
    times = []

    print "\n"
    
    a = AutoRegisterClasses()
    a.setup()
    for x in range(attempts):
        print "--", x+1, "--------------------------------------------------------------------------------"
        try:
            a.startTime()
            a.begin()
            a.register()
            print "--"
            print "Done!"
        except RegistrationException as e:
            printMsg(e)
            
        except Exception as e:
            print "An error was thrown..."
            print e
            traceback.print_exc()

        dt = a.endTime()
        print "Time (seconds):", dt
        times.append(dt)
        print ""
    
    print "\tAverage run time:", sum(times)/len(times)
