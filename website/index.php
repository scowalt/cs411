<html>

<body>
<h1>Project Backend</h1>
<p>A quest for food.</p>

<form method="POST" action='/facility.php'>
<select name='facility'>


<?php
/** Generate the facilities drop down selection menu **/

$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}

mysql_select_db('cs411backend_food', $link);
$facility_names_query = "SELECT * FROM facilities";
$result = mysql_query($facility_names_query) or die($facility_names_query. "<br/><br/>".mysql_error());;

while(($row = mysql_fetch_row($result)) != null)
{
    echo "<option value='{$row[0]}'>{$row[1]}</option>";
}
?>

</select>
<input type="submit" value="GO"/>
</form>

</body>
</html>