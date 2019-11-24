import maya.OpenMaya as om
import time

for each in cmds.shelfLayout("Custom", q=1, ca=1):
    print each
    if cmds.shelfButton(each, q=1,statusBarMessage=1)== "MayaPort":
        print "MayaPort"
       if cmds.shelfButton(each, q=1,i=1) == "activeDeselectedAnimLayer.png":
           new_image = "activeSelectedAnimLayer.png"
       else:
           new_image = "activeDeselectedAnimLayer.png"

       cmds.shelfButton(each, e=1,i=new_image)
       
def time_it(func):
    def wrapper(*args, **kwargs):
        start= time.time()
        result = func(*args, **kwargs)
        print(
            "Time Elapsed for %s is %s" % (
                func,
                time.time()-start
            )
        )
        return result
    return wrapper

def get_mobject(node):
    """Get the MObject of the given node.

    :param node: Node name
    :return: Node MObject
    """
    selection_list = om.MSelectionList()
    selection_list.add(node)
    mobject = om.MObject()
    selection_list.getDependNode(0, mobject)
    return mobject


def get_dag_path(node):
    """Get the MDagPath of the given node.

    :param node: Node name
    :return: Node MDagPath
    """
    selection_list = om.MSelectionList()
    selection_list.add(node)
    path = om.MDagPath()
    selection_list.getDagPath(0, path)
    return path

def get_mfn_mesh(node):
    return om.MFnMesh(get_dag_path(node))

@time_it
def brute_force_test(mesh_name):
    mfn_mesh = get_mfn_mesh(mesh_name)
    mesh_uv_sets = []
    mfn_mesh.getUVSetNames(mesh_uv_sets)
    uv_set_names = []
    uv_set_missing_face = {
        key:[] for key in mesh_uv_sets
    }
    for i in xrange(mfn_mesh.numPolygons()):
        mfn_mesh.getFaceUVSetNames(i, uv_set_names)
        difference = set(mesh_uv_sets).symmetric_difference(uv_set_names)
        if difference:
            print(i, difference)
        # clear the existing list
        del uv_set_names[:]

brute_force_test("pSphere1")