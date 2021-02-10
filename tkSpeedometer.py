'''
tkSpeedometer.1.3.py
Thomas Kutschera
feb 2021

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
		
'''		
from functools import partial 
import maya.cmds as cmds
import maya.mel as mel
import colorsys
import random


def cHelp(*args):
	if cmds.window('win_tk_helpHouseBuilder', exists=1):
			cmds.deleteUI('win_tk_helpHouseBuilder')
	myWindow = cmds.window('win_tk_helpHouseBuilder', s=1, t='help', wh=(200, 200))

	helpText = '\n   Usage:\n   ---------\n   1.  Select the objects, you want the speed get measured.  \n   2.  "Create Speedometer On Selected Objects" sets up the scene. \n   3.  Choose "Position" to define where the HUD should be shown.\n        ---------------------------------------------\n        Depending on other HUDs and the viewport size, \n        the HUD may not be seen! \n        ---------------------------------------------\n   4.  Scene Scale to adjust the overall scale, eg 1:10.\n   5.  Chosse Decimals 0-2 to display decimal count in the HUD.\n        A HUD should appear in your viewport.\n   6.  "Clear HUD" removes the HUD.\n   ---------\n   The information (sceneScale, decimals, objects) is stored in the group "speed_lc_grp".\n   To remove all: Clear the HUD first, then delete the "speed_lc_grp".\n	'

	cmds.columnLayout(adj=1)
	cmds.text(helpText, al='left')
	cmds.showWindow(myWindow)


def cCreateSpeedometer(*args):
	grp 		= 'speed_lc_grp'
	lc 			= '_SLC'
	decimals	= cmds.intField('iDecimals', v=1, q=1)

	sceneScale 	= cmds.floatField('fSceneScale', v=1, q=1)
	objs = cmds.ls(sl=1, l=1)

	for obj in objs:
		if not cmds.objExists('speed_lc_grp'):
			grp = cmds.group(empty=1, n='speed_lc_grp')
			cmds.setAttr(grp + '.visibility', 0)

			cmds.addAttr(grp, ln='sceneScale', at='double', dv=0)
			cmds.setAttr(grp + '.sceneScale', e=1, k=1)
			cmds.setAttr(grp + '.sceneScale', sceneScale)

			cmds.addAttr(grp, ln='decimals', at='long', dv=1)
			cmds.setAttr(grp + '.decimals', e=1, k=1)
			cmds.setAttr(grp + '.decimals', decimals)


		if not cmds.objExists(obj + '_SLC') and len(objs) > 0:
			objShort = obj.split('|')[-1]
			if not cmds.objExists(objShort + '_SLC'):
				lc = cmds.spaceLocator(n=objShort + '_SLC',p=(0, 0,0))
	

				matrix = cmds.createNode('pointMatrixMult')
				cmds.connectAttr(obj + '.parentMatrix[0]', matrix + '.inMatrix')
				cmds.connectAttr(obj + '.translate', matrix + '.inPoint')
				cmds.connectAttr(matrix + '.output', lc[0] + '.translate')

				cmds.parent(lc, grp)

				cmds.addAttr(lc, ln='kmPerHour', at='double', dv=0)
				cmds.setAttr(lc[0] + '.kmPerHour', e=1, k=1)
				cmds.addAttr(lc, ln='milesPerHour', at='double', dv=0)
				cmds.setAttr(lc[0] + '.milesPerHour', e=1, k=1)

				exString = cExString(matrix, lc, sceneScale)

				cmds.expression(n="ex" + lc[0], s=exString, o="", ae=1, uc='all')

				cmds.headsUpMessage('speedometer created!')

				cmds.select(clear=1)
				cSpeedHud(1)



