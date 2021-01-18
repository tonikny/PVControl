<html><body>
<?php
session_start();
$_SESSION['logged'] = "";
session_destroy();
header('Location: '.$_POST["origen"]);
exit();
?>
</body></html>
