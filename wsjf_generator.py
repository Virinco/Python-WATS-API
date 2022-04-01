# -*- coding: utf-8 -*-
"""
Author: Jesper Johnsen - jsj@sky-watch.com
Created on Thu Mar 18 08:35:49 2021
Class to generate WATS JSON Format reports and publish the report
"""
import json
from datetime import datetime
from os import getlogin
import requests
import uuid

class wsjf_generator():
    sWatsToken="" # "Your Token here"
    sWatsURL ="https://example.wats.com/api/report/wsjf" # Your URL here, remember to include the rest api endpoint
    wsjf_dict = {}
    counterID = 0
    TestSequencerName="wsjf_generator.py"
    TestSequencerVersion = "0.1"
    
    #def __init__(self):
        #init code
	
    #machineName is Station Name
    def setHeader(self, mode="oper", pn = "debug", sn = "debug", rev = "NA", machineName="ManTest", user= getlogin(), uniqueID=""):
        if(uniqueID==""):
            uniqueID = str(uuid.uuid4())
        
        if(mode=="oper"):
            #self data['key'] = 'value'    
            dictHeader =   {
                "type": "T",
                "id": uniqueID,
                "pn": pn,
                "sn": sn,
                "rev": rev,
                "processCode": 50,
                "processName": "PCBA test",
                "result": "P",
                "machineName": machineName, 
                "location": "Production",
                "purpose": "Production Test",
                "start": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")+"+%d:00"%(int(datetime.now().strftime("%H"))-int(datetime.utcnow().strftime("%H"))),
                "startUTC": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")+".Z",
                "root": "",
                "uut":{
                    "user": user,
                    "comment": "No Comments added"
                    }
                }
            self.wsjf_dict = dictHeader
            
    def addMain(self, TestSequencerName="wsjf_generator.py", TestSequencerVersion = "0.1"):
        dictMain = {
            "id": 0,
            "group": "M",
            "stepType": "SequenceCall",
            "name": "MainSequence Callback",
            "status": "P",
            "totTime": 0.0,
            "causedUUTFailure": False,
            "reportText": "Here is a report text",
            "steps": [
              ],
              "seqCall": {
                  "path": TestSequencerName,
                  "name": "Numeric tests",
                  "version": TestSequencerVersion
                  }  
                
                  
              
        }
        self.counterID= self.counterID+1
        self.Dict_setValue(self.wsjf_dict, ["root"], dictMain)
        return ["root", "steps"]
    
    def addTestGroup(self, name, path , TestSequencerName="wsjf_generator.py", TestSequencerVersion = "0.1"):
        dictMain = {
                "id": self.counterID,
                "group": "M",
                "stepType": "SequenceCall",
                "name": name,
                "status": "P",
                "totTime": 0.0,
                "causedUUTFailure": False,
                "steps": [
                    ],
                "seqCall": {
                  "path": TestSequencerName,
                  "name": "Numeric tests",
                  "version": TestSequencerVersion
                  }  
                }
        
        self.Dict_addList(self.wsjf_dict, path, dictMain)
        newPath = path[:]
        newPath.append(["id", self.counterID])
        newPath.append("steps")
        self.counterID= self.counterID+1
        return  newPath

    def initMultipleNumericTest(self, path, testname="MultipleNumericTest", steptime=0.0):
        dictSingleTest = {
                "id": self.counterID,
                "group": "M",
                "stepType": "ET_MNLT",
                "name": testname,
                "status": "P",
                "totTime": steptime,
                "causedUUTFailure": False,
                "numericMeas": [
                    ],
                }
        
        self.Dict_addList(self.wsjf_dict, path, dictSingleTest)
        TestStepPath = path[:]
        TestStepPath.append(["id", self.counterID])
        TestStepPath.append("numericMeas")
        
        self.counterID= self.counterID+1
        return TestStepPath
    
    def addNumericTest(self, path, value, unit="V", highLimit="", lowLimit="", testname="SingleTest", steptime=0.0):
          [highLimit, lowLimit, compOp, status, causedUUTFailure] = self.getSimpleLimits(path, value, highLimit, lowLimit)
          dictSingleTest = {
                    "compOp": compOp,
                    "name": testname,
                    "status": status,
                    "unit": unit,
                    "value": value,
                    "highLimit": highLimit,
                    "lowLimit": lowLimit
                    }
          self.counterID= self.counterID+1
          self.Dict_addList(self.wsjf_dict, path, dictSingleTest)
    
    def addSingleTest(self, path, value, unit="V", highLimit="", lowLimit="", testname="SingleTest", steptime=0.0):
        [highLimit, lowLimit, compOp, status, causedUUTFailure] = self.getSimpleLimits(path, value, highLimit, lowLimit)
        
        dictSingleTest = {
                "id": self.counterID,
                "group": "M",
                "stepType": "ET_NLT",
                "name": testname,
                "status": status,
                "totTime": steptime,
                "causedUUTFailure": causedUUTFailure,
                "numericMeas": [
                  {
                    "compOp": compOp,
                    "name": None,
                    "status": status,
                    "unit": unit,
                    "value": value,
                    "highLimit": highLimit,
                    "lowLimit": lowLimit
                  }
                ]
              }
        
        self.counterID= self.counterID+1
        self.Dict_addList(self.wsjf_dict, path, dictSingleTest)
    
    def initChart(self, path, testname="Chart", chartTitel="ChartName", chartType="Line", xLabel="X-axis", xUnit="[]",yLabel="Y-axis", yUnit="[]", steptime=0.0):
        status = "P"
        dictSingleTest = {
                "id": self.counterID,
                "group": "M",
                "stepType": "WATS_XYGMNLT",
                "name": testname,
                "status": status,
                "totTime": steptime,
                "causedUUTFailure": False,
                 "chart": {
                      "chartType": chartType,
                      "label": chartTitel,
                      "xLabel": xLabel,
                      "xUnit": xUnit,
                      "yLabel": yLabel,
                      "yUnit": yUnit,
                      "series": [],
                      }
                }
        
        self.Dict_addList(self.wsjf_dict, path, dictSingleTest)
        TestStepPath = path[:]
        TestStepPath.append(["id", self.counterID])
        TestStepPath.append("chart")
        TestStepPath.append("series")
        
        self.counterID= self.counterID+1
        return TestStepPath
        
    def addChart(self, path, yData, xData, legend="myLegend", yLowLimit = "", xLowLimit="", yHighLimit="", xHighLimit="", steptime=0.0 ):
        def addChartSeries(yData, xData, legend="myLegend"):
             dictSeries = {
                 "dataType": "XYG",
                 "name": legend,
                 "xdata": (';'.join(map(str, xData))),
                 "ydata": (';'.join(map(str, yData)))
             }
             return dictSeries
        dictChart = {
             "dataType": "XYG",
             "name": legend,
             "xdata": (';'.join(map(str, xData))),
             "ydata": (';'.join(map(str, yData)))
             }
        self.Dict_addList(self.wsjf_dict, path, dictChart)    
        
        if(type(xLowLimit)==list and type(yLowLimit)==list and len(xLowLimit)==len(yLowLimit)):
            self.Dict_addList(self.wsjf_dict, path,addChartSeries(yLowLimit, xLowLimit, "Low Limit")) 
            for yVal, xVal in zip(yData, xData):
                if(self.getVectorStatus(yVal, xVal, yLowLimit, xLowLimit, limit="Low")=="F"):
                    self.updateStatusToFail(self.wsjf_dict, path) 
                    break
        if(type(xHighLimit)==list and type(yHighLimit)==list and len(xHighLimit)==len(yHighLimit)):
            self.Dict_addList(self.wsjf_dict, path,addChartSeries(yHighLimit, xHighLimit, "High Limit"))
            for yVal, xVal in zip(yData, xData):
                if(self.getVectorStatus(yVal, xVal, yHighLimit, xHighLimit, limit="High")=="F"):
                    self.updateStatusToFail(self.wsjf_dict, path) 
                    break
        
    # WSJF support functions
    def getSimpleLimits(self,  DictPath, value, highLimit = "", lowLimit = "",):
        if highLimit == "" and lowLimit == "":
            compOp = "LOG" #always pass and no limits
            status = "P"
        if highLimit == "" and lowLimit != "":
            compOp = "GE" #always pass and no limits
            if value >= lowLimit:
                status = "P"
            else: 
                status = "F"
        if highLimit != "" and lowLimit != "":
            compOp = "GELE" #always pass and no limits
            if value >= lowLimit and value <= highLimit:
                status = "P"
            else: 
                status = "F"
        if highLimit != "" and lowLimit == "":
            compOp = "LE" #always pass and no limits
            if value <= highLimit:
                status = "P"
            else: 
                status = "F"
            #fixes Bug in API, <= LE takes a low limit and not a highlimit as expected
            lowLimit = highLimit
            highLimit = None
        causedUUTFailure = True
        if status == "P":
            causedUUTFailure = False
        if highLimit == "":
            highLimit = None
        if lowLimit == "":
            lowLimit = None
        if (status == "F"):
            self.updateStatusToFail(self.wsjf_dict, DictPath)    
        
        return [highLimit, lowLimit, compOp, status, causedUUTFailure]
    
    def getVectorStatus(self, yVal,xVal,yLim,xLim, limit="High"):
        #check if x is in xlim
        if(min(xLim, key=lambda x:abs(x-xVal))==xVal):
            index = xLim.index(xVal)
            #x value found, is the y data passing?
            if(limit=="High"):
                if(yVal<=yLim[index]):
                    return "P"
                else:
                    return "F"
            else:
                if(yVal>=yLim[index]):
                    return "P"
                else:
                    return "F"
        #check if xVal is outside the limit span
        if(xVal>max(xLim) or xVal<min(xLim)):
            return "P"
        #xVal is not in the list and is not outside the specified limits
        #Extrapolate nearst values
        u_xLim = min([ i for i in xLim if i >= xVal], key=lambda x:abs(x-xVal))
        u_yLim = yLim[xLim.index(u_xLim)]
        l_xLim = min([ i for i in xLim if i < xVal], key=lambda x:abs(x-xVal))
        l_yLim = yLim[xLim.index(l_xLim)]
        alpha = float(l_yLim-u_yLim)/float(l_xLim-u_xLim)
        beta = l_yLim-alpha*l_xLim
        if(limit=="High"):    
            if(yVal<=(alpha*xVal+beta)):
                return "P"
            else:
                return "F"
        else:
            if(yVal>=(alpha*xVal+beta)):
                return "P"
            else:
                return "F"
        
        
         
    
    def updateStatusToFail(self, Dict, DictPath):
        Dict["result"] = "F"
        for key in DictPath[:]:
            try:
                Dict["status"] = "F"
            except:
                None
                
            if(type(Dict)==list):
                #Dict is a list of dicts
                #find the right dict in the list
                for dict_ in filter(lambda x: x[key[0]] == key[1], Dict):
                    self.updateStatusToFail(dict_, DictPath[DictPath.index(key)+1:])
                    return
            else:
                Dict = Dict.setdefault(key, {})
    def setComment(self, text):
        self.Dict_setValue(self.wsjf_dict, ["uut", "comment"], text)    
                
    def pushReport(self, sWatsURL="", sWatsToken="", backupFilePath="", printLog = True):
        if(sWatsToken != ""):
            self.sWatsToken = sWatsToken #if you use another Token than the default
        if(sWatsURL != ""):
            self.sWatsURL = sWatsURL #if you use another URL than the default
            
        if(self.sWatsURL != "" and self.sWatsToken != ""):
            json_dump = json.dumps(self.wsjf_dict)
            try:
                response = requests.post(self.sWatsURL, json_dump, headers={"Authorization": 'Basic %s'%self.sWatsToken})
                if(printLog):
                    print("Status code: ", response.status_code)
            except requests.exceptions.RequestException as e:
                if(backupFilePath == ""):
                    backupFilePath = self.wsjf_dict["id"] + ".json"
                with open(backupFilePath, "w") as file:
                    print(json_dump, file=file)
                raise SystemExit(e)
            
        
    
    # Dict Support functions.
    # WSJF report is generated from a Dict object
    # and a Dict Object can be created from a JSON file
    def Dict_lookup(self, Dict, DictPath):
        tempDict = Dict
        for key in DictPath:
            if(type(Dict)==list):
                for dict_ in filter(lambda x: x[key[0]] == key[1], tempDict):
                    return self.Dict_lookup(dict_, DictPath[DictPath.index(key)+1:])
            else:        
                tempDict = tempDict[key]
        return tempDict
    def Dict_setValue(self, Dict, DictPath, value):
        for key in DictPath[:-1]:
            if(type(Dict)==list):
                #Dict is a list of dicts
                #find the right dict in the list
                for dict_ in filter(lambda x: x[key[0]] == key[1], Dict):
                    self.Dict_setValue(dict_, DictPath[DictPath.index(key)+1:], value)
                    return
            else:
                Dict = Dict.setdefault(key, {})    
        Dict[DictPath[-1]] = value
    def Dict_addList(self, Dict, DictPath, value):
        for key in DictPath:
            if(type(Dict)==list):
                #Dict is a list of dicts
                #find the right dict in the list
                for dict_ in filter(lambda x: x[key[0]] == key[1], Dict):
                    self.Dict_addList(dict_, DictPath[DictPath.index(key)+1:], value)
                    return
            else:
                Dict = Dict.setdefault(key, {})    
        Dict.append( value )
        
    def Dict_addKey(self, Dict, DictPath, newkey, value=""):
        for key in DictPath:
            if(type(Dict)==list):
                #Dict is a list of dicts
                #find the right dict in the list
                for dict_ in filter(lambda x: x[key[0]] == key[1], Dict):
                    self.Dict_addKey(dict_, DictPath[DictPath.index(key)+1:], newkey, value)
                    return
            else:
                Dict = Dict.setdefault(key, {})
        Dict[newkey] = value
    def Dict_delKey(self, Dict, DictPath):
        for key in DictPath[:-1]:
            if(type(Dict)==list):
                #Dict is a list of dicts
                #find the right dict in the list
                for dict_ in filter(lambda x: x[key[0]] == key[1], Dict):
                    self.Dict_delKey(dict_, DictPath[DictPath.index(key)+1:])
                    return
            else:
                Dict = Dict.setdefault(key, {})
        del Dict[DictPath[-1]]
        
    

