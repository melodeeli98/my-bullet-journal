####################################
# My Bullet Journal
# Created by Melodee S. Li (melodeeli98@gmail.com)
# Carnegie Mellon University
# Video demonstration: https://www.youtube.com/watch?v=wIegmgyDaIM
####################################

from tkinter import *
import datetime,time,copy,string,math

####################################
# OOP classes
####################################

class Item(object):

    def __init__(self,name,assignedTime=None,group=None,marking="incomplete"):
        self.name=name
        self.group=group
        self.selected=False
        self.row=0
        self.duration=datetime.timedelta(hours=int(self.durationHour),minutes=int(self.durationMinute))
        self.selectedHour=1
        self.selectedMinute=0
        self.selectedAMPM="AM"
        self.assignedTime=assignedTime
        self.shifted=False
        self.timeCreated=datetime.datetime.today()
        self.marking=marking
        self.isEditing=True

    def __hash__(self):
        return hash((self.timeCreated,self.name))

    def __eq__(self,other):
        if not isinstance(other,Item): return False
        return self.name==other.name and self.duration==other.duration

    def getColor(self,data):
        groupDict=DayLog.groupDict
        return groupDict[self.group] if self.group!=None else data.backgroundColor

    def makeShifted(self):
        if not self.shifted:
            self.shifted=True
            self.row+=1

    def getHourMinute(self):
        if self.assignedTime==None: return ":"
        hour=self.assignedTime.hour
        if hour<12:
            hourStr=str(hour) if hour!=0 else "12"
            ampmStr="AM"
        else:
            hourStr=str(int(hour)-12) if hour!=12 else str(int(hour))
            ampmStr="PM"
        minute=self.assignedTime.minute
        minuteStr=str(minute)
        if len(minuteStr)==1: minuteStr="0"+minuteStr
        return hourStr+":"+minuteStr,ampmStr

    def getDurationString(self):
        duration=str(self.duration)
        colonIndex1=duration.find(":")
        hours=duration[:colonIndex1]
        duration=duration[colonIndex1+1:]
        colonIndex2=duration.find(":")
        minutes=duration[:colonIndex2]
        if minutes.startswith("0"): minutes=minutes[1:]
        return (hours+" hours and "+minutes+" minutes")

    def toggleGroup(self):
        groupList=sorted(list(DayLog.groupDict))+[None]
        nextIndex=groupList.index(self.group)+1
        if nextIndex==len(groupList): nextIndex=0
        self.group=groupList[nextIndex]

    def togglePriority(self):
        self.priority=not self.priority

class Task(Item):
    def __init__(self,name,durationHour="0",durationMinute="0",assignedTime=None,group=None,marking="incomplete",priority=False):
        self.durationHour=durationHour
        self.durationMinute=durationMinute
        super().__init__(name,assignedTime,group,marking)
        self.priority=priority

    def __repr__(self):
        return "Task %s" % (self.name)

class DayLog(object):
    groupDict={"school":"khaki","extracurricular":"mediumpurple","health":"lightcyan","personal":"palegreen"}
    invertedMarkingDict={0:"incomplete",1:"started",2:"migrated",3:"completed",4:"cancelled"}

    def __init__(self,date,data):
        self.date=date
        self.itemSet=set()

    def __repr__(self):
        return "DayLog %s" % self.date

    def addItem(self,*args):
        for item in args:
            if isinstance(item,Item):
                self.itemSet.add(item)

    def deleteItem(self,item):
        if item in self.itemSet:
            self.itemSet.remove(item)

    def unshiftAll(self):
        for item in self.itemSet:
            if item.shifted:
                item.shifted=False
                item.row-=1

    def getSortedList(self,sortMode):
        if sortMode=="group" or sortMode=="priority" or sortMode=="marking":
            #sort by grouping all of the items with the same attribute together
            if sortMode=="group": itemList=self.sortByGroup(list(self.itemSet))
            elif sortMode=="priority": itemList=self.sortByPriority(list(self.itemSet))
            elif sortMode=="marking": itemList=self.sortByMarking(list(self.itemSet))
        else:
            #sort by binary search
            itemList=[]
            for item in self.itemSet:
                if len(itemList)==0: itemList.append(item)
                else:
                    if sortMode=="name": index=self.findIndexByName(item,itemList)
                    elif sortMode=="assignedTime": index=self.findIndexByAssignedTime(item,itemList)
                    elif sortMode=="timeCreated": index=self.findIndexByTimeCreated(item,itemList)
                    itemList=itemList[:index]+[item]+itemList[index:]
        #adjust the "row" attribute for each item
        i=0
        while i<len(itemList):
            itemList[i].row=i
            i+=1
            if self.getSelectedTask()!=None and self.getSelectedTask()==itemList[i-1]: break #to handle row shifting
        for j in range(i+1,len(itemList)):
            itemList[i].row=i+1
        return itemList

    @staticmethod
    def findIndexByName(item,itemList): #recursive
        def findNearItem(item,itemList,index=0):
            if len(itemList)==1: return itemList[0]
            else:
                mid=len(itemList)//2
                if item.name>itemList[mid].name:
                    newIndex=index+mid
                    return findNearItem(item,itemList[mid:],newIndex)
                elif item.name==itemList[mid].name: return itemList[mid]
                else:
                    newIndex=index+mid if index==0 else index-mid
                    return findNearItem(item,itemList[:mid],newIndex)
        nearIndex=itemList.index(findNearItem(item,itemList))
        if item.name<itemList[nearIndex].name: return nearIndex
        else: return nearIndex+1

    @staticmethod
    def findIndexByTimeCreated(item,itemList): #recursive
        def findNearItem(item,itemList,index=0):
            if len(itemList)==1: return itemList[0]
            else:
                mid=len(itemList)//2
                if item.timeCreated>itemList[mid].timeCreated:
                    newIndex=index+mid
                    return findNearItem(item,itemList[mid:],newIndex)
                elif item.timeCreated==itemList[mid].timeCreated: return itemList[mid]
                else:
                    newIndex=index+mid if index==0 else index-mid
                    return findNearItem(item,itemList[:mid],newIndex)
        nearIndex=itemList.index(findNearItem(item,itemList))
        if item.timeCreated<itemList[nearIndex].timeCreated: return nearIndex
        else: return nearIndex+1

    @staticmethod
    def findIndexByAssignedTime(item,itemList): #recursive
        def findNearItem(item,itemList,index=0):
            if len(itemList)==1: return itemList[0]
            else:
                mid=len(itemList)//2
                if (itemList[mid].assignedTime==None or item.assignedTime>itemList[mid].assignedTime):
                    newIndex=index+mid
                    return findNearItem(item,itemList[mid:],newIndex)
                elif item.assignedTime==itemList[mid].assignedTime: return itemList[mid]
                else:
                    newIndex=index+mid if index==0 else index-mid
                    return findNearItem(item,itemList[:mid],newIndex)
        if item.assignedTime==None: return len(itemList)
        else:
            nearIndex=itemList.index(findNearItem(item,itemList))
            if (itemList[nearIndex].assignedTime!=None
                and item.assignedTime<itemList[nearIndex].assignedTime):
                return nearIndex
            else: return nearIndex+1

    @staticmethod
    def sortByGroup(itemList):
        result=[]
        groupList=sorted(list(DayLog.groupDict))+[None]
        for group in groupList:
            for item in itemList:
                if item.group==group:
                    result.append(item)
        return result

    @staticmethod
    def sortByPriority(itemList):
        result=[]
        for item in itemList:
            if item.priority: result.insert(0,item)
            else: result.append(item)
        return result

    @staticmethod
    def sortByMarking(itemList):
        result=[]
        markingList=[]
        for index in range(len(DayLog.invertedMarkingDict)):
            markingList.append(DayLog.invertedMarkingDict[index])
        for marking in markingList:
            for item in itemList:
                if item.marking==marking:
                    result.append(item)
        return result

    def getSelectedTask(self):
        for item in self.itemSet:
            if item.selected:
                return item

    def deselectAll(self):
        for item in self.itemSet: #if another item is already selected, deselect it
            if item.selected:
                item.selected=False
                self.unshiftAll()

    def getEditingTask(self):
        for item in self.itemSet:
            if item.isEditing: return item
        else: return None

    def stopEditingTask(self):
        for item in self.itemSet:
            if item.isEditing:
                item.isEditing=False
                continue

    def replaceTask(self,data,currTask,previousTaskState):
        itemList=self.getSortedList(data.sortMode)
        for index in range(len(itemList)):
            if itemList[index] is currTask:
                data.previousTaskState.selected=False
                data.previousTaskState.isEditing=False
                self.itemSet.remove(itemList[index])
                self.itemSet.add(previousTaskState)

