#Import Desired Libraries Here
import maya.OpenMaya as om
import maya.OpenMayaMPx as omMPx

import sys,math

#Set name and id
nodeName = "bpTextConvert"
nodeId = om.MTypeId(0x10123)#type a unique number here

#  Node  class- uses MPxNode as a base
class stringNode(omMPx.MPxNode):
    # input and output variables
    aInput= om.MObject()
    aSOutput= om.MObject()
    def __init__(self):
        omMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        #print("inCompute\n")
        if (plug == stringNode.aSOutput) :
            #get the input
            inputData = dataBlock.inputValue(stringNode.aInput)
            floatValue=inputData.asFloat()
            stringS=str(floatValue)
            #print(stringS+"\n")
            stringHandle=dataBlock.outputValue(stringNode.aSOutput)
            stringHandle.setString(stringS)
            #set the dirty flag
            dataBlock.setClean(plug)

def nodeCreator():
    return omMPx.asMPxPtr( stringNode() )

def nodeInit():
    #input
    numAttr = om.MFnNumericAttribute()
    stringNode.aInput = numAttr.create("input","in",om.MFnNumericData.kFloat,0.0)
    numAttr.setStorable(1)
    
   #output
    stringAttr = om.MFnTypedAttribute()
    stringNode.aSOutput = stringAttr.create("stringOutput","so",om.MFnData.kString)
    stringAttr.setStorable(0)
    stringAttr.setWritable(0)
    
# add the attributes
    stringNode.addAttribute(stringNode.aInput)
    stringNode.addAttribute(stringNode.aSOutput)
    #set the attribute affects 
    stringNode.attributeAffects(stringNode.aInput, stringNode.aSOutput)

       
# This is used for loading plugins
def initializePlugin(mobject):
    mplugin = omMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeId, nodeCreator, nodeInit)
    except:
        sys.stderr.write("Error loading")
        raise

# This is used for removing plugins
def uninitializePlugin(mobject):
    mplugin = omMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( nodeId )
    except:
        sys.stderr.write("Error removing")
        raise
