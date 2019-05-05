"""
Script:Bp_poseManager

Created For Maya:versions 2013 and above
Copyright (c) 2015 Prethish Bhasuran.
All rights reserved.

Redistribution and use in source and binary forms are permitted
provided that the above copyright notice and this paragraph are
duplicated in all such forms and that any documentation,
advertising materials, and other materials related to such
distribution and use acknowledge that the script was developed
by Prethish Bhasuran.
THIS CODE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

Description: PoseManger using json

The script creates and saves animatable  attributes of selected objects in json format.
to save a pose,the objects must be selected,otherwise it will not work.
To make it easier save selected object names, it is recommended to create a list in the begining

List of data created by the script:-----
folder:[projectName]/scripts/poses
files:[projectName]/scripts/poses/poses_list.json--this is created so that the pose can be checked
to see if its already present or not.
files:[projectName]/scripts/poses/[poseName].json--json file with animatable attributes
files:[projectName]/scripts/poses/[poseName].png--screenShot of pose

Maya SetUp instructions
1.Save the script in the default paths which are different depending on your OS:
Windows: <drive>:\Documents and Settings\<username>\My Documents\maya\<Version>\scripts
Mac OS X: ~/Library/Preferences/Autodesk/maya/<version>/scripts
Linux: ~/maya/<version>/scripts
2.Type the following commands to run the script
import Bp_poseManager
Bp_poseManager.showUI()
"""
from pymel.core import *
import json
import os
from pymel.core.general import select, setAttr


def Bp_savePose(poseName):
    """pose saver,returns true if successful

    Args:
        poseName ([type]): [description]

    Returns:
        bool.
    """
    # get all the selected objects
    selectedObjs = selected()
    if len(selectedObjs) == 0:
        print("No objects selected for saving pose:"+str(poseName))
        return False
    # checks to see if the pose has already been saved in the list of poses,if not exit
    if Bp_isPoseExisting(poseName):
        return False
    # get the path to save the file in scripts/poses directory
    path = (os.getcwd()+"/poses/").replace('\\', "/")
    # if not present create the directory
    if not os.path.isdir(path):
        os.mkdir(path)
    # setting the filename
    fileName = poseName+".json"
    # if file is existing delete it,essentially overwriting the old pose.
    if(os.path.isfile(path+fileName)):
            os.remove(path+fileName)
    print("setting pose for"+str(selectedObjs))
    # the dictionary to be written out
    animData = {}
    for obj in selectedObjs:
        # get the object name
        oName = obj.name()
        # get its keyable attributes that is unlocked
        animAttrs = obj.listAttr(k=True, u=True, c=True)
        # create an empty dictionary for the attributes
        attrData = {}
        for attr in animAttrs:
            # store in existing key or create a new one
            attrData.setdefault(str(attr), attr.get())
        # add to anim data
        animData.setdefault(oName, attrData)
    # write the data out
    outFile = open((path+fileName), 'w')
    outFile.write(json.dumps(animData))
    outFile.close()
    return True

  # load the desired pose,returns true if successful


def Bp_loadPose(poseName):
    if Bp_isPoseExisting(poseName):
        return False
    # get the path to get the file
    path = (os.getcwd()+"/poses/").replace('\\', "/")
    # get the pose name
    fileName = poseName+".json"
    # if file present read its data
    if(os.path.isfile(path+fileName)):
        inFile = open((path+fileName), 'r')
        jsonData = json.loads(inFile.readline())
        inFile.close()
    # parsing the data and setting the attributes
    for object in jsonData.keys():
        animData = jsonData[object]
        for attr in animData.keys():
            setAttr(attr, animData[attr])
    return True

 # loads the poselist and returns it as a list
def Bp_getPoseList(fileName="poses_list.json"):
    _path = os.path.join(
        os.getcwd(),
        "poses",
        fileName
    )

    # read the stored json list file
    if os.path.isfile(_path):
        with open((_path), 'r') as f:
            listData = json.loads(f.readline())
    else:
        listData = []
    return listData

