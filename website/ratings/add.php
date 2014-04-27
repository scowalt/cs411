<?php
session_start();

if (!isset($_POST['rating']) || !isset($_POST['item'])){
	die;
}

// connect to the database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}
mysql_select_db('cs411backend_food', $link);

$netid = mysql_real_escape_string(netidOf($_SESSION['user_email']));
$rating = mysql_real_escape_string($_POST['rating']);
$item = mysql_real_escape_string($_POST['item']);

// query the database
$query = "INSERT INTO ratings (user_net_id, food_name, rating) VALUES " .
	"(\"$netid\", \"$item\", $rating)" . 
	" ON DUPLICATE KEY UPDATE rating = $rating";
$result = mysql_query($query) or die($query . "<br/><br />" . mysql_error());;

function netidOf($email){
	return substr($email, 0, (strlen($email) - 13));
}

?>