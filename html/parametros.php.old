<!--
<div><?php include 'Parametros_Web.js'; ?></div>
-->

<?php
$titulo="Inicio";
include("cabecera.inc");

require('conexion.php');

$sql = "SELECT * FROM parametros";

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


<?php
/**
 * Oculta parte de un string
 * @param  string  $str   Texto a ocultar
 * @param  integer $start Cuantos caracteres dejar sin ocultar al inicio
 * @param  integer $end   Cuantos caracteres dejar sin ocultar al final
 * @author Jodacame
 * @return string
 */
function hiddenString($str, $start = 1, $end = 1)
{
    $len = strlen($str);
    return substr($str, 0, $start) . str_repeat('*', $len - ($start + $end)) . substr($str, $len - $end, $end);
}
//echo hiddenString("123456789");
// Salida 1*******9
 
//echo hiddenString("123456789",5);
// Salida 12345***9
 
//echo hiddenString("123456789",5,0);
// Salida 12345****
 
//echo hiddenString("123456789",0,5);
// Salida ****56789
?>
<!--
<textarea id="areadetexto" rows="10" cols="50">
  <pre>
  <?php include "Parametros_Web.js"; ?>
  </pre>
</textarea>
-->

<div id="jst"  style="width: 47%; height: 50px; margin-left: 2%; float: left ">
  <h1 style="text-align: center;"><span style="background-color: #ffff99;"><strong>Parametros_Web.js</strong></h1>	
</div>	

<div id="pyt"  style="width: 47%; height: 50px; margin-right: 2%; float: right ">
  <h1 style="text-align: center;"><span style="background-color: #ffff99;"><strong>Parametros_FV.py</strong></h1>	
</div>	

<div id="js"  style="width: 47%; height: 500px; overflow:scroll; margin-left: 2%; float: left ">
  <?php
  $file = fopen("Parametros_Web.js", "r") or exit("Unable to open file!"); //Output a line of the file until the end is reached 
  while(!feof($file)) 
    { echo fgets($file);
	  echo "<br>";  } 
  fclose($file); 
  ?>

</div>

<div id="py"  style="width: 47%; height: 500px; overflow:scroll; margin-right: 2%; float: right">


<?php
  $file = fopen("../Parametros_FV.py", "r") or exit("Unable to open file!"); //Output a line of the file until the end is reached 
  while(!feof($file)) 
    {$a = fgets($file);
	 $pos = strpos($a, "***"); 
	 if ($pos === false) {
	   echo $a; 
	 }else{
	   echo hiddenString($a,10,0);
	  }  
	 echo "<br>"; 
    } 
  
  fclose($file); 
  echo "<br>"; 

?>
</div>


<div id="div1" style="width: 98%; height: 100px; margin-left: 2%; float: left">
  <hr />
  <h1 style="text-align: center;"><span style="background-color: #ffff99;"><strong>Tabla parametros</strong></h1>
  
  <table width="100%" border="1" style="text-align:center;">	
	<tr>
	<?php
       //Añadimos los titulos
       for($i=0;$i<$columnas-1;$i++){
         next($rawdata[0]);
         echo "<th><b>".key($rawdata[0])."</b></th>";
         next($rawdata[0]);
       }
    ?>                
	</tr>  
	<tbody>
        <?php
          for($i=0;$i<$filas;$i++){
            echo "<tr>";
            for($j=0;$j<$columnas-1;$j++){
              echo "<td>".$rawdata[$i][$j]."</td>";
               }
           echo "</tr>";
           }
         ?> 
            
      </tbody>
      
  </table>
  	  
 
  </table>

</div>


