<html>
<body>

<?php

$facility_id = $_POST['facility'];

$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

mysql_select_db('cs411backend_food', $link);
$menu_query = "SELECT * FROM menus WHERE facility_id = $facility_id";
$result = mysql_query($menu_query)  or die($menu_query. "<br/><br/>".mysql_error());;

while(($row = mysql_fetch_row($result)) != null)
{
	echo "<a href='/menu.php?menu_id=$row[0]'>$row[1]  --  $row[3]</a><br>";
}

?>


</body>
</html>