<?php
session_start();

// setup Twig                  
require_once './vendor/autoload.php';
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

// confirm that the user is logged in
if (!isset($_SESSION['user_email'])){
        header('Location: ' . 'http://' . $_SERVER['HTTP_HOST'] . '/google_auth.php?redirect=myratings');
}


$user_email = $_SESSION['user_email'];
$netid = split("@", $user_email)[0];


// connect to the database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}


// query the database
mysql_select_db('cs411backend_food', $link);
$ratings_query = "SELECT food_items.food_name, rating " .
                 "FROM food_items LEFT JOIN ratings " .
                 "ON food_items.food_name = ratings.food_name " .
                 "WHERE user_net_id = \"$netid\" " .
                 "ORDER BY rating DESC";

$result = mysql_query($ratings_query)  or die($ratings_query. "<br/><br/>".mysql_error());;


$rows = array();
while(($row = mysql_fetch_row($result)) != null)
{
        array_push($rows, $row);
}


echo $twig->render('menu.html', array(
        'is_logged_in' => isset($_SESSION['user_email']),
        'items' => $rows,
        'user' => $_SESSION['user_email'])
);
?>