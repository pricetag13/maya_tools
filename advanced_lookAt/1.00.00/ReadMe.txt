USAGE:

1) Copy the entire "advanced_lookAt" folder anywhere on your local machine.
For example, C:\advanced_lookAt

2) In the python script below, modify the "lookAt_root" path.  It should point to your local folder.
For example, lookAt_root = r"C:\advanced_lookAt\1.00.00"

3) run the python script below in a python tab in your Maya script editor.




# /////////// Launcher for Advanced Lookat UI ////////////////////

import sys

lookAt_root = r"**your_path_here**\1.00.00"
sys.path.append(lookAt_root)

import gui.main as main

reload(main)
main.show()