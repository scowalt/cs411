<?php

// setup Twig
require_once './vendor/autoload.php';
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

$menu_id = htmlspecialchars($_GET['menu_id']);

// connect to database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

// query databaase
mysql_select_db('cs411backend_food', $link);
$menu_query = "SELECT * FROM menus_have_food_items WHERE menus_id = $menu_id";
$result = mysql_query($menu_query) or die($menu_query. "<br/><br/>".mysql_error());

$rows = array();
while(($row = mysql_fetch_row($result)) != null)
{
	array_push($rows, $row);
}
echo $twig->render('menu.html', array('items' => $rows));

?>