class DaySchedule(object):
    def __init__(self):
        self.startTime=datetime.time(hour=0,minute=0)
        self.endTime=datetime.time(hour=23,minute=59)
        self.dayLength=datetime.timedelta(hours=24)
        self.date=datetime.datetime.today()
        self.questions=[]
        self.schedule=[]
        self.sleepTime=None

    def addQuestion(self,*questions):
        for question in questions:
            self.questions.append(question)

    def addPeriod(self,task):
        self.schedule.append(task)

    def isEmpty(self):
        if self.schedule==None or len(self.schedule)==0: return True
        else: return False

class Question(object):
    def __init__(self,question=""):
        self.question=question
        self.possibleAnswers=[] #answer choices for the user
        self.answer=None #actual answer the user gave

    def __repr__(self):
        return self.question

    def addAnswer(self,answer):
        self.answer=answer

    def addPossibleAnswer(self,*possibleAnswers):
        for possibleAnswer in possibleAnswers:
            self.possibleAnswers.append(possibleAnswer)

class StudyQuestion(Question):
    def __init__(self,question,item):
        super().__init__(question)
        self.test=item

####################################
# Model/Controller Functions
####################################

#init functions:

def init(data):
    data.x,data.y=0,0
    data.timesFired=0
    data.minPerHour=60
    data.day=datetime.datetime.today().day
    data.month=datetime.datetime.today().month
    data.year=datetime.datetime.today().year

    colors(data)
    openingScreenValues(data)
    windowValues(data)
    loadImages(data)
    dailyLogValues(data)
    editTaskScreenValues(data)
    planMyDayValues(data)
    helpScreens(data)

def loadImages(data):
    data.dailyLogImage=PhotoImage(file="images\dailylogbutton.gif")
    data.planMyDayImage=PhotoImage(file="images\planmydaybutton.gif")
    data.enterUsernameImage=PhotoImage(file="images\enterUsernameText.gif")
    data.submitButtonImage=PhotoImage(file="images\submitbutton.gif")
    data.helpButtonImage=PhotoImage(file="images\helpbutton.gif")
    data.menuButtonImage=PhotoImage(file="images\menubutton.gif")
    data.smallSubmitButtonImage=PhotoImage(file="images\smallsubmitbutton.gif")
    data.smallPlanMyDayImage=PhotoImage(file="images\smallplanmydaybutton.gif")
    data.smallDailyLogImage=PhotoImage(file="images\smalldailylogbutton.gif")
    data.smallBlankButton=PhotoImage(file="images\smallblankbutton.gif")
    data.helpScreen1=PhotoImage(file="images\help1.gif")
    data.helpScreen2=PhotoImage(file="images\help2.gif")
    data.helpScreen3=PhotoImage(file="images\help3.gif")
    data.helpScreen4=PhotoImage(file="images\help4.gif")
    data.helpScreen5=PhotoImage(file="images\help5.gif")
    data.helpScreen6=PhotoImage(file="images\help6.gif")
    data.scheduleErrorScreen=PhotoImage(file="images\scheduleError.gif")

def colors(data):
    data.backgroundColor="Lavender"
    data.color1="lightBlue"
    data.color2="salmon"
    data.exitButtonColor="lightCoral"

def openingScreenValues(data):
    data.isOpeningScreen=True
    data.isEditingUsername=False
    data.isErrorScreen=False
    data.errorMarginX=70
    data.errorMarginY=250
    data.username=""
    data.isMenu=False

def windowValues(data):
    data.outerMarginX=90
    data.outerMarginY=190
    data.shadowMargin=3
    data.blinkingCursor=" "
    data.exitButtonDim=data.outerMarginY/9
    data.exitButtonMargin=2

    data.errorexitx0=data.width-data.errorMarginX-data.exitButtonDim-data.exitButtonMargin
    data.errorexitx1=data.errorexitx0+data.exitButtonDim
    data.errorexity0=data.errorMarginY+data.exitButtonMargin
    data.errorexity1=data.errorexity0+data.exitButtonDim

    data.taskexitx0=data.width-data.outerMarginX-data.exitButtonDim-data.exitButtonMargin
    data.taskexitx1=data.taskexitx0+data.exitButtonDim
    data.taskexity0=data.outerMarginY+data.exitButtonMargin
    data.taskexity1=data.taskexity0+data.exitButtonDim

    data.menux0=data.width*1/32
    data.menux1=data.width*7/32
    data.menuy0=data.height*115/128
    data.menuy1=data.height*31/32

    data.continuex0,data.continuey0=data.width*11/32,data.height*59/64
    data.continuex1,data.continuey1=data.width*23/32,data.height*126/128

def dailyLogValues(data):
    data.isDailyLog=False
    data.taskMargin=50
    data.bulletDim=20
    data.arrowSize=15
    data.sortDropDownM=data.width/10
    data.sortDropDownHeight=25
    data.showSortByDropdown=False
    data.taskDropDownM=3
    data.plusButtonDiameter=40
    data.sortbyx0,data.sortbyy0=data.width/3+data.sortDropDownM,data.height/5
    data.sortbyx1,data.sortbyy1=data.width*2/3,data.sortbyy0+data.sortDropDownHeight

    data.editx0,data.editx1=data.width*3/8,data.width*15/32
    data.deletex0,data.deletex1=data.width*15/32,data.width*9/16

    data.currTask=None
    data.anyTaskSelected=False
    data.todayLog=DayLog(datetime.date.today(),data)
    data.currLog=data.todayLog
    data.logList=[data.todayLog]
    data.sortMode="timeCreated"
    data.markingDict={"incomplete":1,"started":2,"migrated":3,"completed":4,"cancelled":5}
    data.invertedMarkingDict={0:"incomplete",1:"started",2:"migrated",3:"completed",4:"cancelled"}
    data.sortModeDict={"name":1,"assignedTime":2,"timeCreated":3,"group":4,"priority":5,"marking":6}

def editTaskScreenValues(data):
    data.nameFieldx0,data.nameFieldy0=data.outerMarginX*10/8,data.outerMarginY*22/16
    data.nameFieldx1,data.nameFieldy1=data.width-data.nameFieldx0,data.nameFieldy0*9/8
    data.priorityX,data.priorityY=data.nameFieldx0*9/8,data.nameFieldy1*21/16
    data.checkmarkDim=data.outerMarginY/15
    data.checkOffset=data.bulletDim/2-data.checkmarkDim/2
    data.checkx0,data.checky0=data.priorityX+data.outerMarginX+data.checkOffset,data.priorityY+data.checkOffset
    data.checkx1,data.checky1=data.checkx0+data.checkmarkDim,data.checky0+data.checkmarkDim
    data.timeFieldx0,data.timeFieldy0=data.nameFieldx0*9/8+data.outerMarginX,data.nameFieldy1*3/2
    data.timeFieldx1,data.timeFieldy1=data.timeFieldx0+data.bulletDim*4,data.timeFieldy0+data.bulletDim
    data.durationX,data.durationY=data.nameFieldx0*9/8,data.nameFieldy1*27/16
    data.durationHourx0,data.durationHoury0=data.nameFieldx0*9/8+data.outerMarginX*23/16,data.durationY
    data.durationHourx1,data.durationHoury1=data.durationHourx0+data.bulletDim*3/2,data.durationHoury0+data.bulletDim
    data.durationMinutex0,data.durationMinutey0=data.durationHourx0+data.bulletDim+data.outerMarginX*7/8,data.durationY
    data.durationMinutex1,data.durationMinutey1=data.durationMinutex0+data.bulletDim*3/2,data.durationMinutey0+data.bulletDim

    data.tasksubmitx0,data.tasksubmity0=data.outerMarginX*9/4,data.nameFieldy1*30/16
    data.tasksubmitx1,data.tasksubmity1=data.width-data.tasksubmitx0,data.tasksubmity0*17/16
    data.timeMarginX=50
    data.timeMarginY=210
    data.timesubmitx0,data.timesubmity0=data.tasksubmitx0,data.timeMarginY*32/16
    data.timesubmitx1,data.timesubmity1=data.tasksubmitx1,data.timesubmity0*17/16

    data.isEditScreen=False
    data.previousTaskState=None
    data.createNameErrorMessage=False
    data.selectTimeScreen=False
    data.inHourField=False
    data.inMinuteField=False
    data.createDurationErrorMessage=False
    data.isUpdatingName=False

def planMyDayValues(data):
    data.isPlanMyDay=False
    data.isQuestionScreen=False
    data.isScheduleScreen=False
    data.currDaySched=DaySchedule()
    data.currQuestionIndex=0
    data.previousDaySched=None
    data.testKeyWords=["exam","Exam","test","Test","quiz","Quiz","assessment","Assessment"]
    data.numHoursDaily=data.currDaySched.endTime.hour-data.currDaySched.startTime.hour+1
    data.maxAnswersPerLine=4
    data.scheduleError=False

def helpScreens(data):
    data.isHelp=False
    data.isHelpScreen1=False
    data.isHelpScreen2=False
    data.isHelpScreen3=False
    data.isHelpScreen4=False
    data.isHelpScreen5=False
    data.isHelpScreen6=False

