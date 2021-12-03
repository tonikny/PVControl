<?php

// Variable de declaración en segundos
$ActualizarDespuesDe = 20;
 
// Envíe un encabezado Refresh al navegador preferido.
header('Refresh: '.$ActualizarDespuesDe);


$titulo="Diario";
include ("cabecera.inc");

require('conexion.php');

$sql = "SELECT * FROM equipos";

if($result = mysqli_query($link, $sql)){
    $i=0;
    while ($row = mysqli_fetch_array($result)){
        $rawdata[$i]=$row;
        $i++;
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }
mysqli_close($link);

$columnas = (isset($rawdata[0])) ? count($rawdata[0])/2 : 0;
$filas = count($rawdata);

?>

<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css" media="screen" />
<!--
<link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" media="screen" />
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/dataTables.bootstrap.min.css" media="screen" />
-->

<script src="https://code.jquery.com/jquery-3.3.1.js"></script>
<script src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>

<div id="div1">

<table id="example" class="display compact" style="width:100%">
        <thead>
            <tr>
             <?php
                //Añadimos los titulos
                for($i=0;$i<$columnas;$i++){
                    next($rawdata[0]);
                    echo "<th><b>".key($rawdata[0])."</b></th>";
                    next($rawdata[0]);
                }
               ?>                
            </tr>
        </thead>
        <tbody>
            <?php
               	for($i=0;$i<$filas;$i++){
                    echo "<tr>";
                    for($j=0;$j<$columnas;$j++){
                        echo "<td>".$rawdata[$i][$j]."</td>";
                    }
                    echo "</tr>";
                }
             ?> 
            
        </tbody>
        <tfoot>
            <?php
                //Añadimos los pies
                for($i=1;$i<count($rawdata[0]);$i=$i+2){
                    next($rawdata[0]);
                    echo "<th><b>".key($rawdata[0])."</b></th>";
                    next($rawdata[0]);
                }
               ?>                
        </tfoot>

</table>

</div>


<script>
$(document).ready(function() {
    $('#example').DataTable({
        "order": [[ 0, "asc" ]],
        "scrollY": "800px",
        "scrollCollapse": true,
        "scrollX": true,
        "info":    false,
        "paging":  false
        
    } );
} );

</script>
    
<?php
include ("pie.inc");
?>

