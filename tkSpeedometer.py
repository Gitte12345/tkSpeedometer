'''
tkSpeedometer.0.1.py
Thomas Kutschera
feb 2021

Help
--------------------------------------------------------------
Animate visibility in a row
		
'''		
from functools import partial 
import maya.cmds as cmds
import maya.mel as mel
import colorsys
import random




def cCreateSpeedometer(*args):
	grp = 'speed_lc_grp'
	lc 	= '_SLC'
	obj = cmds.ls(sl=1, l=1)[0]

	if not cmds.objExists('speed_lc_grp'):
		grp = cmds.group(empty=1, n='speed_lc_grp')

	if not cmds.objExists(obj + '_SLC'):
		objSrt = obj.split('|')[-1]
		lc = cmds.spaceLocator(n=objSrt + '_SLC',p=(0, 0,0))
		print lc

		matrix = cmds.createNode('pointMatrixMult')
		cmds.connectAttr(obj + '.parentMatrix[0]', matrix + '.inMatrix')
		cmds.connectAttr(obj + '.translate', matrix + '.inPoint')
		cmds.connectAttr(matrix + '.output', lc[0] + '.translate')

		cmds.parent(lc, grp)

		cmds.addAttr(lc, ln='kmPerHour', at='double', dv=0)
		cmds.setAttr(lc[0] + '.kmPerHour', e=1, k=1)
		cmds.addAttr(lc, ln='milesPerHour', at='double', dv=0)
		cmds.setAttr(lc[0] + '.milesPerHour', e=1, k=1)

		exString = cExString(matrix, lc)
		print exString

		cmds.expression(n="ex" + lc[0], s=exString, o="", ae=1, uc='all')

		cmds.headsUpMessage('speedometer created!')



def cExString(matrix, lc, *args):
	exString  = 'float $read;\n'
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
	exString += lc[0] + '.kmPerHour = int($read/100000);\n'
	exString += lc[0] + '.milesPerHour = int($read/100000 * 0.621371);\n'

	return exString
	


def cExStringHudUpdate(lc, *args):
	print lc
	exString  = 'if (`objExists ' + str(lc) + '"` == true)\n'
	exString += '\theadsUpDisplay -r headsUp' + str(lc) + ';'

	return exString


def cGetTime(lc):
	myTime = cmds.currentTime(q=1)
	print lc
	# return str(lc)
	return str(myTime)


def cSpeedHud(state, *args):
	if state == 1:
		cmds.headsUpDisplay(rp=(3, 0))
		cmds.headsUpDisplay(rp=(3, 1))
		cmds.headsUpDisplay(rp=(3, 2))
		cmds.headsUpDisplay(rp=(3, 3))
		cmds.headsUpDisplay(rp=(3, 4))
		cmds.headsUpDisplay(rp=(3, 5))

		if cmds.objExists('speed_lc_grp'):
			lcs = cmds.listRelatives('speed_lc_grp', c=1)

			for lc in lcs:
				print lc
				cmds.headsUpDisplay('headsUp' + str(lc), c=partial(cReadHudContent, 1, lc), s=3, b=0, bs='small', dw=250, dfs='large', lfs='large',l=lc, event='timeChanged')

				exString = cExStringHudUpdate(lc)
				cmds.expression(n='exUpdate' + lc, s=exString, o="", ae=1, uc='all')



	if state == 0:
		if cmds.objExists('speed_lc_grp'):
			lcs = cmds.listRelatives('speed_lc_grp', c=1)

			for lc in lcs:
				if cmds.headsUpDisplay('headsUp' + lc, ex=1):
					cmds.headsUpDisplay('headsUp' + lc, rem=1)


def cDelExpression(*args):
	ex = cmds.ls(type='expression')
	cmds.delete(ex)


def cReadHudContent(counter, lc, *args):
	txtHeadsUp = 'test'
	print 'cReadHudContent...'
	# print lc
	if counter == 1:
		hudKm		= "_kmh"
		# hudMiles	= ' miles h'
		km			= cmds.getAttr(lc + '.kmPerHour')  
		# miles 		= cmds.getAttr(lc + '.milesPerHour')  
		print km
		# txtHeadsUp	= str(km) + hudKm
		txtHeadsUp	= str(km)
		txtHeadsUp	+= " km/h"


		# print txtHeadsUp
		return txtHeadsUp



def tkSpeedometer():
	colRed				= [0.44, 0.28, 0.28];
	colGreen			= [0.28, 0.44, 0.28];
	colGreen2			= [0.18, 0.30, 0.18];
	colGreen3			= [0.08, 0.20, 0.08];
	colBlack			= [0.00, 0.00, 0.00];
	colSilverLight 		= [0.35, 0.42, 0.47];
	colSilverDark 		= [0.08, 0.09, 0.10];
	colSilverMid 		= [0.23, 0.28, 0.30];
	colSilverMid2 		= [0.17, 0.22, 0.24];
	ver = '0.1'
	windowStartHeight = 50
	windowStartWidth = 480
	bh1 = 18

	if (cmds.window('win_tkSpeedometer', exists=1)):
		cmds.deleteUI('win_tkSpeedometer')
	myWindow = cmds.window('win_tkSpeedometer', t=('win_tkSpeedometer ' + ver), s=1)

	cmds.columnLayout(adj=1, bgc=(colGreen3[0], colGreen3[1], colGreen3[2]))
	cmds.rowColumnLayout(nc=3, cw=[(1, 240), (2, 120), (3,120)])

	cmds.button(l='Create Speedometer on Selected Object', c=partial(cCreateSpeedometer), bgc=(colGreen[0], colGreen[1], colGreen[2]))
	cmds.button(l='HUD', c=partial(cSpeedHud, 1), bgc=(colGreen2[0], colGreen2[1], colGreen2[2]))
	cmds.button(l='Clear HUD', c=partial(cSpeedHud, 0), bgc=(colRed[0], colRed[1], colRed[2]))
	cmds.button(l='Delet Expressions', c=partial(cDelExpression), bgc=(colRed[0], colRed[1], colRed[2]))
	
	cmds.showWindow(myWindow)

tkSpeedometer()
# cmds.window('win_tkSpeedometer', e=1, h=60)
cmds.window('win_tkSpeedometer', e=1, w=480, h=40, s=1)

