#Import Desired Libraries Here
import maya.OpenMaya as om
import maya.OpenMayaMPx as omMPx

import sys,math
#import DualQuaternion as dq

#Set name and id
nodeName = "matrixToDualQuaternion"
nodeId = om.MTypeId(0x10113)#type a unique number here

#  Node  class- uses MPxNode as a base
class matrixToDQNode(omMPx.MPxNode):
    # input and output variables
    matInput= om.MObject()
    #normalizeFlag= om.MObject()
    
    dqCompOutput= om.MObject()
    dqXOutt= om.MObject()
    dqYOut= om.MObject()
    dqZout= om.MObject()
    dqWout= om.MObject()
    def __init__(self):
        #explicitly define the init
        omMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if (plug == matrixToDQNode.dqOutput) :
            #get the input
            inputMatData = dataBlock.inputValue(matrixToDQNode.matInput)

            #set the dirty flag
            dataBlock.setClean(plug)
        else:
            return om.MStatus.kUnknownParameter
        return om.MStatus.kSuccess


def nodeCreator():
    # Create XX Node
    return omMPx.asMPxPtr( matrixToDQNode() )

def nodeInit():
    # Init me
    #attributes
    #set the type of attributes
    #input
    numAttr = om.MFnNumericAttribute()
    matAttr =om.MFnMatrixAttribute()
    compoundAttr=om.MFnCompoundAttribute()
    
    matrixToDQNode.matInput = matAttr.create("inMatrix","inMat",om.MFnMatrixAttribute.kDouble)
    matAttr.setKeyable(1)
    matAttr.setStorable(1)
    matAttr.setReadable(1)
    matAttr.setWritable(1)
        
    #output
    matrixToDQNode.dqXOut = numAttr.create("outputX","ox",om.MFnNumericData.kFloat,0.0)
    numAttr.setStorable(1)
    numAttr.setWritable(0)
    matrixToDQNode.dqYOut = numAttr.create("outputY","oy",om.MFnNumericData.kFloat,0.0)
    numAttr.setStorable(1)
    numAttr.setWritable(0)
    matrixToDQNode.dqZOut = numAttr.create("outputZ","oz",om.MFnNumericData.kFloat,0.0)
    numAttr.setStorable(1)
    numAttr.setWritable(0)
    matrixToDQNode.dqWOut = numAttr.create("outputW","ow",om.MFnNumericData.kFloat,0.0)
    numAttr.setStorable(1)
    numAttr.setWritable(0)
    
    matrixToDQNode.dqWOutt = compoundAttr.create("outputDQ","odq")
    compoundAttr.addChild(matrixToDQNode.dqXOut)
    compoundAttr.addChild(matrixToDQNode.dqYOut)
    compoundAttr.addChild(matrixToDQNode.dqZOut)
    compoundAttr.addChild(matrixToDQNode.dqWOut)

    
# add the attributes
    matrixToDQNode.addAttribute(matrixToDQNode.matInput)
    matrixToDQNode.addAttribute(matrixToDQNode.dqCompOutput)

    #set the attribute affects 
    matrixToDQNode.attributeAffects(matrixToDQNode.matInput, matrixToDQNode.dqCompOutput)

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
