<?php
session_start();

// setup Twig
require_once './vendor/autoload.php';
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

$facility_info = $_POST['facility'];
$facility_arr = split(":", $facility_info);
$facility_id = $facility_arr[0];
$facility_name = $facility_arr[1];

if(!isset($facility_info) || $facility_id === "") {
        header( 'Location: http://cs411backend.web.engr.illinois.edu' );
}

// connect to the database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

// query the database
mysql_select_db('cs411backend_food', $link);

$facility_name = mysql_real_escape_string($facility_name);

$menu_query = "SELECT *
                FROM menus
                WHERE facility_id = $facility_id
                AND date >= CURDATE()
                ORDER BY date, meal_type";
$result = mysql_query($menu_query)  or die($menu_query. "<br/><br/>".mysql_error());;

$rows = array();
while(($row = mysql_fetch_row($result)) != null)
{
        array_push($rows, $row);
}

echo $twig->render('facility.html', array(
        'is_logged_in' => isset($_SESSION['user_email']),
        'facility_name' => $facility_name, 'menus' => $rows)
);
?>
