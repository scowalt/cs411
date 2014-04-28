<?php
session_start();

if (!isset($_POST['location']) || !isset($_POST['item'])){
	die;
}

// connect to the database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}
mysql_select_db('cs411backend_food', $link);

$netid = mysql_real_escape_string(netidOf($_SESSION['user_email']));
$location = mysql_real_escape_string($_POST['facility_id']);
$item = mysql_real_escape_string($_POST['item']);

// query the database
$query = "DELETE from notifications " .
	"WHERE user_net_id = \"$netid\" AND food_name = \"$item\" AND facility_id = $location";

$result = mysql_query($query) or die($query . "<br/><br />" . mysql_error());;

function netidOf($email){
	return substr($email, 0, (strlen($email) - 13));
}

?>