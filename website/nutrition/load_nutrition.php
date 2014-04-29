<?php

session_start();

if (!isset($_POST['food_name'])){
        die;
}

// connect to the database
$link = mysql_connect('engr-cpanel-mysql.engr.illinois.edu', 'cs411backend_web', 'teambackend');
if (!$link) {
    die('Not connected : ' . mysql_error());
}
mysql_select_db('cs411backend_food', $link);

$food_name = mysql_real_escape_string($_POST['food_name']);

// query the database
$query = "SELECT *
          FROM nutritional_information
          WHERE food_name = \"$food_name\"
          LIMIT 1";

$result = mysql_query($query) or die($query . "<br/><br />" . mysql_error());

$row = mysql_fetch_array($result);

$columns = array("calories","total_fat","saturated_fat","polyunsaturated_fat","monounsaturated_fat",
                "cholesterol","sodium","total_carbohydrate","dietary_fiber","vitamin_a","vitamin_c",
                "calcium","iron","protein","sugar");

if( $row != null ) {
        echo "<table>";
        for($i=0; $i < count($columns); $i++) {
                echo "<tr>
                        <td>$columns[$i]</td>
                        <td>" . $row[$columns[$i]] . "</td>
                      </tr>";
        }
        echo "</table";
}
else {
        echo "An error has occured";
}
?>