# write out the list in json format
def Bp_setPoseList(listData):
    path = (os.getcwd()+"/poses/").replace('\\', "/")
    if not os.path.isdir(path):
        os.mkdir(path)
    fileName = "poses_list.json"
    # since it is write mode,it will overwrite previous data
    outFile = open((path+fileName), 'w')
    outFile.write(json.dumps(listData))
    outFile.close()

# returns True if pose present in list
def Bp_isPoseExisting(poseName):
    listData = Bp_getPoseList()
    if poseName in listData:
        return True
    else:
        print("Pose NOT in list:"+str(poseName))
        return False

# deletes a saved pose,it removes the posename from the list and
# deletes the json and png file
def Bp_removePose(poseName):
    path = (os.getcwd()+"/poses/").replace('\\', "/")
    listData = Bp_getPoseList()
    if poseName in listData:
        listData.remove(poseName)
        Bp_setPoseList(listData)
        os.remove(path+"/"+poseName+".json")
        os.remove(path+"/"+poseName+".png")
        return True
    else:
        return False

# add a new posename to lisr and save it
def Bp_addPoseToList(poseName):
    listData = Bp_getPoseList()
    if poseName not in listData:
        listData.append(poseName)
        Bp_setPoseList(listData)
    else:
        print("pose already present!!\n")

# hack to get the snapshot using the maya default hardware renderer
def Bp_createSnapShot(poseName, imageW, imageH):
  # set the presp viewport
  # turn off nurbs,ie controls
    windows.modelEditor('modelPanel4', e=True, nurbsCurves=False)
    # turn off the grid
    windows.modelEditor('modelPanel4', e=True, grid=False)
    # clear selection
    select(cl=True)
    # setting ouput png format
    imgFormat = getAttr("defaultRenderGlobals.imageFormat")
    setAttr("defaultRenderGlobals.imageFormat", 32)
    path = (os.getcwd()+"/poses/").replace('\\', "/")
    # playblast a single frame
    animation.playblast(frame=1, format="image", cf=(path+poseName+".png"), v=0,w=imageW,h=imageH,p=100)
    # reset the previous changes
    setAttr("defaultRenderGlobals.imageFormat", imgFormat)
    windows.modelEditor('modelPanel4', e=True, nurbsCurves=True)
    windows.modelEditor('modelPanel4', e=True, grid=True)


# get current project script path
def Bp_getScriptPath():
    scriptsFolder = workspace("scripts", q=True, fre=True)
    path = workspace(expandName=scriptsFolder)
    print("script path is"+str(path))
    if not os.path.isdir(path):
        os.mkdir(path)
    return path

# dynamically adds the icontext button to the UI
def Bp_populateUI():
    if rowColumnLayout('Bp_PS_poseLayout', exists=True):
        deleteUI('Bp_PS_poseLayout', lay=True)
    rowColumnLayout('Bp_PS_poseLayout', nc=4, p='Bp_PS_parentLayout')
    listData = Bp_getPoseList()
    path = (os.getcwd()+"/poses/").replace('\\', "/")
    for poseN in listData:
        cmd = "iconTextButton -p \"Bp_PS_poseLayout\" -style \"iconAndTextCentered\" "\
              "-image1 \"{0}{1}.png\" -label {1}  -c "\
              "\"python(\\\"Bp_poseManager.Bp_loadPose(\\\\\\\"{1}\\\\\\\")\\\")\";".format(
          path, poseN)
        language.evalEcho(cmd)
# function to read the selected set and its subsets recursively


def Bp_getAllSets(parentSet):
  # creating a list to store all the setnames
  allSets = [parentSet]
  # using recursion to get the data
  for s in allSets:
    subSets = listConnections(
        s, source=True, destination=False, type='objectSet')
    if subSets is not None:
      for ss in subSets:
        allSets.append(ss)
  return allSets


