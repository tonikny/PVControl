<?php
include ("cabecera.inc");


// --------------------- TABLA RELES -----------------------------------------------

require('conexion.php');

date_default_timezone_set("UTC");

$sql_view = "CREATE VIEW reles_activos_hoy AS SELECT * FROM reles_segundos_on WHERE reles_segundos_on.fecha = CURDATE()";

mysqli_query($link, $sql_view);


$sql = "SELECT reles.id_rele,reles.nombre,ROUND(reles_activos_hoy.segundos_on,0) as segundos_on,reles_activos_hoy.nconmutaciones
	FROM reles
	LEFT JOIN reles_activos_hoy
	ON reles.id_rele = reles_activos_hoy.id_rele
	ORDER BY reles.id_rele";


if($result = mysqli_query($link, $sql)){

        $rawdata=array();
       	$i=0;

        while ($row = mysqli_fetch_array($result)){
       	        $rawdata[$i]=$row;
               	$i++;
       	}

       	echo '<table width="48%" border="1" style="text-align:center;">';
       	$columnas = count($rawdata[0])/2;
       	$filas = count($rawdata);

       	//Añadimos los titulos

        for($i=1;$i<count($rawdata[0]);$i=$i+2){
       	        next($rawdata[0]);
               	echo "<th><b>".key($rawdata[0])."</b></th>";
               	next($rawdata[0]);
       	}

        for($i=0;$i<$filas;$i++){
                echo "<tr>";
                for($j=0;$j<$columnas;$j++){
                    echo "<td>".$rawdata[$i][$j]."</td>";
                }
                echo "</tr>";
        }

        echo '</table>';

} else{

       	echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


echo "<br \>";


if( $_POST["id_rele"] ) {

    require('conexion.php');
    $rele = $_POST["id_rele"];

    //Coger datos grafica 1
    $sql = "SELECT fecha as Fecha, ROUND(segundos_on,0) as segundos FROM reles_segundos_on WHERE id_rele = $rele AND Fecha>= SUBDATE(NOW(), INTERVAL 7 DAY) GROUP BY Fecha";

    if($result = mysqli_query($link, $sql)){

            $i=0;
            while($row = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata10[$i] = $row;
                $i++;
            }

    } else{

            echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
    }


    //Coger datos grafica 2
    $sql = "SELECT Tiempo, valor_rele FROM reles_grab WHERE id_rele = $rele AND DATE(Tiempo)>= SUBDATE(NOW(), INTERVAL 7 DAY)";

    if($result = mysqli_query($link, $sql)){

            $rawdata=array();
            $rawdata1=array();

            $i=0;
            while($row = mysqli_fetch_assoc($result)) {
                    //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                    $rawdata[$i] = $row;
                    $rawdata1[$i] = $row;
                    $i++;
            }

    } else{

            echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
    }



    mysqli_close($link);


    //Adaptar el tiempo grafica1
    for($i=0;$i<count($rawdata10);$i++){
        $time = $rawdata10[$i]["Fecha"];
        $date = new DateTime($time);
        $rawdata10[$i]["Fecha"]=$date->getTimestamp()*1000;
    }

    //Adaptar el tiempo grafica2

    $valor_ant=0;

    for($i=0;$i<count($rawdata);$i++){
        $time = $rawdata[$i]["Tiempo"];
        $date = new DateTime($time);
        $rawdata1[2*$i]["Tiempo"]=$date->getTimestamp()*1000;
        $rawdata1[2*$i+1]["Tiempo"]=$date->getTimestamp()*1000;


        $valor=$rawdata[$i]["valor_rele"];
        $rawdata1[2*$i]["valor_rele"]=$valor_ant;
        $rawdata1[2*$i+1]["valor_rele"]=$valor;
        $valor_ant=$rawdata[$i]["valor_rele"];

    }

}


?>


<script src="https://code.jquery.com/jquery.js"></script>

<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="http://code.highcharts.com/themes/grid.js"></script>

<?php

require('conexion.php');
$sql = "SELECT id_rele FROM reles  ORDER BY id_rele";
$result = mysqli_query($link, $sql) ;
echo "id_rele: ";
      echo '<form style="display:inline-block" action="" method="POST"><select name="id_rele">';
      while($row = mysqli_fetch_assoc($result)) {
         echo '<option style="width:50px" value="'.$row['id_rele'].'">'.$row['id_rele'].'</option>';
      }
      // Cerramos lista + boton enviar + cerramos formulario
      echo '</select> <input type="submit" value="Ver" /></form>';

?>

<p></p>


<div id="container1" style="width: 48%; height: 240px;  margin: 5px; float: left"></div>
<div id="container2" style="width: 90%; height: 240px; margin: 5px; float: left"></div>

<script>
$(function () {

	Highcharts.setOptions({
            global: {
                useUTC: true
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

        var char1 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container1',
                //zoomType: 'xy'
            },

            title: {
                text: 'Tiempo ON ' + '<?php echo $rele;?>'
            },
            subtitle: {
                //text: 'Permite Zoom XY'
            },
            credits: {
                enabled: false
            },
	    xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
		type: 'datetime'
	    },
	    yAxis: {
		title: {
		    text: 'Horas'
		},
		labels: {
		    enabled: false
		},
		//type: 'datetime',
		dateTimeLabelFormats: { //force all formats to be hour:minute:second
			second: '%H:%M:%S',
			minute: '%H:%M:%S',
			hour: '%H:%M:%S',
			day: '%H:%M:%S',
			week: '%H:%M:%S',
			month: '%H:%M:%S',
			year: '%H:%M:%S'
		}
	    },
	    legend: {
		enabled: false
	    },
	    plotOptions: {
		column: {
		    dataLabels: {
			enabled: true,
			crop: false,
			overflow: 'none',
			formatter: function(){
			    if( this.series.index == 0 ) {
				return secondsTimeSpanToHMS(this.y/1000) ;
			    } else {
				return this.y;
			    }
			}
		    },
		    enableMouseTracking: false
		}
	    },
	    series: [{
		name: 'Tiempo',
		type: 'column',
		pointWidth: '30',
		color: Highcharts.getOptions().colors[0],
		data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata10);$i++){
                   ?>
                   data.push([<?php echo $rawdata10[$i]["Fecha"];?>,<?php echo $rawdata10[$i]["segundos"]*1000;?>]);
                   <?php } ?>
		return data;
                     })()
		}]
	});


        var chart2 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container2',
                zoomType: 'x',
                alignTicks: false,
            },
            title: {
                text: null,
                x:-0
            },
            subtitle: {
                text: null,
            },
            credits: {
                enabled: false
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'On/Off'
                },
                labels: {
                    enabled: false
                },

	    },

            legend: {
                enabled: false
            },

            series: [{
		name: 'Estado',
                type: 'line',
                color: Highcharts.getOptions().colors[0],
                tooltip: {
                },

                data: (function() {
                   var data = [];
                   <?php
                        for($i = 0 ;$i<count($rawdata1);$i++){
                   ?>

                   data.push([<?php echo $rawdata1[$i]["Tiempo"];?>,<?php echo $rawdata1[$i]["valor_rele"];?>]);

                   <?php } ?>
                return data;
                })()
            }]
        });

});


function secondsTimeSpanToHMS(s) {
    var h = Math.floor(s / 3600); //Get whole hours
    s -= h * 3600;
    var m = Math.floor(s / 60); //Get remaining minutes
    s -= m * 60;
    return h + ":" + (m < 10 ? '0' + m : m) + ":" + (s < 10 ? '0' + s : s); //zero padding on minutes and seconds
}


</script>

<?php
include ("pie.inc");
?>
