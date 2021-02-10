# tkSpeedometer
Tool to measure speed in km/h or miles/h in a maya scene
hierarchy doesnt matter
Generates HUDs
   Usage:
   ---------
   1.  Select the objects, you want the speed get measured.  
   2.  "Create Speedometer On Selected Objects" sets up the scene. 
   3.  Choose "Position" to define where the HUD should be shown.
        ---------------------------------------------
        Depending on other HUDs and the viewport size, 
        the HUD may not be seen! 
        ---------------------------------------------
   4.  Scene Scale to adjust the overall scale, eg 1:10.
   5.  Chosse Decimals 0-2 to display decimal count in the HUD.
        A HUD should appear in your viewport.
   6.  "Clear HUD" removes the HUD.
   ---------
   The information (sceneScale, decimals, objects) is stored in the group "speed_lc_grp".
   To remove all: Clear the HUD first, then delete the "speed_lc_grp".