# gets all sets in the outliner
def Bp_getAllSceneSets():
    myOutliner = "outlinerPanel1"  # Name of the default Outliner
    setFilter = outlinerEditor(myOutliner, query=True, setFilter=True)
    outlinerSets = lsThroughFilter(setFilter, nodeArray=True)
    if "defaultLightSet" in outlinerSets:
        outlinerSets.remove("defaultLightSet")
    if "defaultObjectSet" in outlinerSets:
        outlinerSets.remove("defaultObjectSet")
    return outlinerSets


def Bp_populateOptionMenu():
    # delete existing menu if present
    existingMenuItems = optionMenu("Bp_PS_menu", q=True, ill=True)
    if len(existingMenuItems) != 0:
        for item in existingMenuItems:
            deleteUI(item, menuItem=True)
    # populating a new list
    menuData = Bp_getAllSceneSets()
    if len(menuData) != 0:
        for m in menuData:
            menuItem(p="Bp_PS_menu", l=m)
    else:
        menuItem(p="Bp_PS_menu", l="createNew")


def Bp_PS_UI_execute(operation):
    poseName = textFieldButtonGrp('pose_txt', q=True, tx=True)
    setName = optionMenu('Bp_PS_menu', q=True, v=True)
    if(operation == 'savePose'):
        if(poseName == "Type name of pose.."):
            warning("Please enter name of pose!!\n")
            return False
        select(cl=True)
        if  setName == "defaultLightSet"  or setName =="defaultObjectSet" :
            warning("nothing is selected,Please create sets to select the controls\n")
            return False
        else:
            select(setName, r=True)
        selectN = selected()
        if len(selectN) == 0:
            warning("nothing is there is in this Set!!-->"+setName)
            return False
        else:
            print('Creating pose!!-->'+poseName)
            Bp_addPoseToList(poseName)
            Bp_savePose(poseName)
            Bp_createSnapShot(poseName, 64, 64)
            Bp_populateUI()
    elif(operation == "removePose"):
        if(poseName == "Type name of pose.."):
            warning("Please enter name of pose!!\n")
            return False
        Bp_removePose(poseName)
        Bp_populateUI()
    elif(operation == "selectSet"):
        select(setName, r=True)
    elif(operation == "createSet"):
        mel.eval("CreateSetOptions")
    elif(operation == "refreshSet"):
        Bp_populateOptionMenu()
    else:
        print("invalid Option for Bp_PS_UI")


def showUI():
    """[summary]
    """
    # change the script path to the existing project scripts folder
    path = Bp_getScriptPath()
    os.chdir(path)
    # deleting existing window
    if window('Bp_PS_window', exists=True):
        deleteUI('Bp_PS_window', window=True)
    # deleting preferences
    if windowPref('Bp_PS_window', exists=True):
        windowPref('Bp_PS_window', remove=True)
    # display window
    window('Bp_PS_window', rtf=True, s=False)
    columnLayout('Bp_PS_parentLayout')
    textFieldGrp(l="Current Save Path:", tx=path, en=False)
    rowLayout(nc=4)
    optionMenu('Bp_PS_menu')
    Bp_populateOptionMenu()
    button(l="select set", c="Bp_poseManager.Bp_PS_UI_execute(\"selectSet\")")
    button(l="create set", c="Bp_poseManager.Bp_PS_UI_execute(\"createSet\")")
    button(l="refresh List", c="Bp_poseManager.Bp_PS_UI_execute(\"refreshSet\")")
    setParent('..')
    textFieldButtonGrp('pose_txt', tx='Type name of pose..', bl='Save', bc="Bp_poseManager.Bp_PS_UI_execute(\"savePose\")")
    button(l='removePose', c="Bp_poseManager.Bp_PS_UI_execute(\"removePose\")")
    rowColumnLayout('Bp_PS_poseLayout', nc=4, p='Bp_PS_parentLayout')
    Bp_populateUI()
    showWindow('Bp_PS_window')


# the script has been run in the script editor instead of laoding it as a module
if __name__ == "__main__":
    warning("This script is meant to loaded using the import command!please check setup instructions!\n")
