<?php

# Connect to the database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

# Switch to the proper database
mysql_select_db('cs411backend_food', $link);

# Get tomorrow's date
date_default_timezone_set('America/Chicago');
$tomorrow = $str = date("Y-m-d", mktime(0, 0, 0, date("m")  , date("d")+1, date("Y")));

# Find all food_items that will be served tomorrow
$query = "SELECT user_net_id, food_name, name, meal_type " .
	"FROM notifications NATURAL JOIN food_items NATURAL JOIN menus_have_food_items NATURAL JOIN menus NATURAL JOIN facilities " . 
	"WHERE date = \"$tomorrow\"";

# query the database
$result = mysql_query($query) or die(mysql_error());

# iterate through the results
while(($row = mysql_fetch_row($result)) != null){
	$to = $row[0] . '@illinois.edu';
	$subject = 'Food notification';
	$message = $row[1] . ' is available tomorrow at ' . $row[2] . ' for ' . $row[3];
	$headers = 'From: Food' . "\r\n" . 
  		'X-Mailer: PHP/' . phpversion();

	mail($to, $subject, $message, $headers);
}

?>