def cExString(matrix, lc, sceneScale, *args):
	exString  = 'float $read;\n'
	exString  = 'int $decimals;\n'
	exString += '$sceneScale = `getAttr speed_lc_grp.sceneScale`;\n'
	exString += '$deci = `getAttr speed_lc_grp.decimals`;\n'

	exString += 'if ($deci == 0)\n'
	exString += '\t$decimals = 1;\n' 
	exString += 'if ($deci == 1)\n'
	exString += '\t$decimals = 10;\n' 
	exString += 'if ($deci == 2)\n'
	exString += '\t$decimals = 100;\n' 
	
	exString += '$obj1 = "' + matrix + '";\n'
	
	exString += 'int $timex = (`currentTime -query`) -1;\n'
	
	exString += 'float $x = `getAttr ($obj1 + ".outputX")`;\n'
	exString += 'float $y = `getAttr ($obj1 + ".outputY")`;\n'
	exString += 'float $z = `getAttr ($obj1 + ".outputZ")`;\n'
	
	exString += 'float $x1 = `getAttr -t $timex ($obj1 + ".outputX")`;\n'
	exString += 'float $y1 = `getAttr -t $timex ($obj1 + ".outputY")`;\n'
	exString += 'float $z1 = `getAttr -t $timex ($obj1 + ".outputZ")`;\n'
	
	exString += '$read = mag( << $x-$x1,  $y-$y1,  $z-$z1  >> );\n'
	
	exString += '$read = $read *24 *60 *60;\n'
	exString += lc[0] + '.kmPerHour = float(int($read /100000 / $sceneScale *$decimals ))/$decimals;\n'
	exString += lc[0] + '.milesPerHour = float(int($read /100000 * 0.621371 / $sceneScale *$decimals))/$decimals;\n'

	return exString





def cExStringHudUpdate(lc, *args):
	exString  = 'if (`objExists "' + str(lc) + '"` == true)\n'
	exString += '\theadsUpDisplay -r headsUp' + str(lc) + ';'
	return exString



def cHUDGetPostion(*args):
	sel = cmds.radioCollection('rcPosition', q=1, sl=1)
	if sel == 'rb1':
		return 0, 10
	if sel == 'rb2':
		return 1, 0
	if sel == 'rb3':
		return 2, 4
	if sel == 'rb4':
		return 3, 0
	if sel == 'rb5':
		return 4, 6
	if sel == 'rb6':
		return 5, 2
	if sel == 'rb7':
		return 6, 0
	if sel == 'rb8':
		return 7, 7
	if sel == 'rb9':
		return 8, 0
	if sel == 'rb10':
		return 9, 18


def cSpeedHud(state, *args):
	if state == 1:
		# for i in range(0, 10, 1):
		# 	for k in range(0, 20, 1):
		# 		cmds.headsUpDisplay(rp=(i, k))

		cSpeedHud(0)

		block = 0

		if cmds.objExists('speed_lc_grp'):
			lcs = cmds.listRelatives('speed_lc_grp', c=1)
			section = cHUDGetPostion()

			for lc in lcs:
				cmds.headsUpDisplay('headsUp' + str(lc), c=partial(cReadHudContent, 1, lc), s=section[0], b=section[1] + block, bs='small', dw=250, dfs='large', lfs='large',l=lc, event='timeChanged')
				if not cmds.objExists('exUpdate' + str(lc)):
					exString = cExStringHudUpdate(lc)
					cmds.expression(n='exUpdate' + lc, s=exString, o="", ae=1, uc='all')

				block +=1



	if state == 0:
		if cmds.objExists('speed_lc_grp'):
			lcs = cmds.listRelatives('speed_lc_grp', c=1)

			for lc in lcs:
				if cmds.headsUpDisplay('headsUp' + lc, ex=1):
					cmds.headsUpDisplay('headsUp' + lc, rem=1)
				if cmds.objExists('exUpdate' + str(lc)):
					cmds.delete('exUpdate' + lc)


def cDelExpression(*args):
	ex = cmds.ls(type='expression')
	cmds.delete(ex)


def cReadHudContent(counter, lc, *args):
	txtHeadsUp = ''
	if counter == 1:
		hudKm		= " km/h"
		hudMiles	= ' miles/h'
		km			= cmds.getAttr(lc + '.kmPerHour')  
		miles 		= cmds.getAttr(lc + '.milesPerHour')  
		txtHeadsUp	= str(km)
		txtHeadsUp	+= " km/h --- "
		txtHeadsUp	+= str(miles)
		txtHeadsUp	+= " miles/h"

		return txtHeadsUp



def cAdjustAttr(field, attribute, *args):
	grp = 'speed_lc_grp'
	if cmds.objExists(grp):
		if attribute == 'sceneScale': 
			value = cmds.floatField(field, v=1, q=1)
			cmds.setAttr(grp + '.' + attribute, value)
		if attribute == 'decimals': 
			value = cmds.intField(field, v=1, q=1)
			cmds.setAttr(grp + '.' + attribute, value)