#mousePressed functions:

def mousePressed(event, data):
    data.x,data.y=event.x,event.y
    if data.isHelp: checkHelpScreenButtons(data)
    elif data.isOpeningScreen: checkOpeningScreenSelections(data)
    elif data.isMenu: checkMenuSelections(data)
    elif data.isDailyLog: checkDailyLogSelections(data)
    elif data.isQuestionScreen: checkQuestionScreenSelections(data)
    elif data.isScheduleScreen: checkScheduleScreenSelections(data)
    elif data.scheduleError: checkScheduleErrorScreenSelections(data)

def checkHelpScreenButtons(data):
    if data.continuex0<data.x<data.continuex1 and data.continuey0<data.y<data.continuey1:
        if data.isHelpScreen1:
            data.isHelpScreen1=False
            data.isHelpScreen2=True
        elif data.isHelpScreen2:
            data.isHelpScreen2=False
            data.isHelpScreen3=True
        elif data.isHelpScreen3:
            data.isHelpScreen3=False
            data.isHelpScreen4=True
        elif data.isHelpScreen4:
            data.isHelpScreen4=False
            data.isHelpScreen5=True
        elif data.isHelpScreen5:
            data.isHelpScreen5=False
            data.isHelpScreen6=True
        elif data.isHelpScreen6:
            data.isHelpScreen6=False
            data.isHelp=False
            data.isMenu=True

def checkOpeningScreenSelections(data):
    if data.isErrorScreen:
        #exit button
        if data.errorexitx0<data.x<data.errorexitx1 and data.errorexity0<data.y<data.errorexity1:
          data.isErrorScreen=False
    else:
        #submit button
        if data.width/3<data.x<data.width*2/3 and data.height*23/32<data.y<data.height*27/32:
            #user did not enter anything:
            if data.username=="": data.isErrorScreen=True
            else:
                data.isOpeningScreen=False
                data.isEditingUsername=False
                data.isMenu=True
        #username text field
        elif data.width/8<data.x<data.width*7/8 and data.height*35/64<data.y<data.height*5/8:
            data.isEditingUsername=True
        else: data.isEditingUsername=False

def checkMenuSelections(data):
    #daily log button
    if (data.width*5/32<data.x<data.width*27/32 and data.height*7/32<data.y<data.height*15/32):
        data.isDailyLog=True
        data.isMenu=False
    #plan my day button
    elif (data.width*5/32<data.x<data.width*27/32 and data.height*16/32<data.y<data.height*24/32):
        data.isMenu=False
        #a schedule hasn't been made yet
        if data.currDaySched.isEmpty():
            data.previousDaySched=copy.deepcopy(data.currDaySched)
            createQuestions(data)
            data.isQuestionScreen=True
        else: data.isScheduleScreen=True
    #help button
    elif (data.width*19/64<data.x<data.width*43/64 and data.height*26/32<data.y<data.height*30/32):
        data.isHelp=True
        data.isHelpScreen1=True
        data.isMenu=False

def checkDailyLogSelections(data):
    if data.isEditScreen:
        data.showSortByDropdown=False
        if data.isEditScreen: checkEditScreenSelections(data)
    else:
        #menu button
        if (data.menux0<data.x<data.menux1 and data.menuy0<data.y<data.menuy1):
            data.anyTaskSelected=False
            data.currLog.deselectAll()
            data.showSortByDropdown=False
            data.isDailyLog=False
            data.isMenu=True
        #today button
        elif (data.width*9/16<data.x<data.width*3/4 and data.height*7/56<data.y<data.height*9/56):
            deltaDays=datetime.datetime.today().day-data.currLog.date.day
            changeDate(data,deltaDays)
        #plus button- use distance function because the button is a circle
        elif distance(data.x,data.y,data.width*27/32+data.plusButtonDiameter/2,
            data.height*29/32+data.plusButtonDiameter/2)<=data.plusButtonDiameter/2:
            data.isEditScreen=True
            data.anyTaskSelected=False
        #sort by menu
        if data.sortbyx0<data.x<data.sortbyx1 and data.sortbyy0<data.y<data.sortbyy1:
            data.showSortByDropdown=not data.showSortByDropdown
        if data.showSortByDropdown:
            data.anyTaskSelected=False
            if not (data.sortbyx0<data.x<data.sortbyx1 and data.sortbyy0<data.y<data.sortbyy1):
                data.showSortByDropdown=False
            checkSortByMenuSelections(data)
        checkIfTaskSelected(data)
        if data.anyTaskSelected:
            data.currTask=data.currLog.getSelectedTask()
            if data.currTask!=None:
                data.showSortByDropdown=False
                checkTaskMenuSelections(data,data.currTask)
        checkIfTriangleSelected(data)

def checkIfTriangleSelected(data):
    leftx0,lefty0=data.width/8,data.height/7
    leftx1,lefty1=leftx0+data.arrowSize,lefty0-data.arrowSize
    leftx2,lefty2=leftx0+data.arrowSize,lefty0+data.arrowSize
    left1M=(lefty1-lefty0)/(leftx1-leftx0)#left triangle, line 1 slope
    left1B=lefty0-left1M*leftx0 #left triangle, line 1 y-intercept
    left2M=(lefty2-lefty0)/(leftx2-leftx0)#left triangle, line 2 slope
    left2B=lefty0-left2M*leftx0 #left triangle, line 2 y-intercept
    if ((leftx0<=data.x<=leftx1 and data.x*left1M+left1B<=data.y<=lefty0)
        or (leftx0<=data.x<=leftx2 and lefty0<=data.y<=data.x*left2M+left2B)):
        changeDate(data,-1)
    rightx0,righty0=data.width*7/8,data.height/7
    rightx1,righty1=rightx0-data.arrowSize,righty0-data.arrowSize
    rightx2,righty2=rightx0-data.arrowSize,righty0+data.arrowSize
    right1M=(righty1-righty0)/(rightx1-rightx0)#right triangle, line 1 slope
    right1B=righty0-right1M*rightx0 #right triangle, line 1 y-intercept
    right2M=(righty2-righty0)/(rightx2-rightx0)#right triangle, line 2 slope
    right2B=righty0-right2M*rightx0 #right triangle, line 2 y-intercept
    if ((rightx1<=data.x<=rightx0 and data.x*right1M+right1B<=data.y<=righty0)
        or (rightx2<=data.x<=rightx0 and righty0<=data.y<=data.x*right2M+right2B)):
        changeDate(data,1)

def checkIfTaskSelected(data):
    if data.anyTaskSelected==False: data.currLog.deselectAll()
    for i in range(len(data.itemList)):
        currItem=data.itemList[i]
        if not isinstance(currItem,Task): continue
        bulletx0,bullety0=data.width/4-data.bulletDim/2,data.height/4+(currItem.row+1)*data.taskMargin-data.bulletDim/2
        bulletx1,bullety1=bulletx0+data.bulletDim,bullety0+data.bulletDim
        taskx0,tasky0=data.width*3/8,bullety0
        taskx1,tasky1=taskx0+len(currItem.name)*8,bullety1
        if ((bulletx0<data.x<bulletx1 and bullety0<data.y<bullety1) or
            (taskx0<data.x<taskx1 and tasky0<data.y<tasky1)): #currItem was clicked on
            if currItem.selected: #if currItem has already been selected, deselect it
                data.anyTaskSelected=False
                currItem.selected=False
                data.currLog.unshiftAll()
            else:
                data.anyTaskSelected=True
                data.currLog.deselectAll() #if another item is already selected, deselect it
                currItem.selected=True
                for index in range(i+1,len(data.itemList)): #shift all of the items below currTask down
                    data.itemList[index].makeShifted()

def checkTaskMenuSelections(data,task):
    x,y=data.width/4-data.bulletDim/2,data.height/4+(task.row+1)*data.taskMargin+data.bulletDim/2+data.taskDropDownM
    edity0,edity1=y,y+data.bulletDim
    deletey0,deletey1=y,y+data.bulletDim
    if data.editx0<data.x<data.editx1 and edity0<data.y<edity1:
        data.isEditScreen=True
        task.isEditing=True
    elif data.deletex0<data.x<data.deletex1 and deletey0<data.y<deletey1:
        data.currLog.deleteItem(task)
    #check bullet options
    bulletx0=x+data.taskDropDownM
    bulletx1=bulletx0+data.bulletDim-data.taskDropDownM*2
    i=0
    for index in range(len(data.invertedMarkingDict)):
        marking=data.invertedMarkingDict[index]
        if marking!=task.marking:
            bullety0,bullety1=y+i*0.8*data.bulletDim+data.taskDropDownM,y+(i+1)*0.8*data.bulletDim
            if bulletx0<data.x<bulletx1 and bullety0<data.y<bullety1:
                task.marking=marking
                task.selected=False
                data.anyTaskSelected=False
                data.currLog.unshiftAll()
            i+=1
    checkMigration(data,task)

