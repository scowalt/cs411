<html>
<body>

<?php

$menu_id = htmlspecialchars($_GET['menu_id']);

$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

mysql_select_db('cs411backend_food', $link);
$menu_query = "SELECT * FROM menus_have_food_items WHERE menus_id = $menu_id";
$result = mysql_query($menu_query) or die($menu_query. "<br/><br/>".mysql_error());


while(($row = mysql_fetch_row($result)) != null)
{
	echo $row[1], "<br>";	// @TODO:  make this food item a link that opens nutritional information
}

?>


</body>
</html>