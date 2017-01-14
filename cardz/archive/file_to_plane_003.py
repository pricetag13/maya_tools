import maya.cmds as cmds

global_user_path = "stuff"


def my_path():

    path = "C:\working_projects\DreamEater\sourceimages\01_old_house_int_tex\card_clock.tif"
    print path


def create_shading_network():

        # create a shader
    shader = cmds.shadingNode("lambert", asShader=True, n=global_user_path + "L")
    # a file texture node
    file_node = cmds.shadingNode("file", asTexture=True, n=global_user_path + "F")
    # defines location where texture is
    my_file = ("sourceimages" + "/" + "01_old_house_int_tex" + "/" + "card_clock.tif")
    # a shading group
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
    cmds.setAttr('%s.fileTextureName' % file_node, my_file, type="string")
    # connect shader to sg surface shader
    cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)
    # connect file texture node to shader's color
    cmds.connectAttr('%s.outColor' % file_node, '%s.color' % shader)


def create_plane():

    # Gets the image dimensions and scales them down by 500 times
    x_source_width = cmds.getAttr("text_0"+".outSizeX")
    x_width = x_source_width/500
    y_source_height = cmds.getAttr("text_0"+".outSizeY")
    y_height = y_source_height/500

    # Creates the poly plane
    cmds.polyPlane(w=x_width, h=y_height, sx=1, sy=1, ax=[0, 0, 1], cuv=1, ch=0, n="my_fancy"+"_plane")


def assign_shader():
    cmds.sets(e=True, forceElement="set1")


def retrieve_user_path():
    # Query and print user supplied path
    global global_user_path
    global_user_path = cmds.textField("user_image_path", query=True, text=True)
    print global_user_path
    create_shading_network()


def build_gui():
    window_pos = [0, 0]  # default window position...

    # checks if window already exists, and if so deletes all the preferences and kills it
    if cmds.window("CardCreator", exists=True):
        window_pos = cmds.window("CardCreator", q=1, topLeftCorner=True)
        cmds.deleteUI("CardCreator")
        cmds.windowPref("CardCreator", removeAll=True)

    # here we are making new window, and giving preferences to it - assign result to window variable
    win_main = cmds.window("CardCreator", title="Price Card Creator", iconName='PriceCardCreator', sizeable=False,
                           width=800, height=150)

    # here u define ur window - layout buttons etc..
    cmds.frameLayout(label="Card Creator", borderStyle="in", collapsable=True, parent=win_main)

    cmds.rowColumnLayout(numberOfColumns=2)

    cmds.text(label="Image Path                                                                                      ")
    cmds.textField("user_image_path")
    cmds.textField("user_image")
    cmds.button("get_image_path", label="Create Card", command=lambda *args: retrieve_user_path())

    cmds.showWindow(win_main)
    cmds.window(win_main, e=1, topLeftCorner=window_pos)

# create_shading_network()
# create_plane()
# assign_shader()
build_gui()