def checkMigration(data,task):
    newDate=data.currLog.date+datetime.timedelta(days=1)
    index=getDateIndex(data.logList,newDate)
    if index==None: #tomorrow's log hasn't been made yet
        newLog=DayLog(newDate,data)
        addLog(data.logList,newLog)
    else: newLog=data.logList[index]
    if task.marking=="migrated":
        newTask=copy.deepcopy(task)
        newTask.marking="incomplete"
        newLog.addItem(newTask)
    else: #if task is not migrated, make sure it's not in tomorrow's log
        for item in copy.deepcopy(newLog.itemSet):
            if item.name==task.name:
                newLog.deleteItem(item)

def checkSortByMenuSelections(data):
    i=1
    for sortMode in data.sortModeDict:
        if sortMode!=data.sortMode:
            y0,y1=data.height/5+data.sortDropDownHeight*i,data.height/5+data.sortDropDownHeight*(i+1)
            if data.sortbyx0<data.x<data.sortbyx1 and y0<data.y<y1:
                data.sortMode=sortMode
                data.showSortByDropdown=False
            i+=1

def checkEditScreenSelections(data):
    if data.selectTimeScreen: checkTimeScreenSelections(data)
    else:
        #name field
        if data.nameFieldx0<data.x<data.nameFieldx1 and data.nameFieldy0<data.y<data.nameFieldy1:
            data.isUpdatingName=True
            if data.currLog.getEditingTask()==None:
              data.isUpdatingName=True
              data.inHourField=False
              data.inMinuteField=False
              data.currLog.addItem(Task(""))
        else: data.isUpdatingName=False
        #group field
        groupFieldx0,groupFieldy0=data.nameFieldx0*9/8+data.outerMarginX,data.nameFieldy1*9/8
        groupFieldx1,groupFieldy1=groupFieldx0+data.bulletDim,groupFieldy0+data.bulletDim
        if groupFieldx0<data.x<groupFieldx1 and groupFieldy0<data.y<groupFieldy1:
            if data.currTask==None or data.currTask.name=="": data.createNameErrorMessage=True
            else: data.currTask.toggleGroup()
        #priority field
        if data.checkx0<data.x<data.checkx1 and data.checky0<data.y<data.checky1:
            if data.currTask==None or data.currTask.name=="": data.createNameErrorMessage=True
            else: data.currTask.togglePriority()
        #time field
        if data.timeFieldx0<data.x<data.timeFieldx1 and data.timeFieldy0<data.y<data.timeFieldy1:
            if data.currTask==None or data.currTask.name=="": data.createNameErrorMessage=True
            else:
                data.selectTimeScreen=True
        #duration field
        if data.durationHourx0<data.x<data.durationHourx1 and data.durationHoury0<data.y<data.durationHoury1:
            if data.currTask==None or data.currTask.name=="": data.createNameErrorMessage=True
            data.inHourField=True
            data.inMinuteField=False
            data.isUpdatingName=False
        else: data.inHourField=False
        if data.durationMinutex0<data.x<data.durationMinutex1 and data.durationMinutey0<data.y<data.durationMinutey1:
            if data.currTask==None or data.currTask.name=="": data.createNameErrorMessage=True
            data.inMinuteField=True
            data.inHourField=False
            data.isUpdatingName=False
        else: data.inMinuteField=False
        #submit button
        if data.tasksubmitx0<data.x<data.tasksubmitx1 and data.tasksubmity0<data.y<data.tasksubmity1:
            if data.currTask==None:
                data.createNameErrorMessage=True
            elif durationCorrect(data):
                data.isEditScreen=False
                data.currTask.selected=False
                data.currLog.stopEditingTask()
                data.previousTaskState=None
            else: data.createDurationErrorMessage=True
        #exit button
        if data.taskexitx0<data.x<data.taskexitx1 and data.taskexity0<data.y<data.taskexity1:
            data.isEditScreen=False
            data.currLog.stopEditingTask()
            if data.previousTaskState==None or data.previousTaskState.name=="empty":
                data.currLog.deleteItem(data.currTask)
            else: data.currLog.replaceTask(data,data.currTask,data.previousTaskState)
            data.previousTaskState=None
        #exit button of error message
        if data.createNameErrorMessage or data.createDurationErrorMessage:
            data.inHourField=False
            data.inMinuteField=False
            data.isUpdatingName=False
            if data.errorexitx0<data.x<data.errorexitx1 and data.errorexity0<data.y<data.errorexity1:
              data.createNameErrorMessage=False
              data.createDurationErrorMessage=False

def checkTimeScreenSelections(data):
    if data.timesubmitx0<data.x<data.timesubmitx1 and data.timesubmity0<data.y<data.timesubmity1:
           data.selectTimeScreen=False
    div=(data.width-data.timeMarginX*9/2)/12
    numOfDivs=12
    for hourNum in range(1,numOfDivs+1):
        if (data.timeMarginX*3+div*(hourNum-1)<data.x<data.timeMarginX*3+div*hourNum
            and data.timeMarginY*22/16<data.y<data.timeMarginY*24/16):
            data.currTask.selectedHour=hourNum
            break
    for minuteNum in range(0,(numOfDivs)*5,5):
        if (data.timeMarginX*3+div*minuteNum/5<data.x<data.timeMarginX*3+div*(minuteNum/5+1)
            and data.timeMarginY*28/16<data.y<data.timeMarginY*30/16):
            data.currTask.selectedMinute=minuteNum
            break
    if (data.timeMarginX*3<data.x<data.timeMarginX*3+div*2
        and data.timeMarginY*25/16<data.y<data.timeMarginY*27/16):
        data.currTask.selectedAMPM="AM"
    elif (data.timeMarginX*3+div*2<data.x<data.timeMarginX*3+div*4
        and data.timeMarginY*25/16<data.y<data.timeMarginY*27/16):
        data.currTask.selectedAMPM="PM"
    #adjust the hour according the "AM" or "PM"
    if data.currTask.selectedAMPM=="AM":
        if data.currTask.selectedHour==12: hour=0
        else: hour=data.currTask.selectedHour
    else:
        if data.currTask.selectedHour==12: hour=data.currTask.selectedHour
        else: hour=data.currTask.selectedHour+12
    data.currTask.assignedTime=datetime.datetime(data.year,data.month,data.day,hour,data.currTask.selectedMinute)

def checkQuestionScreenSelections(data):
    question=data.currDaySched.questions[data.currQuestionIndex]
    answersList=question.possibleAnswers
    numAnswers=len(answersList)
    #if there are more than 4 possible answers, split them two lines:
    splitIndex=numAnswers//2 if numAnswers>data.maxAnswersPerLine else numAnswers
    answersPerLine=numAnswers-splitIndex if splitIndex<numAnswers else numAnswers
    distanceBetweenRectangles=(data.width*5/8)/answersPerLine
    margin=1/256
    if numAnswers>answersPerLine: #two lines
        for i in range(splitIndex):
            if (data.width*3/16+distanceBetweenRectangles*(i+1/2)+margin<data.x<data.width*3/16+distanceBetweenRectangles*(i+3/2)-margin
                and data.height*18/32<data.y<data.height*20/32):
                answer=answersList[i]
                data.currDaySched.questions[data.currQuestionIndex].answer=answer
                data.currQuestionIndex+=1
        for i in range(numAnswers-splitIndex):
            if (data.width*3/16+distanceBetweenRectangles*i+margin<data.x<data.width*3/16+distanceBetweenRectangles*(i+1)-margin
                and data.height*21/32<data.y<data.height*23/32):
                answer=answersList[i+splitIndex]
                data.currDaySched.questions[data.currQuestionIndex].answer=answer
                data.currQuestionIndex+=1
    else: #one line
        for i in range(numAnswers):
            if (data.width*3/16+distanceBetweenRectangles*i+margin<data.x<data.width*3/16+distanceBetweenRectangles*(i+1)-margin
                and data.height*20/32<data.y<data.height*22/32):
                answer=answersList[i]
                data.currDaySched.questions[data.currQuestionIndex].answer=answer
                data.currQuestionIndex+=1
    if data.currQuestionIndex==len(data.currDaySched.questions):
        data.isQuestionScreen=False
        interpretAnswers(data)

def checkScheduleScreenSelections(data):
    #menu button
    if (data.menux0<data.x<data.menux1 and data.menuy0<data.y<data.menuy1):
        data.isScheduleScreen=False
        data.isMenu=True

def checkScheduleErrorScreenSelections(data):
    if data.continuex0<data.x<data.continuex1 and data.continuey0<data.y<data.continuey1:
        data.scheduleError=False
        data.isMenu=True

#everything else:

