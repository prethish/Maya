import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

#for error messages
import sys
import math
##mel commandName
kCmdName="bpCreateHelix"
#custom command flags
#must define both the long name and short name
kPitchFlag="-p"
kPitchLongFlag="-pitch"
kRadiusFlag="-r"
kRadiusLongFlag="-radius"
##class which runs the cmd
class bpCreateHelixCmd(OpenMayaMPx.MPxCommand):
    #constructor
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        #instance variables
        self.fDagPath=OpenMaya.MDagPath()
        self.fCVs=OpenMaya.MPointArray()
        #default values for radius and pitch
        self.radius=4.0
        self.pitch=0.5        
    
    def redoIt(self):
        curveFn=OpenMaya.MFnNurbsCurve(self.fDagPath)
        
        numCvs=curveFn.numCVs()
        curveFn.getCVs(self.fCVs)
        
        points=OpenMaya.MPointArray(self.fCVs)
        
        for i in range(0,numCvs):
            points.set(i,self.radius*math.cos(i),
                                self.pitch*i,
                                self.radius*math.sin(i))
        
        curveFn.setCVs(points)
        curveFn.updateCurve()
        
    
    def undoIt(self):
        curveFn=OpenMaya.MFnNurbsCurve(self.fDagPath)       
        curveFn.setCVs(self.fCVs)
        curveFn.updateCurve()
        self.fCVs.clear()
         
    
    #on initializtion this the procedure that is run.
    #to avoid code duplication the redoit procedure is called
    def doIt(self,args):
        #get the flags passed
        argData=OpenMaya.MArgDatabase(self.syntax(),args)
        if argData.isFlagSet(kPitchFlag):
            self.pitch=argData.flagArgumentDouble(kPitchFlag,0)
        if argData.isFlagSet(kRadiusFlag):
            self.radius=argData.flagArgumentDouble(kRadiusFlag,0)
        #get the selection list
        sel=OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(sel)
        #get nurbs curves objects using filter
        nurbsList=OpenMaya.MItSelectionList(sel,OpenMaya.MFn.kNurbsCurve)
        if nurbsList.isDone():
            print ("no crv selected !!")
            return
        
        self.fDagPath
        nurbsList.getDagPath(self.fDagPath)
        self.redoIt()
        
    #the commands are undoable
    def isUndoable(self):
        return True
    #destructor
    def __del__(self):
        self.fCVs.clear()
##end class definition

def cmdCreator():
    return OpenMayaMPx.asMPxPtr(bpCreateHelixCmd()) 

def syntaxCreator():
    #create the syntax obj
    syntax=OpenMaya.MSyntax()
    #add the defined flags
    syntax.addFlag(kPitchFlag,kPitchLongFlag,OpenMaya.MSyntax.kDouble)
    syntax.addFlag(kRadiusFlag,kRadiusLongFlag,OpenMaya.MSyntax.kDouble)
    return syntax

def initializePlugin(mobject):
    cmdPlugin=OpenMayaMPx.MFnPlugin(mobject,"2014Message")
    try:
        cmdPlugin.registerCommand(kCmdName,cmdCreator,syntaxCreator)
        print("registeredCmd!!\n")
    except:
        sys.stderr.write("Error registering cmd->"+kCmdName)
        raise

def uninitializePlugin(mobject):
    cmdPlugin=OpenMayaMPx.MFnPlugin(mobject)
    try:
        cmdPlugin.deregisterCommand(kCmdName)
    except:
        sys.stderr.write("Error deregistering cmd->"+kCmdName)
        raise

 
