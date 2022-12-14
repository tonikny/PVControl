<?php
$titulo="Historico Hibrido";
include ("cabecera.inc");

require('conexion.php');

if(( isset($_POST["fecha1"]) ) && (isset($_POST["fecha2"]) )) {
   $fecha1 = $_POST["fecha1"];
   $fecha2 = $_POST["fecha2"];
   if ( $_POST["nseg_punto"] ) {
	   $nseg_punto=$_POST["nseg_punto"];   
   } else {
	   $nseg_punto=60;
   }
   
 }else{			
   	 $fecha1= date("Y") . "-" . date("m") . "-" . date("d");
     $fecha2= date("Y") . "-" . date("m") . "-" . date("d");
	 $nseg_punto=60;
    
 }

//Ver numero de Hibridos activos...maximo 10
$rawdata=[];
$ngraficos=0;

if($result = mysqli_query($link, 'SHOW TABLES LIKE "hibrido%"')){
    $n = 0;
    while($tabla = mysqli_fetch_array($result)){
        //$sql = "SELECT Tiempo, AVG(Vbus) as Vbus,(AVG(Vbus)/Avg(Vbat))*30 as Vbus_Vbat, (AVG(Ibatp)-AVG(Ibatn)) as Ibat,
        //               AVG(Iplaca) as Iplaca, AVG(Vbat) as Vbat, AVG(Temp) as Temp, AVG(PACW) as PACW, AVG(Flot)*50 as Flot
        //      FROM hibrido".i." WHERE DATE(Tiempo) >= '" . $fecha1 . "' and DATE(Tiempo) <= '" . $fecha2 . "'
        //      GROUP BY DAY(Tiempo),FLOOR(TIME_TO_SEC(TIME(Tiempo))/" . $nseg_punto . " ) ORDER BY Tiempo";
        
        $sql = "SELECT  *, UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo1,(Ibatp-Ibatn) as Ibat, Flot * 50 as Flot1
               FROM ".$tabla[0]." WHERE Tiempo BETWEEN '" . $fecha1 ." 00:00:00' and '".$fecha2 . " 23:59:59'";
        
        if($result1 = mysqli_query($link, $sql)){
           $ngraficos++;
           $j=0;
           
           while($row = mysqli_fetch_assoc($result1)) {
              $rawdata[$n][$j] = $row;
              $j++;
           }
           //echo "  N_puntos=",$i;
         }else{
           echo "ERROR $sql. " . mysqli_error($link);
         }
         $n++;
    }
}

mysqli_close($link);
?>

<!-- Importo el archivo Javascript de Highcharts directamente desde la RPi
<script src="js/jquery.js"></script>
<script src="js/stock/highstock.js"></script>
<script src="js/highcharts-more.js"></script>

<script src="js/themes/grid.js"></script>
-->

<!-- Importo el archivo Javascript directamente desde la web -->
<script src="https://code.jquery.com/jquery.js"></script>
<script src="http://code.highcharts.com/stock/highstock.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="http://code.highcharts.com/themes/grid.js"></script>

<form action = "<?php $_PHP_SELF ?>" method = "POST">
    Periodo Desde: <input type="date" name="fecha1" value=<?php echo $fecha1 ?> />
    A: <input type="date" name="fecha2" value=<?php echo $fecha2 ?> />
	<!--
    Muestra cada:<input type="number" size="5" name="nseg_punto" min="4" max="3600" step="4" value= <?php echo $nseg_punto ?> > seg__
    -->
    <input type = "submit" value = "Ver" />
		
</form>

<p></p>

<?php 
  
  for($n = 0 ;$n<$ngraficos ;$n++)
    {
     echo "<div id='container_".$n."' style='width: 100%; height: 80vh; margin-left: 5; float: left'></div>"."\n";
    }
    
?>

<br>

<script>

