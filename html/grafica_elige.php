<?php
include ("cabecera.inc");

 require('conexion.php');
 date_default_timezone_set("UTC");
 $rango="ASEM";
 $parametro="Produccion";

 $sql = "SELECT FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7)) AS Fecha, TRUNCATE(SUM(Wh_placa/1000),2) as Datos
                        FROM diario
                        WHERE Fecha>= DATE_SUB(curdate(), INTERVAL (364 -2 + DAYOFWEEK(curdate())) DAY)
                        GROUP BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7))
                        ORDER BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7))";

 $vartitulo = "Producción Anual kWh por Semanas";
 $anchocol= 20;

 if(( $_POST["parametro"] ) && ($_POST["rango"] )) {//|| (($rango=="MONTH") && ($parametro=="Produccion")){
    $parametro = $_POST["parametro"];
    $rango = $_POST["rango"];

    if($parametro == "Produccion") {

      $colorbar = 'rgba(100,149,237,0.8)';

	  if($rango=="WEEK") {
		$sql = "SELECT Fecha, TRUNCATE(Wh_placa/1000,2) as Datos FROM diario
			WHERE WEEK(Fecha,1) = WEEK(CURDATE(),1) AND YEAR(Fecha) = YEAR(CURDATE())
			GROUP BY Fecha";

		$vartitulo = "Producción Semanal kWh";
		$anchocol = 40;

	  } elseif($rango=="MONTH") {
		 $sql = "SELECT Fecha, TRUNCATE(Wh_placa/1000,2) as Datos FROM diario
			WHERE MONTH(Fecha) = MONTH(CURDATE()) AND YEAR(Fecha) = YEAR(CURDATE())
			GROUP BY Fecha";

		 $vartitulo = "Producción Mensual kWh";
		 $anchocol= 20;

	  } elseif($rango=="ASEM") {

         $sql = "SELECT FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7)) AS Fecha, TRUNCATE(SUM(Wh_placa/1000),2) as Datos
                        FROM diario
                        WHERE Fecha>= DATE_SUB(curdate(), INTERVAL (364 -2 + DAYOFWEEK(curdate())) DAY)
                        GROUP BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7))
                        ORDER BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7))";

		 $vartitulo = "Producción Anual kWh por Semanas";
		 $anchocol= 20;

	  } else {

          $sql = "SELECT STR_TO_DATE(concat('1,', MONTH(Fecha), ',', YEAR(Fecha)), '%d,%m,%Y') as Fecha, TRUNCATE(SUM(Wh_placa/1000),2) as Datos
                        FROM diario
                        WHERE Fecha >= STR_TO_DATE(concat('1,', MONTH(curdate()), ',', YEAR(curdate())-1), '%d,%m,%Y')
                        GROUP BY YEAR(Fecha),MONTH(Fecha)";

          $vartitulo = "Producción Anual kWh por Meses";
          $anchocol= 40;

	  }


    } elseif($parametro == "Consumo") {

	    $colorbar = 'rgba(255,0,0,0.8)';

        if($rango=="WEEK") {
                $sql = "SELECT Fecha, TRUNCATE((Wh_placa-(Whp_bat-kWhn_bat))/1000,2) as Datos FROM diario
                        WHERE WEEK(Fecha,1) = WEEK(CURDATE(),1) AND YEAR(Fecha) = YEAR(CURDATE())
                        GROUP BY Fecha";

                $vartitulo = "Consumo kWh Semanal";
                $anchocol = 40;

        } elseif($rango=="MONTH") {
                $sql = "SELECT Fecha, TRUNCATE((Wh_placa-(Whp_bat-Whn_bat))/1000,2) as Datos FROM diario
                        WHERE MONTH(Fecha) = MONTH(CURDATE()) AND YEAR(Fecha) = YEAR(CURDATE())
                        GROUP BY Fecha";

                $vartitulo = "Consumo kWh Mensual";
                $anchocol= 20;

        } elseif($rango=="ASEM") {

                $sql = "SELECT FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7)) AS Fecha, TRUNCATE(SUM(Wh_placa-(Whp_bat-Whn_bat))/1000,2) as Datos
                        FROM diario
                        WHERE Fecha>= DATE_SUB(curdate(), INTERVAL (364 -2 + DAYOFWEEK(curdate())) DAY)
                        GROUP BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7))
                        ORDER BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 7))";


                $vartitulo = "Consumo Anual kWh por Semanas";
                $anchocol= 20;

        } else {

                $sql = "SELECT STR_TO_DATE(concat('1,', MONTH(Fecha), ',', YEAR(Fecha)), '%d,%m,%Y') as Fecha, TRUNCATE(SUM(Wh_placa-(Whp_bat-Whn_bat))/1000,2) as Datos
                        FROM diario
                        WHERE Fecha >= STR_TO_DATE(concat('1,', MONTH(curdate()), ',', YEAR(curdate())-1), '%d,%m,%Y')
                        GROUP BY YEAR(Fecha),MONTH(Fecha)";

                $vartitulo = "Consumo Anual kWh por Meses";
                $anchocol= 40;

        }

    }
}

    if($result = mysqli_query($link, $sql)){

        $total=0;
	    $i=0;
	    while($row1 = mysqli_fetch_assoc($result)) {
		    //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
		    $rawdata1[$i] = $row1;
                    $total=$total+$rawdata1[$i]["Datos"];
		    $i++;
	    }

    } else{

            echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
    }


    mysqli_close($link);


    //Adaptar el tiempo grafica4
    for($i=0;$i<count($rawdata1);$i++){
        $time = $rawdata1[$i]["Fecha"];
        $date = new DateTime($time);
        $rawdata1[$i]["Fecha"]=$date->getTimestamp()*1000;
    }


