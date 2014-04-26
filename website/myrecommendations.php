<?php
session_start();

// setup Twig
require_once './vendor/autoload.php';
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

// confirm that the user is logged in
if (!isset($_SESSION['user_email'])){
        header('Location: ' . 'http://' . $_SERVER['HTTP_HOST'] . '/google_auth.php?redirect=myrecommendations');
}


/* TODO -- Stephen: get the user's email and run the recommendation algorithm
			output a few recommended meals

$facility_info = $_POST['facility'];
$facility_arr = split(":", $facility_info);
$facility_id = $facility_arr[0];
$facility_name = $facility_arr[1];

// connect to the database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

// query the database
mysql_select_db('cs411backend_food', $link);
$menu_query = "SELECT * FROM menus WHERE facility_id = $facility_id";
$result = mysql_query($menu_query)  or die($menu_query. "<br/><br/>".mysql_error());;

$rows = array();
while(($row = mysql_fetch_row($result)) != null)
{
        array_push($rows, $row);
}
*/


echo $twig->render('myrecommendations.html', array(
        'is_logged_in' => isset($_SESSION['user_email']))
);
?>

