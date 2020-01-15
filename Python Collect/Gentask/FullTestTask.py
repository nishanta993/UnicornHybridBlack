import numpy
import random 
import pandas
import time
from psychopy import visual, core, event
import Engine.unicornhybridblack as unicornhybridblack

targetsize = 1.2
nontargetsize = 0.6
totaltrials = 20
targetprobability = 0.2

# create target arrays
targettrials = [targetsize] * int(numpy.floor(totaltrials * targetprobability))
nontargettrials = [nontargetsize] * (int(numpy.floor(totaltrials * (1-targetprobability)))-2)
trialsequence = targettrials + nontargettrials
random.shuffle(trialsequence)
trialsequence = [nontargetsize, nontargetsize] + trialsequence

# create event codes
eventcodes = [5] * len(trialsequence)
for incrX in range(len(trialsequence)):
    if (trialsequence[incrX] == targetsize):
        eventcodes[incrX] = 10

# stimulus parameters
stimdurationinsec = .300
trialdurationinsec = 1.0
refreshrate = 1 / 60.0
participantkeys = ['1', '2', '3', '4']


# task setup
cumulativeTime = core.Clock()
participantwin = visual.Window(size = (800,800), fullscr = False, screen = 0, allowGUI = False, allowStencil = False, monitor = 'testMonitor', color = '#000000', colorSpace = 'rgb')

participantwin.flip()   

# connect to Device
UnicornBlack = unicornhybridblack.UnicornBlackFunctions() 
UnicornBlack.connect(deviceID='UN-2019.05.51')
time.sleep(1) # give it some initialization time

UnicornBlack.startrecording('oddballtest')
time.sleep(5) #lets get data rolling before we start

targetstimuli = visual.Circle(participantwin, radius=[0.1, 0.1], pos = [0,0], fillColor='#FFFFFF', lineColor='#FFFFFF', autoLog=False)
responsetracking = []
      
event.BuilderKeyResponse()
event.clearEvents()                        
                              
elapsedTime = core.Clock(); 
cumulativeTime.reset()
trial = 0
stimulusisbeingdisplayed = False

continueTrial = True
continueExperiment = True
while continueExperiment:                              
          
    if (trial >= len(trialsequence)):
        continueExperiment = False
        break                    
         
    if event.getKeys(["escape", "q"]): # Check for kill keys
        continueExperiment = False
        break                 
                              
    continueTrial = True
    
    # set the new stimulus
    stimradiusInitial = ((trialsequence[trial]/500)*100, (trialsequence[trial]/500)*100)
    targetstimuli.setRadius(stimradiusInitial)
    targetstimuli.setAutoDraw(True)
    
    elapsedTime.reset()
    participantwin.flip(); 
    UnicornBlack.mark_event(eventcodes[trial]) # Send trigger 
              
    stimulusisbeingdisplayed = True
                          
    while continueTrial:
        turnstimoff = False # trial starts with stimulus on
        
        if (float(numpy.sum([elapsedTime.getTime(),refreshrate])) > float(trialdurationinsec)): # is the trial out of time
            continueTrial = False
            trial = trial + 1
        else:
                
            if stimulusisbeingdisplayed: 
                # should stim be off
                if (float(numpy.sum([elapsedTime.getTime(),refreshrate])) > float(stimdurationinsec)): # If stimulus duration has expired
                    turnstimoff = True
            
            # To avoid tying RT to the monitor refresh rate, this loops for most of the refresh rate period
            checkkeytimer = core.CountdownTimer(start=(float(numpy.multiply(float(0.8),float(refreshrate)))))
            while (checkkeytimer.getTime() > 0):
                
                theseKeys = event.getKeys(keyList=participantkeys, timeStamped=cumulativeTime)
                if (len(theseKeys) > 0): #at least one key was pressed
                    responsetracking.append(theseKeys[0])
                    UnicornBlack.mark_event(theseKeys[0][0]) # Send trigger 
                        
                if event.getKeys(["escape", "q"]): # Check for kill keys
                    continueExperiment = False
                    continueTrial = False
                    break   
            
        if turnstimoff:
            targetstimuli.setAutoDraw(False)
            stimulusisbeingdisplayed = False
            participantwin.flip()

# stop recording
UnicornBlack.disconnect()
                
event.clearEvents()                          
respmatrix  = pandas.DataFrame(columns = ['Event', 'Onset', 'Type'])
for trial in range(0,len(responsetracking)):
    respmatrix.at[trial,'Event'] = 'Response'
    respmatrix.at[trial,'Onset'] = numpy.float32(responsetracking[trial][1])
    respmatrix.at[trial,'Type'] = int(responsetracking[trial][0])                              
                

participantwin.close()
del refreshrate, stimdurationinsec, trialdurationinsec, participantkeys, eventcodes, nontargetsize, nontargettrials, targetprobability, targetsize, targettrials, totaltrials
del targetstimuli, trialsequence, continueTrial, continueExperiment, participantwin, turnstimoff, stimulusisbeingdisplayed, theseKeys, trial
del stimradiusInitial
del responsetracking, incrX

print("Elapsed time: %.6f" % cumulativeTime.getTime())
del  cumulativeTime


# take a look at the dropped samples
import matplotlib.pyplot as plt 
sampleddata = UnicornBlack.data

selectsampleddata = []
for incrX in range(len(sampleddata)):
    if not (sampleddata[incrX][0] == float(0)):
        selectsampleddata.append(sampleddata[incrX])
sampleddata = numpy.array(selectsampleddata)
del selectsampleddata

if (sampleddata.shape[0]) > 2:
    x = numpy.arange(sampleddata[0][15],sampleddata[-1][15],1) 
    y = numpy.array([0] * len(x))
    for incrX in range(len(sampleddata)):
        index_min = numpy.argmin(abs(x-(sampleddata[incrX][15])))
        y[index_min] = sampleddata[incrX][15]
    del index_min, incrX
    x = x * (1/ 250.0)
    plt.plot(x,y)
    print('The recording had a total of %d dropped samples (%0.1f%%).' %(len(y)-numpy.count_nonzero(y), ((len(y)-numpy.count_nonzero(y))/len(y))*100))