def keyPressed(event, data):
    if data.isOpeningScreen:
        if event.keysym=="Return":
            #user did not enter anything:
            if data.username=="": data.isErrorScreen=True
            else:
                data.isOpeningScreen=False
                data.isEditingUsername=False
                data.isMenu=True
        if data.isEditingUsername:
            if event.keysym in string.printable: data.username+=event.keysym
            elif event.keysym=="space": data.username+=" "
            elif event.keysym=="BackSpace": data.username=data.username[:-1]
    elif data.isEditScreen:
        if data.isUpdatingName:
            if data.currTask==None: pass
            elif event.keysym in string.printable: data.currTask.name+=event.keysym
            elif event.keysym=="space": data.currTask.name+=" "
            elif event.keysym=="BackSpace": data.currTask.name=data.currTask.name[:-1]
        elif data.inHourField:
            if event.keysym in string.digits:
                if len(data.currTask.durationHour)==2: pass
                else: data.currTask.durationHour+=event.keysym
            elif event.keysym=="BackSpace": data.currTask.durationHour=data.currTask.durationHour[:-1]
        elif data.inMinuteField:
            if event.keysym in string.digits:
                if len(data.currTask.durationMinute)==2: pass
                else: data.currTask.durationMinute+=event.keysym
            elif event.keysym=="BackSpace": data.currTask.durationMinute=data.currTask.durationMinute[:-1]

def timerFired(data):
    #make fields have blinkingCursor
    data.itemList=data.currLog.getSortedList(data.sortMode)
    data.timesFired+=1
    data.currTask=data.currLog.getEditingTask()
    if (data.isEditingUsername or data.isUpdatingName or data.inHourField or data.inMinuteField) and data.timesFired%6==0:
        if data.blinkingCursor==" ": data.blinkingCursor="|"
        else: data.blinkingCursor=" "
    elif data.isEditingUsername==False: data.blinkingCursor=" "
    elif data.isUpdatingName==False: data.blinkingCursor=" "

def redrawAll(canvas, data):
    if data.isOpeningScreen:
        drawOpeningScreen(canvas,data)
        if data.isErrorScreen: drawErrorScreen(canvas,data)
    elif data.isMenu: drawMenu(canvas,data)
    elif data.isDailyLog:
        drawDailyLog(canvas,data)
        if data.isEditScreen:
            drawTaskEditScreen(canvas,data)
            if data.createNameErrorMessage: drawNameErrorMessage(canvas,data)
            if data.createDurationErrorMessage: drawDurationErrorMessage(canvas,data)
            if data.selectTimeScreen: drawSelectTimeScreen(canvas,data)
        elif data.showSortByDropdown: drawSortByDropdown(canvas,data)
    elif data.isQuestionScreen: drawQuestionScreen(canvas,data)
    elif data.isScheduleScreen: drawScheduleScreen(canvas,data)
    elif data.isHelp: drawHelpScreen(canvas,data)
    elif data.scheduleError: drawScheduleError(canvas,data)

####################################
# Draw functions
####################################

#Opening
def drawOpeningScreen(canvas,data):
    canvas.create_image(data.width/2,data.height*3/8,image=data.enterUsernameImage)
    nameField=data.username+data.blinkingCursor
    canvas.create_text(data.width/2,data.height*19/32,text=nameField,font="Cambria 26")
    canvas.create_line(data.width/8,data.height*5/8,data.width*7/8,data.height*5/8)
    canvas.create_rectangle(data.width/3,data.height*3/4,data.width*2/3,data.height*13/16,fill=data.color1)
    canvas.create_image(data.width/2,data.height*25/32,image=data.submitButtonImage)
    canvas.create_text(data.width/2,data.height*29/32,text="Click 'Submit' or press 'Enter' to continue",font="Verdana 14")

def drawErrorScreen(canvas,data):
    #shadow
    canvas.create_rectangle(data.errorMarginX+data.shadowMargin,
        data.errorMarginY+data.shadowMargin,data.width-data.errorMarginX+data.shadowMargin,
        data.height-data.errorMarginY+data.shadowMargin,fill="gray")
    #window
    canvas.create_rectangle(data.errorMarginX,data.errorMarginY,data.width-data.errorMarginX,
        data.height-data.errorMarginY,fill=data.color1)
    #text
    canvas.create_text(data.width/2,data.height*7/16,text="Please enter a",font="Cambria 24")
    canvas.create_text(data.width/2,data.height*9/16,text="valid username!",font="Cambria 24")
    #exit button
    canvas.create_rectangle(data.errorexitx0,data.errorexity0,data.errorexitx1,data.errorexity1,fill=data.exitButtonColor)
    canvas.create_line(data.errorexitx0,data.errorexity0,data.errorexitx1,data.errorexity1,width=2)
    canvas.create_line(data.errorexitx1,data.errorexity0,data.errorexitx0,data.errorexity1,width=2)

#Menu
def drawMenu(canvas,data):
    canvas.create_text(data.width/2,data.height/8, text=data.username+"'s Bullet Journal", font="Verdana 28")
    canvas.create_image(data.width/2,data.height*11/32,image=data.dailyLogImage)
    canvas.create_image(data.width/2,data.height*20/32,image=data.planMyDayImage)
    canvas.create_image(data.width/2,data.height*28/32,image=data.helpButtonImage)

#Help
def drawHelpScreen(canvas,data):
    if data.isHelpScreen1: image=data.helpScreen1
    elif data.isHelpScreen2: image=data.helpScreen2
    elif data.isHelpScreen3: image=data.helpScreen3
    elif data.isHelpScreen4: image=data.helpScreen4
    elif data.isHelpScreen5: image=data.helpScreen5
    elif data.isHelpScreen6: image=data.helpScreen6
    canvas.create_image(data.width/2,data.height/2,image=image)

#Daily Log
def drawDailyLog(canvas,data):
    canvas.create_image(data.width/2,data.height/16,image=data.smallDailyLogImage)
    #date and arrows
    canvas.create_polygon(data.width/8,data.height/7,data.width/8+data.arrowSize,data.height/7-data.arrowSize,
                        data.width/8+data.arrowSize,data.height/7+data.arrowSize,fill=data.color2,outline="black")
    canvas.create_polygon(data.width*7/8,data.height/7,data.width*7/8-data.arrowSize,data.height/7-data.arrowSize,
                        data.width*7/8-data.arrowSize,data.height/7+data.arrowSize,fill=data.color2,outline="black")
    drawDate(canvas,data)
    #"sort by" dropdown
    drawSortByMenu(canvas,data)
    #task box
    canvas.create_rectangle(data.width/8,data.height/4,data.width*7/8,data.height*7/8,fill=data.color1)
    #only update the drawn item list when the user finishes editing the current task:
    if data.currLog.getEditingTask()==None: drawItemList(canvas,data)
    #plus button
    canvas.create_oval(data.width*27/32,data.height*29/32, data.width*27/32+data.plusButtonDiameter,
        data.height*29/32+data.plusButtonDiameter,fill=data.color2,width=2)
    canvas.create_text(data.width*27/32+data.plusButtonDiameter/2,data.height*29/32+data.plusButtonDiameter/2,
        text="+",font="Times 32")
    #menu button
    canvas.create_rectangle(data.width*1/32,data.height*29/32,data.width*5/32,data.height*31/32,fill=data.color2)
    canvas.create_image(data.width*4/32,data.height*15/16,image=data.menuButtonImage)

def drawDate(canvas,data):
    date=data.currLog.date
    month="0"+str(date.month) if date.month<10 else str(date.month)
    day="0"+str(date.day) if date.day<10 else str(date.day)
    year=str(date.year)
    dateString=month+"/"+day+"/"+year
    canvas.create_text(data.width*3/8,data.height/7,text=dateString,font="Cambria 18")
    canvas.create_rectangle(data.width*9/16,data.height*7/56,data.width*3/4,data.height*9/56,fill=data.color2,width=2)
    canvas.create_text(data.width*21/32,data.height/7,text="Today",font="Cambria 12")

def drawItemList(canvas,data):
    for item in data.itemList:
        bulletx0,bullety0=data.width/4-data.bulletDim/2,data.height/4+(item.row+1)*data.taskMargin-data.bulletDim/2
        bulletx1,bullety1=bulletx0+data.bulletDim,bullety0+data.bulletDim
        drawBullet(canvas,item.marking,item,data,bulletx0,bullety0,bulletx1,bullety1)
        canvas.create_text(data.width*3/8,data.height/4+(item.row+1)*data.taskMargin,text=item.name,anchor=W,font="Cambria 12")
        if item.selected: drawTaskDropdown(canvas,item,data)

def drawBullet(canvas,marking,item,data,x0,y0,x1,y1):
    bulletDim=x1-x0
    width=bulletDim*.2
    canvas.create_rectangle(x0,y0,x1,y1,fill=item.getColor(data))
    if marking=="incomplete": pass
    elif marking=="started": canvas.create_line(x0,y0,x1,y1,width=width)
    elif marking=="migrated":
        canvas.create_line(x0-bulletDim/4,y0+bulletDim/2,x1,y0+bulletDim/2,width=width)
        canvas.create_line(x0+bulletDim/2,y0,x1,y0+bulletDim/2,width=width)
        canvas.create_line(x0+bulletDim/2,y1,x1,y0+bulletDim/2,width=width)
    elif marking=="completed": canvas.create_rectangle(x0+bulletDim/8,y0+bulletDim/8,x1-bulletDim/8,y1-bulletDim/8,fill="black")
    elif marking=="cancelled": canvas.create_line(x0,y0+bulletDim/2,x1,y0+bulletDim/2,width=width)

