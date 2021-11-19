import advanced_lookat_tabs


def show():
    advanced_lookat_tabs.delete_maya_tool('lookat_main')
    dialogue = advanced_lookat_tabs.AdvancedLookAtMain()
    dialogue.show()

