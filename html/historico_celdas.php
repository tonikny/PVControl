<?php
$titulo="Historico Celdas";
include ("cabecera.inc");

require('conexion.php');



if(( $_POST["fecha1"] ) && ($_POST["fecha2"] )) {
   $fecha1 = $_POST["fecha1"];
   $fecha2 = $_POST["fecha2"];
   if ( $_POST["nseg_punto"] ) {
	   $nseg_punto=$_POST["nseg_punto"];   
   } else {
	   $nseg_punto=300;
   }
 }else{			
   	 $fecha1 = date("Y-m-d");
     $fecha2 = date("Y-m-d");
	 $nseg_punto=15;
 }
//Capturar datos de graficos ...maximo 10
$rawdata=[];
$tablas = [];
$ngraficos = 0;
$nceldas = [];
$n = 0;
if($result = mysqli_query($link, 'SHOW TABLES LIKE "datos_celdas%"')){
    while($tabla = mysqli_fetch_array($result)){
        // Calculo numero de celdas en tabla
        $sql = "SELECT * FROM ".$tabla[0]." LIMIT 1";
        //echo "---------------<br />";
        //echo $sql. "<br />";
        
        $resultado = mysqli_query($link,$sql);
        
        //printf("Tabla: %s\n", $tabla[0]);
        
        $campos = $resultado -> fetch_fields();
        
        $nceldas[$n] = 0;
        $lista_celdas = [];
        
        foreach ($campos as $val) {
          $campo = $val -> name;
          if($campo[0] == 'C'){ 
            $nceldas[$n]++;
            $lista_celdas[] = $campo; // Guardar lista de celdas para cálculo
          }
          
          //printf("Name: %s\n", $val -> name);
          
        }
        
      
        //echo "nceldas=$nceldas[$n] <br />";
        
        $tablas[$n] = $tabla[0];
        //echo $tablas[$n]. " -- ";
        
        $sql = "SELECT  *, UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo1
               FROM ".$tabla[0]." WHERE Tiempo BETWEEN '" . $fecha1 ." 00:00:00' and '".$fecha2 . " 23:59:59'
			   GROUP BY UNIX_TIMESTAMP(Tiempo) DIV ($nseg_punto)
			   ";
        if($result1 = mysqli_query($link, $sql)){
           
           
           //echo "Entro  en if con ngraficos= $ngraficos .. n = $n"."<br />";
           
           $j=0;
           
           while($row = mysqli_fetch_assoc($result1)) {
                // Extraer valores de celdas dinámicamente
                $valores_celdas = [];
                foreach ($lista_celdas as $celda) {
                    if (isset($row[$celda])) {
                        $valores_celdas[] = floatval($row[$celda]); // Convertir a número
                    }
                }

                // Calcular valores calculados
                $row['Vbat'] = array_sum($valores_celdas);
                $row['Dif_celdas'] = round((max($valores_celdas) - min($valores_celdas)) * 1000);
              
              
                $rawdata[$n][$j] = $row;
                $j++;
           }
           
           
         }else{
           echo "ERROR $sql. " . mysqli_error($link);
         }
         
         //echo count($rawdata[$n]). "<br />";
         //echo "salgo del if con filas=$j"."<br />";
         
         if ($j > 0) {
            $n++;
            $ngraficos++;
            //echo "Nuevo grafico valido... numero=$n<br />";
        
         }else{
            //echo "tabla sin datos<br />";
         }
           
         
    }
}
/*
echo "---------------<br />";
echo "RESUMEN<br />";
echo "N Graficos=$ngraficos<br />";
for($n = 0 ;$n<$ngraficos ;$n++){
  echo "N celdas$n=$nceldas[$n]<br />";
  echo "filas $n: ". count($rawdata[$n])."<br />";
}
*/

mysqli_close($link);

?>

<script src="Parametros_Web.js"></script>

<!-- Importo el archivo Javascript de Highcharts directamente desde la RPi 
<script src="js/jquery.js"></script>
<script src="js/stock/highstock.js"></script>
<script src="js/highcharts-more.js"></script>

<script src="js/themes/grid.js"></script>
-->


<!-- Importo el archivo Javascript directamente desde la webr -->
<!---->

<script src="https://code.jquery.com/jquery.js"></script>
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<script src="https://code.highcharts.com/highcharts-more.js"></script>

<script src="https://code.highcharts.com/themes/grid.js"></script>


<form action = "<?php $_PHP_SELF ?>" method = "POST">
    Periodo Desde: <input type="date" name="fecha1" value=<?php echo $fecha1 ?> />
    A: <input type="date" name="fecha2" value=<?php echo $fecha2 ?> />
    
    Muestra cada:<input type="number" size="5" name="nseg_punto" min="1" max="36000" step="1" value= <?php echo $nseg_punto ?> > seg__
    
    <input type = "submit" value = "Ver" />
		