def drawTaskDropdown(canvas,task,data):
    data.currTask=data.currLog.getSelectedTask()
    x,y=data.width/4-data.bulletDim/2,data.height/4+(task.row+1)*data.taskMargin+data.bulletDim/2+data.taskDropDownM
    canvas.create_rectangle(x,y,x+data.bulletDim,y+3.3*data.bulletDim)
    bulletx0=x+data.taskDropDownM
    bulletx1=bulletx0+data.bulletDim-data.taskDropDownM*2
    i=0
    for index in range(len(data.invertedMarkingDict)):
        marking=data.invertedMarkingDict[index]
        if marking!=task.marking:
            bullety0,bullety1=y+i*0.8*data.bulletDim+data.taskDropDownM,y+(i+1)*0.8*data.bulletDim
            drawBullet(canvas,marking,task,data,bulletx0,bullety0,bulletx1,bullety1)
            i+=1
    #edit and delete buttons
    edity0,edity1=y,y+data.bulletDim
    deletey0,deletey1=y,y+data.bulletDim
    canvas.create_rectangle(data.editx0,edity0,data.editx1,edity1,fill=data.color2)
    canvas.create_rectangle(data.deletex0,deletey0,data.deletex1,deletey1,fill=data.color2)
    canvas.create_text((data.editx0+data.editx1)/2,(edity0+edity1)/2,text="Edit",font="Cambria 8")
    canvas.create_text((data.deletex0+data.deletex1)/2,(deletey0+deletey1)/2,text="Delete",font="Cambria 8")
    #time and duration
    canvas.create_rectangle(data.editx0,edity1*65/64,data.deletex1*21/16,edity1*37/32,fill=data.backgroundColor)
    durationText="Duration: "+task.getDurationString()
    canvas.create_text(data.editx0*33/32,edity1*34/32,text=durationText,font="Cambria 8",anchor=W)
    assignedTimeText=data.currTask.getHourMinute()
    if assignedTimeText==":": assignedTimeText="No assigned time"
    canvas.create_text(data.editx0*33/32,edity1*36/32,text=assignedTimeText,anchor=W,font="Cambria 8")

def drawSortByMenu(canvas,data):
    canvas.create_text(data.width/3,data.height/5+data.sortDropDownHeight/2,text="Sort by:",font="Cambria 12")
    canvas.create_rectangle(data.width/3+data.sortDropDownM,data.height/5,data.width*2/3,
        data.height/5+data.sortDropDownHeight,fill=data.color2,width=2)
    canvas.create_text(data.width/2+data.sortDropDownM/2,data.height/5+data.sortDropDownHeight/2,
        text=getSortModeString(data.sortMode),font="Cambria 10")

def drawSortByDropdown(canvas,data):
    x0,x1=data.width/3+data.sortDropDownM,data.width*2/3
    i=1
    for sortMode in data.sortModeDict:
        if sortMode!=data.sortMode:
            y0,y1=data.height/5+data.sortDropDownHeight*i,data.height/5+data.sortDropDownHeight*(i+1)
            canvas.create_rectangle(x0,y0,x1,y1,fill=data.backgroundColor)
            canvas.create_text(data.width/2+data.sortDropDownM/2,y1/2+y0/2,
                    text=getSortModeString(sortMode),font="Cambria 8")
            i+=1

def drawTaskEditScreen(canvas,data):
    task=data.currTask
    #outer box shadow
    canvas.create_rectangle(data.outerMarginX+data.shadowMargin,data.outerMarginY+data.shadowMargin,
        data.width-data.outerMarginX+data.shadowMargin,data.height-data.outerMarginY/2+data.shadowMargin,fill="gray")
    #outer box
    canvas.create_rectangle(data.outerMarginX,data.outerMarginY,data.width-data.outerMarginX,
        data.height-data.outerMarginY/2,fill=data.backgroundColor)
    #title text
    canvas.create_text(data.width/2,data.outerMarginY*19/16,text="Edit Task",font="Cambria 18")
    #exit button
    canvas.create_rectangle(data.taskexitx0,data.taskexity0,data.taskexitx1,data.taskexity1,fill=data.exitButtonColor)
    canvas.create_line(data.taskexitx0,data.taskexity0,data.taskexitx1,data.taskexity1,width=2)
    canvas.create_line(data.taskexitx1,data.taskexity0,data.taskexitx0,data.taskexity1,width=2)
    #name field
    canvas.create_rectangle(data.nameFieldx0,data.nameFieldy0,data.nameFieldx1,data.nameFieldy1,fill=data.color2)
    blinkingCursor=" " if data.inHourField or data.inMinuteField else data.blinkingCursor
    nameField="<click to enter task name>" if task==None else task.name+blinkingCursor
    canvas.create_text(data.nameFieldx0/2+data.nameFieldx1/2,data.nameFieldy0/2+data.nameFieldy1/2,
        text=nameField,font="Cambria 12")
    canvas.create_text(data.nameFieldx1,data.nameFieldy1*33/32,text="*this field is required",font="Cambria 8",anchor=E)
    #group field
    groupX,groupY=data.nameFieldx0*9/8,data.nameFieldy1*9/8
    canvas.create_text(groupX,groupY,text="Group:",font="Cambria 12",anchor=NW)
    groupColor=data.backgroundColor if task==None else task.getColor(data)
    groupText="None" if task==None else task.group
    canvas.create_rectangle(groupX+data.outerMarginX,groupY,groupX+data.outerMarginX+data.bulletDim,
        groupY+data.bulletDim,fill=groupColor)
    canvas.create_text(groupX+data.outerMarginX*3/2,groupY,text=("(",getGroupString(groupText),")"),font="Cambria 10",anchor=NW)
    #priority field
    canvas.create_text(data.priorityX,data.priorityY,text="Priority:",font="Cambria 12",anchor=NW)
    canvas.create_rectangle(data.checkx0,data.checky0,data.checkx1,data.checky1,width=2)
    if task!=None and task.priority==True:
        canvas.create_line(data.checkx0,data.checky0,data.checkx0/2+data.checkx1/2,data.checky1,width=2,fill=data.color2)
        canvas.create_line(data.checkx0/2+data.checkx1/2,data.checky1,data.checkx1+data.checkmarkDim*3/4,
            data.checky0-data.checkmarkDim*3/4,width=3,fill=data.color2)
    #time field
    timeX,timeY=groupX,data.nameFieldy1*3/2
    canvas.create_text(timeX,timeY,text="Time:",font="Cambria 12",anchor=NW)
    timeText=task.getHourMinute() if task!=None else ":"
    canvas.create_rectangle(data.timeFieldx0,data.timeFieldy0,data.timeFieldx1,data.timeFieldy1)
    canvas.create_text(data.timeFieldx0/2+data.timeFieldx1/2,data.timeFieldy0/2+data.timeFieldy1/2,
        text=timeText,font="Cambria 10")
    #duration field
    canvas.create_text(data.durationX,data.durationY,text="Duration:",font="Cambria 12",anchor=NW)
    canvas.create_text(data.nameFieldx1,data.durationY*17/16,text="*this field is required",font="Cambria 8",anchor=E)
    #text for duration fields
    if task==None: durationHour,durationMinute="0","0"
    else: durationHour,durationMinute=task.durationHour,task.durationMinute
    hourText=str(durationHour)+data.blinkingCursor if data.inHourField else str(durationHour)
    minuteText=str(durationMinute)+data.blinkingCursor if data.inMinuteField else str(durationMinute)
    canvas.create_rectangle(data.durationHourx0,data.durationHoury0,data.durationHourx1,data.durationHoury1)
    canvas.create_text(timeX+data.outerMarginX*9/8,data.durationHoury0/2+data.durationHoury1/2,text="Hours",font="Cambria 10")
    canvas.create_text(data.durationHourx0+data.bulletDim/4,data.durationHoury0/2+data.durationHoury1/2,
        text=hourText,font="Cambria 8",anchor=W)
    canvas.create_rectangle(data.durationMinutex0,data.durationMinutey0,data.durationMinutex1,data.durationMinutey1)
    canvas.create_text(data.durationHourx0+data.bulletDim+data.outerMarginX/2,data.durationMinutey0/2+data.durationMinutey1/2,
        text="Minutes",font="Cambria 10")
    canvas.create_text(data.durationMinutex0+data.bulletDim/4,data.durationMinutey0/2+data.durationMinutey1/2,
        text=minuteText,font="Cambria 8",anchor=W)
    canvas.create_image(data.width/2,data.height*26/32,image=data.smallSubmitButtonImage)