def tkSpeedometer():
	colRed				= [0.44, 0.2, 0.2];
	colGreen			= [0.28, 0.44, 0.28];
	colGreen2			= [0.18, 0.30, 0.18];
	colDark 			= [0.08, 0.09, 0.10];
	colDark2 			= [0.02, 0.21, 0.22];
	ver 				= '1.3'
	windowStartHeight 	= 50
	windowStartWidth 	= 480

	if (cmds.window('win_tkSpeedometer', exists=1)):
		cmds.deleteUI('win_tkSpeedometer')
	myWindow = cmds.window('win_tkSpeedometer', t=('win_tkSpeedometer ' + ver), s=1)

	cmds.columnLayout(adj=1, bgc=(colDark[0], colDark[1], colDark[2]))
	cmds.rowColumnLayout(nc=3, cw=[(1, 240), (2, 180), (3,120)])

	cmds.button(l='Create Speedometer on Selected Object', c=partial(cCreateSpeedometer), bgc=(colGreen[0], colGreen[1], colGreen[2]))
	cmds.button(l='HUD', c=partial(cSpeedHud, 1), bgc=(colGreen2[0], colGreen2[1], colGreen2[2]))
	cmds.button(l='Clear HUD', c=partial(cSpeedHud, 0), bgc=(colRed[0], colRed[1], colRed[2]))
	# cmds.button(l='Delete Expressions', c=partial(cDelExpression), bgc=(colRed[0], colRed[1], colRed[2]))
	cmds.setParent('..')

	cmds.columnLayout(adj=1, bgc=(colDark[0], colDark[1], colDark[2]))
	cmds.rowColumnLayout(nc=6, cw=[(1, 240), (2, 60), (3,60), (4, 60), (5, 60), (6, 60)])
	cmds.text('Position Top')
	cmds.radioCollection('rcPosition')
	cmds.radioButton('rb1', l='T 1', bgc=(colDark2[0], colDark2[1], colDark2[2]))
	cmds.radioButton('rb2', l='T 2')
	cmds.radioButton('rb3', l='T 3', sl=1, bgc=(colDark2[0], colDark2[1], colDark2[2]))
	cmds.radioButton('rb4', l='T 4')
	cmds.radioButton('rb5', l='T 5', bgc=(colDark2[0], colDark2[1], colDark2[2]))

	cmds.text('Position Bottom')
	cmds.radioButton('rb6', l='B 1', bgc=(colDark2[0], colDark2[1], colDark2[2]))
	cmds.radioButton('rb7', l='B 2')
	cmds.radioButton('rb8', l='B 3', bgc=(colDark2[0], colDark2[1], colDark2[2]))
	cmds.radioButton('rb9', l='B 4')
	cmds.radioButton('rb10', l='B 5', bgc=(colDark2[0], colDark2[1], colDark2[2]))

	cmds.setParent('..')
	# cmds.rowColumnLayout(nc=3, cw=[(1, 240), (2, 60), (3,240)])
	cmds.rowColumnLayout(nc=4, cw=[(1, 240), (2, 60), (3,180), (4,60)])
	cmds.text('Maya Scene Scale', bgc=(colGreen2[0], colGreen2[1], colGreen2[2]))
	cmds.floatField('fSceneScale', v=1, pre=2, min = .00001, cc=partial(cAdjustAttr, 'fSceneScale', 'sceneScale'), bgc=(colGreen[0], colGreen[1], colGreen[2]))
	cmds.text('Decimals', bgc=(colGreen2[0], colGreen2[1], colGreen2[2]))
	cmds.intField('iDecimals', min=0, max=2, v=1, cc=partial(cAdjustAttr, 'iDecimals', 'decimals'), bgc=(colGreen[0], colGreen[1], colGreen[2]))

	cmds.setParent('..')
	cmds.button(l='Help', c=partial(cHelp), bgc=(colDark[0], colDark[1], colDark[2]))
	
	cmds.showWindow(myWindow)

tkSpeedometer()
# cmds.window('win_tkSpeedometer', e=1, h=60)
cmds.window('win_tkSpeedometer', e=1, w=480, h=40, s=1)

