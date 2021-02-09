// speedometer.1.5.mel


global proc cShrinkWin(string $windowToClose)
{
	window -e -h 20 $windowToClose;
	window -e -w 280 $windowToClose;
}

global proc cSpeedometer()
{
	$mySel = `ls -sl`;
	string $flyer = $mySel[0];
	
	if (objExists ("SpeedoPointMatrixMult.inMatrix") == false)
		createNode pointMatrixMult -n "SpeedoPointMatrixMult";
		
	if (objExists ("SpeedoPointMatrixMult") == true)
	{

		connectAttr -f ($flyer + ".worldMatrix[0]") ("SpeedoPointMatrixMult.inMatrix");
		addAttr -ln "kmPerHour" -at double -dv 0 ("SpeedoPointMatrixMult");
		setAttr -e -keyable true ("SpeedoPointMatrixMult.kmPerHour");
		addAttr -ln "milesPerHour" -at double -dv 0 ("SpeedoPointMatrixMult");
		setAttr -e -keyable true ("SpeedoPointMatrixMult.milesPerHour");

		{
			expression -n "exSpeedo" -s "if (`objExists SpeedoPointMatrixMult` == true)\n{\n\t$obj1 = \"SpeedoPointMatrixMult\";\n\t\n\tint $timex = (`currentTime -query`) -1;\n\t\n\tfloat $x = `getAttr ($obj1 + \".outputX\")`;\n\tfloat $y = `getAttr ($obj1 + \".outputY\")`;\n\tfloat $z = `getAttr ($obj1 + \".outputZ\")`;\n\t\n\tfloat $x1 = `getAttr -t $timex ($obj1 + \".outputX\")`;\n\tfloat $y1 = `getAttr -t $timex ($obj1 + \".outputY\")`;\n\tfloat $z1 = `getAttr -t $timex ($obj1 + \".outputZ\")`;\n\t\n\t$read = mag( << $x-$x1,  $y-$y1,  $z-$z1  >> );\n\t\n\tfloat $read = $read *24 *60 *60;\n\t\n\tSpeedoPointMatrixMult.kmPerHour = int($read/100000); \n\tSpeedoPointMatrixMult.milesPerHour = int($read/100000 * 0.621371);\n}"  -o "" -ae 1 -uc all ;
		}
		
		headsUpMessage ("Speedometer created!");
	}
	else
		headsUpMessage ("Speedometer already there");
}

global proc cSpeedHud(int $state)
{
	if ($state == 1)	// add Hud
	{
		headsUpDisplay -rp 3 0;
		headsUpDisplay -rp 3 1;
		headsUpDisplay -rp 3 2;
		headsUpDisplay -rp 3 3;
		headsUpDisplay -rp 3 4;
		headsUpDisplay -rp 3 5;
		
		if (`objExists ("SpeedoPointMatrixMult.inMatrix")` == true){
			print "\n speed";
			headsUpDisplay -s 3 -b 0 -bs "small" -dw 250 -dfs "large" -lfs "large" -l "dra_01" -c "cReadHudContent(1)" -event "timeChanged" dra01HeadsUp;
		}
		
		
		if (`objExists ("exUpdateHUD")` == false)
			expression -n "exUpdateHUD" -s "if (`objExists \"SpeedoPointMatrixMult\"` == true)\n{\n\theadsUpDisplay -r dra01HeadsUp;\n\n   if (`objExists \"camHUD:camHUD\"` == true)\n{\n\theadsUpDisplay -r camHeight;\n\theadsUpDisplay -r camTilt;\n\theadsUpDisplay -r camFocalLength;\n}"  -o "" -ae 1 -uc all ;


	}
		
	if ($state == 0)	// remove Hud 
	{
		if (`headsUpDisplay -ex dra01HeadsUp`)
		{
			headsUpDisplay -remove dra01HeadsUp;
			headsUpDisplay -remove dra01HeadsUpHeight;
		}
			
			
		if (`objExists ("exUpdateHUD")` == true)
		{
			delete exUpdateHUD;
		}
	}


	
}

global proc string cReadHudContent(int $counter)
{
	// global string $dra01HeadsUp;
	// global string $dra02HeadsUp;
	// global string $dra03HeadsUp;

	if ($counter == 1)	// dra_01
	{
		$hudKm = " km/h, ";
		$hudMiles = " miles/h ";
		int $km1 = `getAttr ("SpeedoPointMatrixMult.kmPerHour")`;
		int $miles1 = `getAttr ("SpeedoPointMatrixMult.milesPerHour")`;
		string $dra01HeadsUp = (($km1) + ($hudKm) + ($miles1) + ($hudMiles));
		string $dra01HeadsUp = (($miles1) + ($hudMiles));
		
		return $dra01HeadsUp;
	}
	

	
	print "\n next frame";
}




///////////////////// window ////////////////////////////
global proc tk_speedometer()
{

$ver = "v1.5";
int $windowStartHeight = 50;
int $windowStartWidth = 280;
int $bh1 = 18;
int $bh2 = 22;

$nucEnable = 0;
$nucStartFrame = 1;
$nucSubstep = 4; 
$nucCollSubstep = 3; 

if( `window -exists win_tk_speedometer` )
	deleteUI win_tk_speedometer;

$myWindow = `window -title ("Speedometer " + $ver) -s 1 -wh $windowStartHeight $windowStartWidth win_tk_speedometer`;

/* -------------------- windowStart ------------------------- */

	
columnLayout -adj 1;		
	rowColumnLayout -nc 3 -cw 1 160 -cw 2 60 -cw 3 60;
		button -h $bh1 -l "Create Speedometer" -bgc .4 .3 .3  -c "cSpeedometer";
		button -h $bh1 -l "HUD" -c "cSpeedHud(1)";
		button -h $bh1 -l "Clear HUD" -c "cSpeedHud(0)";
		setParent..;
		
		showWindow $myWindow;
}
tk_speedometer;
cShrinkWin("win_tk_speedometer");