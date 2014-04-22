<?php
/** Generate the facilities drop down selection menu **/

// setup Twig
require_once './vendor/autoload.php';
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

// start/resume user session for persistent information
session_start();

// connect to the database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

// query the database
mysql_select_db('cs411backend_food', $link);
$facility_names_query = "SELECT * FROM facilities";
$result = mysql_query($facility_names_query) or die($facility_names_query. "<br/><br/>".mysql_error());;

$rows = array();
while(($row = mysql_fetch_row($result)) != null)
{
    array_push($rows, $row);
}

echo $twig->render('index.html', array('facilities' => $rows))
?>