def drawSelectTimeScreen(canvas,data):
    div=(data.width-data.timeMarginX*9/2)/12
    numOfDivs=12
    minsPerDiv=5
    #shadow
    canvas.create_rectangle(data.timeMarginX+data.shadowMargin,data.timeMarginY+data.shadowMargin,
        data.width-data.timeMarginX+data.shadowMargin,data.height-data.timeMarginY+data.shadowMargin,fill="gray")
    #window
    canvas.create_rectangle(data.timeMarginX,data.timeMarginY,data.width-data.timeMarginX,
        data.height-data.timeMarginY,fill=data.backgroundColor)
    #title
    canvas.create_text(data.width/2,data.timeMarginY*19/16,text="Edit Time",font="Cambria 20")
    #hour label
    canvas.create_text(data.timeMarginX*2,data.timeMarginY*23/16,text="Hour:",font="Cambria 14")
    canvas.create_rectangle(data.timeMarginX*3,data.timeMarginY*11/8,data.width-data.timeMarginX*3/2,data.timeMarginY*3/2)
    #minute label
    canvas.create_text(data.timeMarginX*2,data.timeMarginY*29/16,text="Minute:",font="Cambria 14")
    canvas.create_rectangle(data.timeMarginX*3,data.timeMarginY*28/16,data.width-data.timeMarginX*3/2,data.timeMarginY*30/16)
    divNum=1
    while divNum<numOfDivs+1:
        #hour text
        hourText=str(divNum) if divNum>=10 else "0"+str(divNum)
        canvas.create_line(data.timeMarginX*3+div*divNum,data.timeMarginY*22/16,
            data.timeMarginX*3+div*divNum,data.timeMarginY*24/16)
        canvas.create_text(data.timeMarginX*3+div*(divNum-1)+div/2,data.timeMarginY*23/16,text=hourText,font="Cambria 8")
        #highlight selected hour
        if data.currTask.selectedHour==divNum:
            canvas.create_rectangle(data.timeMarginX*3+div*(divNum-1),data.timeMarginY*22/16,
                data.timeMarginX*3+div*divNum,data.timeMarginY*24/16,outline=data.color2,width=2)
        #minute text
        minuteText=str((divNum-1)*minsPerDiv) if (divNum-1)*minsPerDiv>=10 else "0"+str((divNum-1)*minsPerDiv)
        canvas.create_line(data.timeMarginX*3+div*divNum,data.timeMarginY*28/16,
            data.timeMarginX*3+div*divNum,data.timeMarginY*30/16)
        canvas.create_text(data.timeMarginX*3+div*(divNum-1)+div/2,data.timeMarginY*29/16,text=minuteText,font="Cambria 8")
        #highlight selected minute
        if data.currTask.selectedMinute==(divNum-1)*5:
            canvas.create_rectangle(data.timeMarginX*3+div*(divNum-1),data.timeMarginY*28/16,
                data.timeMarginX*3+div*divNum,data.timeMarginY*30/16,outline=data.color2,width=2)
        divNum+=1
    #AM or PM
    canvas.create_rectangle(data.timeMarginX*3,data.timeMarginY*25/16,data.timeMarginX*3+div*4,data.timeMarginY*27/16)
    canvas.create_line(data.timeMarginX*3+div*2,data.timeMarginY*25/16,data.timeMarginX*3+div*2,data.timeMarginY*27/16)
    canvas.create_text(data.timeMarginX*3+div,data.timeMarginY*26/16,text="AM",font="Cambria 10")
    canvas.create_text(data.timeMarginX*3+div*3,data.timeMarginY*26/16,text="PM",font="Cambria 10")
    #highlight selected AMPM
    if data.currTask.selectedAMPM=="AM":
        canvas.create_rectangle(data.timeMarginX*3,data.timeMarginY*25/16,
            data.timeMarginX*3+div*2,data.timeMarginY*27/16,outline=data.color2,width=2)
    else:
        canvas.create_rectangle(data.timeMarginX*3+div*2,data.timeMarginY*25/16,
            data.timeMarginX*3+div*4,data.timeMarginY*27/16,outline=data.color2,width=2)
    #submit button
    canvas.create_image(data.width/2,data.timesubmity0/2+data.timesubmity1/2,image=data.smallSubmitButtonImage)

def drawNameErrorMessage(canvas,data):
    #shadow
    canvas.create_rectangle(data.errorMarginX+data.shadowMargin,data.errorMarginY+data.shadowMargin,
        data.width-data.errorMarginX+data.shadowMargin,data.height-data.errorMarginY+data.shadowMargin,fill="gray")
    #window
    canvas.create_rectangle(data.errorMarginX,data.errorMarginY,data.width-data.errorMarginX,
        data.height-data.errorMarginY,fill=data.color2)
    #text
    canvas.create_text(data.width/2,data.height/2,text="Enter a task name first!",font="Cambria 18")
    #exit button
    canvas.create_rectangle(data.errorexitx0,data.errorexity0,data.errorexitx1,data.errorexity1,fill=data.exitButtonColor)
    canvas.create_line(data.errorexitx0,data.errorexity0,data.errorexitx1,data.errorexity1,width=2)
    canvas.create_line(data.errorexitx1,data.errorexity0,data.errorexitx0,data.errorexity1,width=2)

def drawDurationErrorMessage(canvas,data):
    #shadow
    canvas.create_rectangle(data.errorMarginX+data.shadowMargin,data.errorMarginY+data.shadowMargin,
        data.width-data.errorMarginX+data.shadowMargin,data.height-data.errorMarginY+data.shadowMargin,fill="gray")
    #window
    canvas.create_rectangle(data.errorMarginX,data.errorMarginY,data.width-data.errorMarginX,
        data.height-data.errorMarginY,fill=data.color2)
    #text
    canvas.create_text(data.width/2,data.height/2,text="Please enter a valid duration!",font="Cambria 18")
    #exit button
    canvas.create_rectangle(data.errorexitx0,data.errorexity0,data.errorexitx1,data.errorexity1,fill=data.exitButtonColor)
    canvas.create_line(data.errorexitx0,data.errorexity0,data.errorexitx1,data.errorexity1,width=2)
    canvas.create_line(data.errorexitx1,data.errorexity0,data.errorexitx0,data.errorexity1,width=2)

#Plan My Day!
def drawQuestionScreen(canvas,data):
    question=data.currDaySched.questions[data.currQuestionIndex]
    canvas.create_image(data.width/2,data.height/8,image=data.smallPlanMyDayImage)
    #current question in the middle
    canvas.create_oval(data.width/10,data.height*2/7,data.width*9/10,data.height*6/7,fill=data.color1)
    maxCharactersPerLine=30
    questionString=str(question)
    if len(questionString)>30: questionSplitIndex=len(questionString)//2
    #look in both directions for a blank space to put the index
    i=1
    while questionString[questionSplitIndex]!=" ":
        if i%2==1: questionSplitIndex+=i
        else: questionSplitIndex-=i
        i+=1
    canvas.create_text(data.width/2,data.height*15/32,text=questionString[:questionSplitIndex],font="Cambria 18")
    canvas.create_text(data.width/2,data.height*17/32,text=questionString[questionSplitIndex:],font="Cambria 18")
    #answer buttons
    answersList=question.possibleAnswers
    numAnswers=len(answersList)
    answerSplitIndex=numAnswers//2 if numAnswers>data.maxAnswersPerLine else numAnswers
    answersPerLine=numAnswers-answerSplitIndex if answerSplitIndex<numAnswers else numAnswers
    distanceBetweenRectangles=(data.width*5/8)/answersPerLine
    if numAnswers>data.maxAnswersPerLine:
        for i in range(answerSplitIndex):
            canvas.create_image(data.width*3/16+distanceBetweenRectangles*(i+1),data.height*19/32,image=data.smallBlankButton)
            canvas.create_text(data.width*3/16+distanceBetweenRectangles*(i+1),data.height*19/32,text=answersList[i],font="Cambria 16")
        for i in range(numAnswers-answerSplitIndex):
            canvas.create_image(data.width*3/16+distanceBetweenRectangles*(i+1/2),data.height*22/32,image=data.smallBlankButton)
            canvas.create_text(data.width*3/16+distanceBetweenRectangles*(i+1/2),
                data.height*22/32,text=answersList[answerSplitIndex+i],font="Cambria 16")
    else:
        for i in range(numAnswers):
            canvas.create_image(data.width*3/16+distanceBetweenRectangles*(i+1/2),data.height*21/32,image=data.smallBlankButton)
            canvas.create_text(data.width*3/16+distanceBetweenRectangles*(i+1/2),
                data.height*21/32,text=answersList[i],font="Cambria 16")

