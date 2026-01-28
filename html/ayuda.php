<?php

$page = urldecode($_GET['page']) ? urldecode($_GET['page']) : 'index.md';

$titulo="Ayuda";
include_once "cabecera.inc";
?>
<style type="text/css">
    /* div, p, nav, ul, li, a {
        all: revert;
    } */
    #content {
        width: 80%;
        margin: auto;
        padding: 20px 50px;
        background: lightgray;
        border-radius: 10px;
    }
</style>

<div id="content"></div>
<script src="ayuda/showdown.min.js"></script>
<script src="ayuda/ayuda.js"></script>
<script type="text/javascript">
    md2html("ayuda/<?php echo $page; ?>");
</script>

<?php
include_once "pie.inc";
?>