$(function () {

	Highcharts.setOptions({
            global: {
                useUTC: false
            },
	    lang: {
		  months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
		  weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
		  shortMonths: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
	        rangeSelectorFrom: "Desde",
	        rangeSelectorTo: "A",
 	        printChart: "Imprimir gr??fico",
		  loading: "Cargando..."
	    }
        });
  <?php
  
  for($n = 0 ;$n<$ngraficos ;$n++)
    {   $T = (0 == $n) ? '' : $n;
        echo
          "
          var char = new Highcharts.StockChart ({
            chart: {
                renderTo: 'container_".$n."',
                zoomType: 'xy',
				panning: true,
                panKey: 'shift'
            },

            title: {
                text: 'HIBRIDO".$T." -  Vbus, Iplaca/Ibat/Vbat/PACW/Flot y Temp Disipador'
            },
            subtitle: {
                //text: 'Permite Zoom XY'
            },
            credits: {
                enabled: false
            },
            yAxis: [{
		        opposite: false,
				min: Escala_intensidad_min,
		        max: Escala_intensidad_max ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                }
             },{
                opposite: false,
				min: Escala_Vbat_min,
		        max: Escala_Vbat_max ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: Vabs,
		            width: 2,
		            color: 'green',
		            dashStyle: 'shortdash',
		            label: {
			            text: 'Vabs'
		             }
		            }, {
		            value: Vflot,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: 'Vflot'
		              }
		          }]
	
             },{
                opposite: true,
				min: 0,
		        max: 500 ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: 480,
		            width: 2,
		            color: 'green',
		            dashStyle: 'shortdash',
		            label: {
			            text: '480= Ratio 16*30'
		                   }
		            }, {
		            value: 80,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: '80%'
					       }
		              }, {
		            value: 30,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: '30??C'
		                   }
		          }]
		       },{
                opposite: true,
				min: Escala_Wred_min,
		        max: Escala_Wred_max ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: 1000,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: '1000w'
		                   }
		          }]
		
			 }],
			
			xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
             },
            legend: {
                enabled: true
             },

            rangeSelector: {
                buttons: [{
                    type: 'day',
                    count: 1,
                    text: '1d??a'
                }, {
                    type: 'day',
                    count: 3,
                    text: '3d??as'
                },	{
                    type: 'day',
                    count: 7,
                    text: '7d??as'
                }, {
                    type: 'day',
                    count: 15,
                    text: '15d??as'
                }, {
                    type: 'all',
                    text: 'Todo'
                }],
                selected: 1
             },
            tooltip: {
                crosshairs: true,
                shared: true,
                valueDecimals: 2
             },

            series:
             [";
            
            //  #### Vbus ####
            echo "
              { name: 'Vbus',
                type: 'spline',
				yAxis: 2,
                color: Highcharts.getOptions().colors[1],
                tooltip: {
                    valueSuffix: ' V',
                    valueDecimals: 0,
                },
                data: (function()
                {
                   var data = [];
              ";
                   
              for($i = 0 ;$i<count($rawdata[$n]);$i++){
                echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["Vbus"]."]);";
               }
              echo "
                return data;
                                })()
                              
                 },";
                 
            //  #### Vbat ####
            echo "
              { name: 'Vbat',
                type: 'spline',
				yAxis: 1,
                color: Highcharts.getOptions().colors[0],
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
                              
                 },";
                 
             //  #### Ibat ####
            echo "
              { name: 'Ibat',
                type: 'spline',
				yAxis: 0,
                color: Highcharts.getOptions().colors[2],
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 0,
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
                              
                 },";
                 
             //  #### Iplaca ####
            echo "
              { name: 'Iplaca',
                type: 'spline',
				yAxis: 0,
                color: Highcharts.getOptions().colors[3],
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 0,
                },
                data: (function()
                {
                   var data = [];
              ";
                   
              for($i = 0 ;$i<count($rawdata[$n]);$i++){
                echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["Iplaca"]."]);";
               }
              echo "
                return data;
                                })()
                              
                 },";     
                 
            //  #### Temp Disipador ####
            echo "
              { name: 'Temp Disipador',
                type: 'spline',
				yAxis: 0,
                color: 'black', //Highcharts.getOptions().colors[3],
                tooltip: {
                    valueSuffix: ' ??C',
                    valueDecimals: 0,
                },
                data: (function()
                {
                   var data = [];
              ";
                   
              for($i = 0 ;$i<count($rawdata[$n]);$i++){
                echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["temp"]."]);";
               }
              echo "
                return data;
                                })()
                              
                 },";     
                 
            //  #### Consumo AC ####
            echo "
              { name: 'Consumo AC',
                type: 'spline',
				yAxis: 3,
                color: 'brown',
                tooltip: {
                    valueSuffix: ' W',
                    valueDecimals: 0,
                },
                data: (function()
                {
                   var data = [];
              ";
                   
              for($i = 0 ;$i<count($rawdata[$n]);$i++){
                echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["PACW"]."]);";
               }
              echo "
                return data;
                                })()
                              
                 },";     
                 
            //  #### FLOT ####
            echo "
              { name: 'Flot',
                type: 'spline',
				yAxis: 2,
                color: 'green',
                tooltip: {
                    valueSuffix: ' ',
                    valueDecimals: 0,
                },
                data: (function()
                {
                   var data = [];
              ";
                   
              for($i = 0 ;$i<count($rawdata[$n]);$i++){
                echo "data.push([".$rawdata[$n][$i]["Tiempo1"].",".$rawdata[$n][$i]["Flot1"]."]);";
               }
              echo "
                return data;
                                })()
                              
                 },";     
                 
                 
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