def drawScheduleScreen(canvas,data):
    canvas.create_image(data.width/2,data.height*3/32,image=data.smallPlanMyDayImage)
    canvas.create_text(data.width/2,data.height*3/16,text="Ok "+data.username+", here's what I think",font="Cambria 18")
    canvas.create_text(data.width/2,data.height*15/64,text="your day should look like:",font="Cambria 18")
    canvas.create_rectangle(data.width/8,data.height*9/32,data.width*7/8,data.height*7/8,fill=data.color1)
    drawPlan(canvas,data)
    #menu button
    canvas.create_image(data.width*4/32,data.height*15/16,image=data.menuButtonImage)

def drawPlan(canvas,data):
    #hour labels
    hourDimY=(data.height*19/32)/data.numHoursDaily
    hourDimX=data.width/4
    for hour in range(data.numHoursDaily):
        canvas.create_rectangle(data.width/8,data.height*9/32+hourDimY*hour,data.width/8+hourDimX,
            data.height*9/32+hourDimY*(hour+1))
        canvas.create_line(data.width/8,data.height*9/32+hourDimY*hour,data.width*7/8,
            data.height*9/32+hourDimY*hour)
        hourText=getHourText(hour)
        canvas.create_text(data.width/8+hourDimX/2,data.height*9/32+(2*hourDimY*hour+hourDimY)/2,
            text=hourText,font="Cambria 12")
    #periods
    periodDim=data.width/3
    for period in data.currDaySched.schedule:
        time=period.assignedTime
        duration=period.duration
        dayLength=data.currDaySched.dayLength
        periodx0=data.width*5/8-periodDim/2
        periodx1=data.width*5/8+periodDim/2
        periody0=data.height*9/32+(getFloatTimeDifference(data,data.currDaySched.startTime,time))*hourDimY
        periody1=data.height*9/32+(getFloatTimeDifference(data,data.currDaySched.startTime,time+duration))*hourDimY
        canvas.create_rectangle(periodx0,periody0,periodx1,periody1,fill=period.getColor(data))
        canvas.create_text(periodx0/2+periodx1/2,periody0/2+periody1/2,text=period.name,font="Cambria 10")

def drawScheduleError(canvas,data):
    canvas.create_image(data.width/2,data.height/2,image=data.scheduleErrorScreen)

####################################
# Plan My Day Functions
####################################

def createQuestions(data):
    todayIndex=data.logList.index(data.todayLog)
    #study question
    try:
        tomorrowLog=data.logList[todayIndex+1]
        for item in tomorrowLog.itemSet:
            for word in data.testKeyWords:
                if word in item.name:
                    studyQuestion=getStudyQuestion(data,item)
                    data.currDaySched.addQuestion(studyQuestion)
    except: pass
    #sleep question
    data.sleepQuestion=None
    data.sleepQuestion=getSleepQuestion(data)
    data.currDaySched.addQuestion(data.sleepQuestion)

def getSleepQuestion(data): #determines when user should go to bed to get 8 hours of sleep
    text="What time do you plan on waking up tomorrow?"
    question=Question(text)
    question.addPossibleAnswer("8:00 AM","8:30 AM","9:00 AM","9:30 AM","10:00 AM")
    return question

def getStudyQuestion(data,item):
    text="Do you want to find time to study for tomorrow's %s?" % item.name
    question=StudyQuestion(text,item)
    question.addPossibleAnswer("Yes","No")
    return question

def interpretAnswers(data):
    data.currDaySched.sleepTime=getDateTimeFromString(data,data.sleepQuestion.answer)-datetime.timedelta(hours=8)
    sleepTask=Task("Sleep",assignedTime=data.currDaySched.sleepTime,durationHour="8",group="health")
    data.todayLog.addItem(sleepTask)
    for question in data.currDaySched.questions: #add the study periods as tasks
        if isinstance(question,StudyQuestion):
            if question.answer=="Yes":
                studyTaskName="Study for %s" % question.test.name
                studyTask=Task(studyTaskName,durationHour="2",group="school")
                data.todayLog.addItem(studyTask)
    schedule=constructSchedule(data)
    if scheduleBlank(data,schedule):
        data.scheduleError=True
        data.isScheduleScreen=False
        for item in list(data.currLog.itemSet):
            item.isEditing=False
            if item==sleepTask: data.currLog.deleteItem(sleepTask)
    else:
        data.isScheduleScreen=True
        for item in schedule:
            item.isEditing=False
            data.currDaySched.addPeriod(item)

def scheduleBlank(data,schedule):
    if schedule==None: return True
    for task in schedule:
        if task.assignedTime==None: return True
    return False

def constructSchedule(data): #backtracking!
    schedule=[]*len(data.todayLog.itemSet)
    itemsWithoutTimes=[]
    for item in data.todayLog.itemSet: #add items already with an assigned time
        if item.assignedTime!=None: schedule.append(item)
        else: itemsWithoutTimes.append(item)
    def isAvailable(data,testTime,duration):
        for task in schedule:
            if task.assignedTime<=testTime<task.assignedTime+task.duration:
                #start time overlaps with existing tasks
                return False
            if (task.assignedTime<testTime+duration<task.assignedTime+task.duration
                or testTime<task.assignedTime<testTime+duration
                or testTime<task.assignedTime+duration<testTime+duration):
                #duration overlaps with existing tasks
                return False
        return True
    def solve(itemIndex=0):
        if itemIndex==len(itemsWithoutTimes): return schedule
        else:
            item=itemsWithoutTimes[itemIndex]
            for hour in range(data.numHoursDaily):
                testTime=datetime.datetime(data.year,data.month,data.day,hour=hour)
                if isAvailable(data,testTime,item.duration):
                    item.assignedTime=testTime
                    schedule.append(item)
                    solution=solve(itemIndex+1)
                    if solution!=None: return solution
                    item.assignedTime=None
                    schedule.remove(item)
            return None
    return solve()

####################################
# Controller Helper Functions
####################################

def getSortModeString(sortMode):
    if sortMode=="name": return "Name"
    elif sortMode=="assignedTime": return "Assigned Time"
    elif sortMode=="timeCreated": return "Time Created"
    elif sortMode=="group": return "Group"
    elif sortMode=="priority": return "Priority"
    elif sortMode=="marking": return "Bullet Marking"

def getGroupString(groupText):
    return None if groupText==None else capitalized(groupText)

def capitalized(str):
    firstLetter=str[0]
    if firstLetter in string.ascii_uppercase: return str
    updatedLetter=chr(ord(firstLetter)-32)
    return updatedLetter+str[1:]

def distance(x0,y0,x1,y1):
    return ((x1-x0)**2+(y1-y0)**2)**0.5

def changeDate(data,deltaDays):
    newDate=data.currLog.date+datetime.timedelta(days=deltaDays)
    newDateIndex=getDateIndex(data.logList,newDate)
    if newDateIndex==None:
        data.currLog=DayLog(newDate,data)
        addLog(data.logList,data.currLog)
    else: data.currLog=data.logList[newDateIndex]

def getDateIndex(logList,date,returnAppendLocationIfNotFound=False):
    #binary search algorithm adapted from
    #https://interactivepython.org/runestone/static/pythonds/SortSearch/TheBinarySearch.html
    first=0
    last=len(logList)-1
    found=False
    while first<=last and not found:
        midpoint=(first+last)//2
        if logList[midpoint].date==date: found=True
        else:
            if date<logList[midpoint].date: last=midpoint-1
            else: first=midpoint+1
    if found: return midpoint
    elif returnAppendLocationIfNotFound: return first
    else: return None

def addLog(logList,log):
    index=getDateIndex(logList,log.date,True)
    logList.insert(index,log)

def durationCorrect(data):
    if data.currTask.durationHour.startswith("0") and data.currTask.durationMinute=="0": return False
    if data.currTask.durationMinute!="0" and  data.currTask.durationMinute.startswith("0"): return False
    if int(data.currTask.durationHour)>24 or int(data.currTask.durationMinute)>60: return False
    data.currTask.duration=datetime.timedelta(hours=int(data.currTask.durationHour),minutes=int((data.currTask.durationMinute)))
    return True

def getHourText(hour):
    if hour==0: return str(hour+12)+":00 AM"
    elif hour<12: return str(hour)+":00 AM"
    elif hour==12: return str(hour)+":00 PM"
    else: return str(hour-12)+":00 PM"

def getDateTimeFromString(data,timeString):
    colonIndex=timeString.find(":")
    hour=int(timeString[:colonIndex])
    minuteLen=2
    minute=int(timeString[colonIndex+1:colonIndex+1+minuteLen])
    return datetime.datetime(data.year,data.month,data.day,hour=hour,minute=minute)

def getFloatTimeDifference(data,time1,time2):
    hour1,minute1,hour2,minute2=time1.hour,time1.minute,time2.hour,time2.minute
    float1=hour1+minute1/data.minPerHour
    float2=hour2+minute2/data.minPerHour
    return (float2-float1)

####################################
# run function
####################################

def run(width=300, height=300):
    root = Tk()
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill=data.backgroundColor, width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()
    print("bye!")

run(500, 700)
