<?php

// setup Twig
require_once './vendor/autoload.php';
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

// confirm that the user is logged in
if (!isset($_SESSION['user_email'])){
	header('Location: ' . 'http://' . $_SERVER['HTTP_HOST'] . '/google_auth.php?redirect=notification');
}

// connect to database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}
mysql_select_db('cs411backend_food', $link);

// if the form has been submitted
if(isset($_POST['submit'])){
	// SQL escape data received
	$netid = mysql_real_escape_string($_POST['netid']);
    $facility = mysql_real_escape_string($_POST['facility']);
    $item = mysql_real_escape_string($_POST['item']);

    // add user to database
    $query = "INSERT IGNORE INTO users (user_net_id) VALUES (\"$netid\")";
    $result = mysql_query($query) or die($query . "<br/><br />" . mysql_error());;

    // add notification registration to database
    $query = "INSERT INTO notifications (user_net_id, food_name, facility_id) VALUES (\"$netid\",\"$item\",$facility)";
    $result = mysql_query($query) or die($query . "<br/><br />" . mysql_error());;

	// display whether or not signing up for the notification was successful
	echo "notification registration successful";
} else {
	// query the database for facilities	
	$facility_names_query = "SELECT * FROM facilities";
	$result = mysql_query($facility_names_query) or die($facility_names_query. "<br/><br/>".mysql_error());;
	$facilities = array();
	while(($row = mysql_fetch_row($result)) != null)
	{
	    array_push($facilities, $row);
	}

	// query the database for food items
	$query = "SELECT food_name FROM food_items";
	$result = mysql_query($query) or die($query . "<br/>" . mysql_error());;
	$items = array();
	while(($row = mysql_fetch_row($result)) != null)
	{
	    array_push($items, $row);
	}

	// display the notification sign-up form
	echo $twig->render('notification.html', array('facilities' => $facilities, 'items' => $items));

}

?>