def main(options=None):
    
    wsjf = wsjf_generator()
    # --- Example report generation usages ---
    #wsjf.setHeader(rev=3)
    #pathMain = wsjf.addMain()
    #pathBoot = wsjf.addTestGroup("Boot Test", pathMain)
    #wsjf.addSingleTest(pathBoot, value=12, testname="Test1")
    #wsjf.addSingleTest(pathBoot, value=15, testname="Test3", highLimit=20, lowLimit=10)
    #wsjf.addSingleTest(pathBoot, value=31, testname="Test4", lowLimit=30)
    #wsjf.addSingleTest(pathBoot, value=17, testname="Test5", highLimit=20)
    #pathSub = wsjf.addTestGroup("Subcircuit 1 Test", pathMain, TestSequencerName="TestSequencer.py", TestSequencerVersion = "0.5")
    #path_MNL1 = wsjf.initMultipleNumericTest(pathSub, testname="Test10")
    #wsjf.addNumericTest(path_MNL1, value=18, testname="Test6", lowLimit=10)
    #wsjf.addNumericTest(path_MNL1, value=18, testname="Test7", highLimit=20)
    #wsjf.addSingleTest(pathBoot, value=18, testname="Test8", lowLimit=12, highLimit=20)
    #wsjf.addNumericTest(path_MNL1, value=30, unit="mA", testname="Test9", lowLimit=10, highLimit=35)
    #wsjf.addNumericTest(path_MNL1, value=19, unit="mA", testname="Test10", lowLimit=18)
    #path_Chart2 = wsjf.initChart(pathSub,"chart","Super Cool Test")
    #wsjf.addChart(path_Chart2, [0,2,2.6, 1, 2], [6,7,8, 10, 11], "Fantastic Dataset 2", [0, 0], [5, 15], [2.6, 2.6, 2, 2], [2, 10, 10.01, 15])
    #wsjf.addChart(path_Chart2, [0,2,2.6, 1, 2], [5,6,7, 9, 10], "Fantastic Dataset 2", [0, 0], [5, 15], [2.6, 2.6, 2, 2], [2, 10, 10.01, 15])
    #path_Chart = wsjf.initChart(pathSub,"chart2","Super Cool Test2")
    #wsjf.addChart(path_Chart, [2.5,2.5,1.7, 1.7], [8,9.5, 10.5, 12], "Fantastic Dataset", [0, 0], [5, 15], [2.6, 2.6, 2, 2], [2, 10, 10.01, 15])
    #path_Chart2 = wsjf.initChart(pathSub,"chart3","Super Cool Test3 ")
    #wsjf.addChart(path_Chart2, [0,2,2.6, 2.29, 2.29, 1, 1], [6,7,8, 10, 10.7, 10.8,  12], "Fantastic Dataset 3", [0, 0], [5, 15], [2.6, 2.6, 2, 2], [2, 10, 11, 15])  
    #wsjf.setComment("Test generated to test Python API")
	
    wsjf.pushReport(sWatsURL="https://example.wats.com/api/report/wsjf", sWatsToken="Your Token") # one can set the token and Url in the class file, or by setting wsjf.sWatsToken and wsjf.sWatsURL   
	# if submit to server fails the wsjf was saved to a file
        
    print("Submitted Report")
    print(json.dumps(wsjf.wsjf_dict, indent=2))
    
    

if __name__ == '__main__':
    main()

