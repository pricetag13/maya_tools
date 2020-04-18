import maya.cmds as cmds

class RibbonzClass(object):
    """
    This is my tool to automate the process of creating ribbons
    """
    def __init__(self):
        self.edge_a = ['pCylinder1.e[89]',
                       'pCylinder1.e[97]',
                       'pCylinder1.e[105]',
                       'pCylinder1.e[113]',
                       'pCylinder1.e[121]',
                       'pCylinder1.e[129]',
                       'pCylinder1.e[137]',
                       'pCylinder1.e[145]',
                       'pCylinder1.e[153]',
                       'pCylinder1.e[161]']

        self.edge_b = ['pCylinder1.e[93]',
                       'pCylinder1.e[101]',
                       'pCylinder1.e[109]',
                       'pCylinder1.e[117]',
                       'pCylinder1.e[125]',
                       'pCylinder1.e[133]',
                       'pCylinder1.e[141]',
                       'pCylinder1.e[149]',
                       'pCylinder1.e[157]',
                       'pCylinder1.e[165]']

        self.curve_a = ''
        self.curve_b = ''
        self.ribbon = ''
        self.ribbon_knots = []
        self.ribbon_column_a = []
        self.ribbon_column_b = []


    def edge_to_curve(self):
        cmds.select(self.edge_a)
        self.curve_a = cmds.polyToCurve(name='curve_a', degree=2)
        cmds.select(self.edge_b)
        self.curve_b = cmds.polyToCurve(name='curve_b', degree=2)
        self.ribbon = cmds.loft(self.curve_a, self.curve_b, name='ribbon', degree=1, constructionHistory=False)

    def get_knots(self):
        cmds.nurbsSelect(self.ribbon)
        all_nurb_cvs = cmds.ls(selection=True)
        for cv in all_nurb_cvs:
            cv_position = cmds.pointPosition(cv)
            cmds.joint
            print 'CV:', cv_position



    def create_joints(self):
        cmds.joint()

    def run_ribbonz(self):
        self.edge_to_curve()
        self.get_knots()