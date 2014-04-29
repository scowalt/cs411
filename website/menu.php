<?php
session_start();

// setup Twig
require_once './vendor/autoload.php';
$loader = new Twig_Loader_Filesystem('./views');
$twig = new Twig_Environment($loader);

$menu_id = htmlspecialchars($_GET['menu_id']);

if(!isset($menu_id) || $menu_id === "") {
        header( 'Location: http://cs411backend.web.engr.illinois.edu' );
}

// connect to database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

// query databaase
mysql_select_db('cs411backend_food', $link);

$menu_id = mysql_real_escape_string($menu_id);

$menu_query = null;
// if the user is logged in
if (isset($_SESSION['user_email']) && $_SESSION['user_email']){
        $netid = netidOf($_SESSION['user_email']);
        // look for the ratings from that user
        $menu_query = "SELECT food_items.food_name,rating FROM " .
                "menus_have_food_items NATURAL JOIN food_items LEFT JOIN ratings " .
                "ON food_items.food_name = ratings.food_name " .
                "AND user_net_id = \"$netid\" WHERE menus_id = $menu_id";
} else {
        // just look for the food items
        $menu_query = "SELECT food_name FROM menus_have_food_items WHERE menus_id = $menu_id";
}

$result = mysql_query($menu_query) or die($menu_query. "<br/><br/>".mysql_error());

$food_items = array();
while(($row = mysql_fetch_row($result)) != null)
{
        array_push($food_items, $row);
}

echo $twig->render('menu.html', array(
        'is_logged_in' => isset($_SESSION['user_email']),
        'items' => $food_items,
        'user' => $_SESSION['user_email'])
);


function netidOf($email){
        return substr($email, 0, (strlen($email) - 13));
}

?>
