<?php

// Variable de declaración en segundos
$ActualizarDespuesDe = 20;
 
// Envíe un encabezado Refresh al navegador preferido.
header('Refresh: '.$ActualizarDespuesDe);


$titulo="Equipos";
include ("cabecera.inc");

require('conexion.php');

$sql = "SELECT * FROM equipos";

if($result = mysqli_query($link, $sql)){
    $i=0;
    while ($row = mysqli_fetch_assoc($result)){
        $rawdata[$i]=$row;
        $i++;
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
}
mysqli_close($link);

$columnas = (isset($rawdata[0])) ? count($rawdata[0]) : 0;
$filas = count($rawdata);

function pretty_print($json_data) {
    //Initialize variable for adding space
    $space = 0;
    $flag = false;
    $keyPerLine = 10000; // infinito
    $num = 0;
    //Use <pre> or <code> tag to format alignment and font
    $json_pretty =  "";
    //loop for iterating the full json data
    for($counter=0; $counter<strlen($json_data); $counter++) {
        //Checking ending second and third brackets
        if( $json_data[$counter] == '}' || $json_data[$counter] == ']' ) {
                $space--;
                //$json_pretty .=  "<br />\n";
                $json_pretty .= str_repeat(' ', ($space*2));
        }
        if( $json_data[$counter-2] == '}' && $json_data[$counter-1] == ',' ) {
            $json_pretty .=  "<br /><br />\n";
            $json_pretty .= str_repeat(' ', ($space*2));
        }
        //Checking for double quote(“) and comma (,)
        if( $json_data[$counter] == '"'&& ($json_data[$counter-1] == ',' || $json_data[$counter-2] == ',') ) {
                $num++;
                if ($num % $keyPerLine == 0) $json_pretty .= "<br />";
                $json_pretty .= str_repeat(' ', ($space*2));
        }
        if( $json_data[$counter] == '"'&& !$flag ) {
            if( $json_data[$counter-1] == ':' || $json_data[$counter-2] == ':' )
                //Add formatting for question and answer
                $json_pretty .='<span style="color:darkblue">';
            else
                //Add formatting for answer options
                $json_pretty .='<span style="color:firebrick">';
        }
        $json_pretty .= $json_data[$counter];
        //Checking conditions for adding closing span tag  
        if( $json_data[$counter] == '"'&&$flag ) $json_pretty .= '</span>';
        if( $json_data[$counter] == '"' ) $flag= !$flag;
        //Checking starting second and third brackets
        if( $json_data[$counter] == '{' || $json_data[$counter] == '[' ) {
                $space++;
                $json_pretty .= "\n";
                $json_pretty .= str_repeat(' ', ($space*2));
        }
    }
    return trim($json_pretty,"{}");
}
?>

<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css" media="screen" />
<!--
<link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" media="screen" />
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/dataTables.bootstrap.min.css" media="screen" />
-->

<script src="https://code.jquery.com/jquery-3.3.1.js"></script>
<script src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>
<style>
    .tiempo {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: block;
        width: 100%;
        min-width: 1px;
        }
</style>
<div id="div1">

<table id="example" class="display compact" style="width:100%">
        <thead>
            <tr>
                <th>Tiempo</th><th>Equipo</th><th>Sensores</th>
            </tr>
        </thead>
        <tbody>
            <?php
                $formato = "Y-m-d H:i:s";
               	for($i=0;$i<$filas;$i++){
                    echo "<tr>";
                    $now =  date($formato);
                    if ($rawdata[$i]["tiempo"] < date($formato, strtotime("-30 seconds"))) $color = "red";
                    elseif ($rawdata[$i]["tiempo"] < date($formato, strtotime("-15 seconds"))) $color = "rgb(255,167,0,0.5)";
                    elseif ($rawdata[$i]["tiempo"] < date($formato, strtotime("-6 seconds"))) $color = "rgb(255,244,0,0.5)";
                    elseif ($rawdata[$i]["tiempo"] < date($formato, strtotime("-2 seconds"))) $color = "rgb(80,240,0,0.5)";
                    else $color = "rgb(44,186,0,0.6)";
                    print "<td style='background-color:".$color.";'><span class='tiempo'>".$rawdata[$i]["tiempo"]."</span></td>";

                    print "<td style='text-align:center'>".$rawdata[$i]["id_equipo"]."</td>";
                                       
                    print "<td style='color:darkblue'>".pretty_print($rawdata[$i]["sensores"])."</td>";
                    
                    echo "</tr>";
                }
             ?> 
            
        </tbody>
        <tfoot>
                <th>Tiempo</th><th>Equipo</th><th>Sensores</th>
        </tfoot>

</table>

</div>


<script>
$(document).ready(function() {
    $('#example').DataTable({
        "order": [[ 1, "asc" ]],
        "scrollY": "10000px",
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