</form>

<p></p>

<?php 
  // Se crean tantos div como graficos existan
  for($n = 0 ;$n<$ngraficos ;$n++)
    {
     //echo '<h3 style="color: #5e9ca0;" align="center">TABLA <span style="color: #2b2301;">'.$tablas[$n]."</span> Registros=".count($rawdata[$n])."</h3>";
     echo "<div id='container_".$n."' style='width: 100%; height: 80vh; margin-botton: 5px; float: left'></div>";
     echo "<p>&nbsp;</p>";
     //echo "<div id='sep_".$n."' style='width: 100%; height: 10px; float: left'></div>"; // separador
     
    }
    
?>


<script>
$(function () 
  {
  Highcharts.setOptions({
    global: {
      useUTC: false
      },

    time: {
        timezone: zona_horaria
    },

    lang: {
      months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
      weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
      shortMonths: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
      rangeSelectorFrom: "Desde",
      rangeSelectorTo: "A",
      printChart: "Imprimir gráfico",
      loading: "Cargando..."
      }
    });

  <?php
  
  for($n = 0 ;$n<$ngraficos ;$n++)
    {   $T = (0 == $n) ? '' : $n;
        echo "
        
      var char = new Highcharts.StockChart ({

      chart: {
        renderTo: 'container_".$n."',
        zoomType: 'xy',
        alignTicks: false,
        panning: true,
        panKey: 'shift'
        },
      title: {
        text: 'TABLA : ".$tablas[$n]."... Nº Registros:".count($rawdata[$n])."'
        },
      subtitle: {
        text: 'Voltaje Celdas / Ibat -- '
        },
      credits: {
        enabled: false
        },
      yAxis: [
       {// ########## Valores eje Vceldas ######################
        opposite: false,
        min: Vcelda_min[".$n."],
        max: Vcelda_max[".$n."],
        tickInterval: 0.1,
        //gridLineColor: 'transparent',
        minorGridLineColor: 'transparent',
        labels: {
          //align: 'left',
          y: 5
          },
        title: {
          align: 'high',
          offset: 0,
          text: 'Vcelda',//null
          rotation: 0,
          y: -10
          },
        plotBands: [{
          from: Vcelda_franja_min[".$n."],
          to: Vcelda_franja_max[".$n."],
          color: 'rgba(68, 170, 213, 0.2)',
          label: {
              text: ''
            }
          }],
       },
       {// ########## Valores eje Intensidad ######################
        opposite: true,
        min: Escala_intensidad_min_BMS[".$n."],
        max: Escala_intensidad_max_BMS[".$n."],
        tickInterval: 20,
        gridLineColor: 'transparent',
        minorGridLineColor: 'transparent',
        labels: {
          //align: 'left',
          y: 5
          },
        title: {
          align: 'high',
          offset: 0,
          text: 'Ibat',//null
          rotation: 0,
          y: -5
          },
        plotLines: [{
          value: 0,
          width: 2,
          color: 'black',
          dashStyle: 'shortdash'
          }]
       },
       {// ########## Valores eje AH ######################
        opposite: true,
        visible: false,
        min: 0,
        max: Escala_AH_BMS[".$n."],
        tickInterval: 20,
        gridLineColor: 'transparent',
        minorGridLineColor: 'transparent',
        labels: {
          //align: 'left',
          y: 5
          },
        title: {
          align: 'high',
          offset: -20,
          text: 'AH',
          rotation: 0,
          y: -20
          },
        
       },
       {// ########## Valores eje SOC ######################
        opposite: true,
        visible: false,
        min: 0,
        max: 100,
        tickInterval: 20,
        gridLineColor: 'transparent',
        minorGridLineColor: 'transparent',
        labels: {
          //align: 'left',
          y: 5
          },
        title: {
          align: 'high',
          offset: -20,
          text: 'SOC',
          rotation: 0,
          y: -20
          },
        
       },
       {// ########## Valores eje Vbat ######################
        opposite: true,
        visible: false,
        //min: 0,
        //max: 100,
        tickInterval: 1,
        gridLineColor: 'transparent',
        minorGridLineColor: 'transparent',
        labels: {
          //align: 'left',
          y: 5
          },
        title: {
          align: 'high',
          offset: -20,
          text: 'Vbat',
          rotation: 0,
          y: -20
          },
        
       },
       
       {// ########## Valores eje Dif_celdas ######################
        opposite: true,
        visible: false,
        min: 0,
        max: 300,
        //tickInterval: 1,
        gridLineColor: 'transparent',
        minorGridLineColor: 'transparent',
        labels: {
          //align: 'left',
          y: 5
          },
        title: {
          align: 'high',
          offset: -20,
          text: 'V',
          rotation: 0,
          y: -20
          },
        
       },
       ],
    
      xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
        },
      legend: {
        enabled: true
        },
      rangeSelector: {
        buttons: [{
          type: 'hour',
          count: 1,
          text: '1h'
         }, {
          type: 'hour',
          count: 8,
          text: '8h'
         }, {
          type: 'hour',
          count: 24,
          text: '24h'
         }, {
          type: 'all',
          text: 'Todo'
         }],
        selected: 2
        },
      tooltip: {
        valueSuffix: 'C1',
        split: true,
        distance: 30,
        padding: 2,
        outside: true,
        crosshairs: true,
        //shared: true,
        valueDecimals: 3
        },
      navigator: {
        enabled: true // false
        },
      series: 
        [";
    
         //  #### Ibat ####
        echo "
          {name: 'Ibat',
          type: 'spline',
          yAxis: 1,
          color: 'red', //Highcharts.getOptions().colors[2],
          tooltip: {
            valueSuffix: ' A',
            valueDecimals: 2,
            },
          data: (function() 
           {
            var data = [];
            ";
            
            for($i = 0 ;$i<count($rawdata[$n]);$i++){
              echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["Ibat"]."]);";
               }
                 
              echo "
               return data;
                        })()
                                 
                },"."\n";;
        
         //  #### Vbat ####
        echo "
          {name: 'Vbat',
          type: 'spline',
          yAxis: 4,
          visible: false,
          color: 'blue', //Highcharts.getOptions().colors[2],
          tooltip: {
            valueSuffix: ' V',
            valueDecimals: 2,
            },
          data: (function() 
           {
            var data = [];
            ";
            
            for($i = 0 ;$i<count($rawdata[$n]);$i++){
              echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["Vbat"]."]);";
               }
                 
              echo "
               return data;
                        })()
                                 
                },"."\n";;

        
         //  #### SOC ####
        echo "
          {name: 'SOC',
          type: 'spline',
          yAxis: 3,
          color: 'green', //Highcharts.getOptions().colors[2],
          tooltip: {
            valueSuffix: ' %',
            valueDecimals: 2,
            },
          data: (function() 
           {
            var data = [];
            ";
            
            for($i = 0 ;$i<count($rawdata[$n]);$i++){
              echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["SOC"]."]);";
               }
                 
              echo "
               return data;
                        })()
                                 
                },"."\n";;

         //  #### AH_p ####
        echo "
          {name: 'AH_p',
          type: 'area',
          yAxis: 2,
          color: 'rgba(255, 183, 51,0.5)',
          tooltip: {
            valueSuffix: ' Ah',
            valueDecimals: 1,
            
            },
          data: (function() 
           {
            var data = [];
            ";
            
            for($i = 0 ;$i<count($rawdata[$n]);$i++){
              echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["AH_p"]."]);";
               }
                 
              echo "
               return data;
                        })()
                                 
                },"."\n";;

        //  #### AH_n ####
        echo "
          {name: 'AH_n',
          type: 'spline',
          yAxis: 2,
          color: 'rgba(255, 183, 51,1)',
          tooltip: {
            valueSuffix: ' Ah',
            valueDecimals: 1,
            },
          data: (function() 
           {
            var data = [];
            ";
            
            for($i = 0 ;$i<count($rawdata[$n]);$i++){
              echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["AH_n"]."]);";
               }
                 
              echo "
               return data;
                        })()
                                 
                },"."\n";;

        //  #### Dif_celdas ####
        echo "
          {name: 'Dif',
          type: 'spline',
          yAxis: 5,
          //visible: false,
          color: 'magenta',
          tooltip: {
            valueSuffix: ' mV',
            valueDecimals: 0,
            },
          data: (function() 
           {
            var data = [];
            ";
            
            for($i = 0 ;$i<count($rawdata[$n]);$i++){
              echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["Dif_celdas"]."]);";
               }
                 
              echo "
               return data;
                        })()
                                 
                },"."\n";;
      
     //  #### Vceldas ####
      
       for($j = 1 ;$j<$nceldas[$n]+1 ;$j++)
       {
        $Cx = "C".$j;
        echo "\n" . "{name: '".$Cx."'";
        echo ",type: 'spline', color: Highcharts.getOptions().colors[".$j."],";
        echo "tooltip: {valueSuffix: ' V',valueDecimals: 3,},";
        echo "data: (function() {var data = [];";
        for($i = 0 ;$i<count($rawdata[$n]);$i++)
         {
          echo "data.push([";
          echo $rawdata[$n][$i]["Tiempo1"];
          echo ",";
          echo $rawdata[$n][$i][$Cx];
          echo"]);";
         }
        echo "return data;";
        echo "})()";
        echo "},";
       }
     
     echo"]

        });
  
        ";
   }

echo "  
 });
 </script>
    "; 


include ("pie.inc");
?>