?>

<script src="https://code.jquery.com/jquery.js"></script>

<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="http://code.highcharts.com/themes/grid.js"></script>


<form action = "<?php $_PHP_SELF ?>" method = "POST">
    <select name="parametro">
	<option value="Produccion">Producción</option>
        <option value="Consumo">Consumo</option>
    </select>
    <select name="rango">
        <option value="WEEK">Semana</option>
        <option value="MONTH">Mes</option>
	    <option value="ASEM" selected >AñoXSem</option>
	    <option value="AMES">AñoXMes</option>
    </select>
    <input type = "submit" value = "Ver" />
</form>

<p></p>

<div id="container1" style="width: auto;height: 60vh;margin-left: 5;margin-right:5"></div>
<br>


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

        var chart1 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container1',
                zoomType: 'xy'
            },

            title: {
                text: '<?php echo $vartitulo.' '.$total;?>'
	    },

            subtitle: {
                //text: 'Permite Zoom XY'
            },
            credits: {
                enabled: false
            },
	    xAxis: {
                dateTimeLabelFormats: {
                    day: '%e %b',
                    week:'%e %b',
                    month: '%b',
                    year: '%Y'
                },
                type: 'datetime'    //datetime
            },
            yAxis: {
                title: {
                    text: ''
                },
                labels: {
                    enabled: true
                }
            },
	    legend: {
		enabled: false
	    },
            //tooltip: {
                //valueSuffix: ' Wh',
                //valueDecimals: 1
            //},

            plotOptions: {
                column: {
                    dataLabels: {
                        enabled: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y,1);
                        },
                        crop: false,
                        overflow: 'none',
                    },
                    enableMouseTracking: false
                }
            },

	    series: [{
		name: 'Wh',
		type: 'column',
		pointWidth: '<?php echo $anchocol;?>', //Ancho fijado de las columnas
		color: '<?php echo $colorbar;?>',
		//color: Highcharts.getOptions().colors[5],
		data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata1);$i++){
		   ?>
		   data.push([<?php echo $rawdata1[$i]["Fecha"];?>,<?php echo $rawdata1[$i]["Datos"];?>]);
                   <?php } ?>
		return data;
                     })()
		}]
	});
});


</script>

<?php
include ("pie.inc");
?>

