<?php

$server           = 'localhost';        # Server (default:localhost)
$username_mysql   = 'rpi';  		    # Mysql database user
$password_mysql   = 'fv';        	    # Mysql database password
$database_mysql   = 'control_solar';  	# Mysql database


#  Check database to host connection 
if(!function_exists('mysqli_connect'))
{
    echo 'PHP cannot find the mysql extension. MySQL is required for run. Aborting.';
    exit();
}

$link = mysqli_connect($server, $username_mysql, $password_mysql) or die('Error: Database to host connection: '.mysqli_error());

mysqli_select_db($link, $database_mysql) or die('Error: Select database: '.mysqli_error());
?>

