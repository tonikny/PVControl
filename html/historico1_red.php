<?php
$titulo = "Inicio";
include("cabecera.inc");


require('conexion.php');
//Coger datos grafica tiempo real


$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, Wred, Wplaca, Vbat * Ibat as Wbat, Wplaca-Wred-Vbat*Ibat as Wconsumo, LEAST(Wplaca,Wplaca-Wred) as Wautoconsumo
        FROM datos_c WHERE Tiempo >= (NOW()- INTERVAL 3 DAY)
        ORDER BY Tiempo";

if ($result = mysqli_query($link, $sql)) {

    $i = 0;
    while ($row = mysqli_fetch_assoc($result)) {
        //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
        $rawdata3[$i] = $row;
        $i++;
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
}

mysqli_close($link);

?>




<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery.js"></script>
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<script src="https://code.highcharts.com/themes/grid.js"></script>
<script src="https://code.highcharts.com/modules/legend.js"></script>
<script src="https://code.highcharts.com/modules/series-label.js"></script>


<div id="grafica_t_real" style="width: 100%; height: 280px; margin-left: 0%; margin-bottom: 0% ;float: left"></div>


<br>
<br style="clear:both;" />
<br>

<script>
    $(function () {

        recibirDatosFV();

        if (typeof color_rotulos == 'undefined') { color_rotulos = '#18F905' }; // Verde claro
        if (typeof t_refresco === 'undefined') { t_refresco = 3000};
        
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
                shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                rangeSelectorFrom: "Desde",
                rangeSelectorTo: "A",
                printChart: "Imprimir gráfico",
                loading: "Cargando..."
            }
        });

        grafica_t_real = new Highcharts.stockChart({
            chart: {
                renderTo: 'grafica_t_real',
				zoomType: 'x',
                type: 'area',
				panning: true,
                panKey: 'shift',
				
                fillOpacity: 0.2,
                backgroundColor: null,//'#ffffff',//'#f2f2f2',
                borderColor: null,
                plotBorderWidth: 1,

                alignTicks: false,
                animation: Highcharts.svg, // don't animate in old IE
                //marginRight: 10,
            },
            title: {
                text: '',
                floating: true,
                y: 12,
                x: -0
            },
            subtitle: {
                text: 'Prueba Dinamica',
                floating: true,
                align: 'right',
                verticalAlign: 'bottom',
                y: 25,
            },
            credits: {
                enabled: false
            },
                        
            xAxis: {
				dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
            },
           rangeSelector: {
                inputEnabled: false,  // Esto desactiva los inputs de fecha
                labelStyle: {
                    display: 'none'   // Esto oculta las etiquetas "Desde" y "A"
                },
                
                buttons: [{
                    type: 'hour',
                    count: 12,
                    text: '12h'
                }, {
                    type: 'day',
                    count: 1,
                    text: '1día'
                }, {
                    type: 'day',
                    count: 2,
                    text: '2días'
                }, {
                    type: 'all',
                    text: 'Todo'
                }],
                selected: 1
            },

			yAxis: [
                {// ########## Valores eje Wred #################
                    gridLineWith: 2,
                    //min: -5000,
                    //max: Escala_Wred_max,
                    opposite: true,
                    tickInterval: 50,
                    gridLineColor: 'transparent',
                    minorGridLineColor: 'transparent',
                    //endOnTick: true,
                    //maxPadding: 0.2,
                    //tickAmount: 7,
                    labels: {
                        //format: '{value} W',
                        style: {
                            color: Highcharts.getOptions().colors[2]
                        }
                    },
                    title: {
                        text: null,
                    },
                    //opposite: false,
                },
            ],

            tooltip: {
                crosshairs: true,
                shared: true,
                valueDecimals: 2
            },
            navigator: {
				enabled: false
            },
            plotOptions: {
                series: {
                    marker: {
                        enabled: false
                    }
                }
            },
            
            /*
            legend: {
                enabled: true,
                layout: 'horizontal',
                floating: true,
                align: 'left',
                verticalAlign: 'bottom',
                //x: -100,
                y: 20,
                borderWidth: 0
            },
            */
            
            legend: {
                enabled: true, // Asegurar que esté habilitada
                align: 'center',
                verticalAlign: 'bottom',
                layout: 'horizontal',
                x: 0,
                y: 0,
                floating: false,
                backgroundColor: 'rgba(255,255,255,0.8)',
                borderWidth: 1,
                borderColor: '#CCC'
            },

            series: [

                {   name: 'Wred',
                    yAxis: 0,
                    color: '#4C9FEC',
                    lineWidth: 1,
                    data: (function () {
                        var data = [];
                        <?php
                        for ($i = 0; $i < count($rawdata3); $i++) {
                        ?>
                        data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Wred"]; ?>]);
                        <?php } ?>
                    return data;
                    }) ()

                },

                {   name: 'WPlaca',
                    yAxis: 0,
                    color: '#FFA726',
                    lineWidth: 1,
                    data: (function () {
                        var data = [];
                        <?php
                        for ($i = 0; $i < count($rawdata3); $i++) {
                        ?>
                        data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Wplaca"]; ?>]);
                        <?php } ?>
                    return data;
                    }) ()

                },

                {   name: 'Wbat',
                    yAxis: 0,
                    color: '#66BB6A',
                    lineWidth: 1,
                    data: (function () {
                        var data = [];
                        <?php
                        for ($i = 0; $i < count($rawdata3); $i++) {
                        ?>
                        data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Wbat"]; ?>]);
                        <?php } ?>
                    return data;
                    }) ()

                },

                {   name: 'Consumo',
                    yAxis: 0,
                    color: '#EF5350',
                    lineWidth: 1,
                    data: (function () {
                        var data = [];
                        <?php
                        for ($i = 0; $i < count($rawdata3); $i++) {
                        ?>
                        data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Wconsumo"]; ?>]);
                        <?php } ?>
                    return data;
                    })()
                },

                {   name: 'Autoconsumo',
				    visible: false,
                    yAxis: 0,
                    color: '#FFEB3B',
                    lineWidth: 1,
                    data: (function () {
                        var data = [];
                        <?php
                        for ($i = 0; $i < count($rawdata3); $i++) {
                        ?>
                        data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Wautoconsumo"]; ?>]);
                        <?php } ?>
                    return data;
                    })()
                },          
            ]
      });


    function recibirDatosFV() {
        $.ajax({
            url: 'datos_fv.php',
            success: function (data) {
                try {
                    //console.log(data);              
                    fecha = data['FV']['tiempo'];


                    //Wconsumo, Wh_consumo
					Wplaca = data['FV']['Wplaca'];
                    Wconsumo = data['FV']['Wconsumo'];
                    Wh_consumo = data['FV']['Wh_consumo'];
                    Wautoconsumo = Math.min(Wplaca, Wconsumo);
					Wred = data['FV']['Wred'];
					Wbat = data['FV']['Vbat'] * data['FV']['Ibat'];
					

                    //console.log(Wconsumo, Wh_consumo, Wautoconsumo);
                    
					// Actualizacion Grafica a tiempo real
                    grafica_t_real.setTitle({
                        text: 'Fecha: ' + fecha
                    });
                    grafica_t_real.setSubtitle({
                        text: 'Excedente=' + Wred.toFixed(2)
                    });

                    x = (new Date()).getTime(); // current time
                    
					grafica_t_real.series[0].addPoint([x, Wred], true, true); //Wplaca
                    grafica_t_real.series[1].addPoint([x, Wplaca], true, true); //Wplaca
					grafica_t_real.series[2].addPoint([x, Wbat], true, true); //Wplaca
                    grafica_t_real.series[3].addPoint([x, Wconsumo], true, true); //Wconsumo
                    grafica_t_real.series[4].addPoint([x, Wautoconsumo], true, true); //Wautoconsumo



                    //console.log(data)

                    //setTimeout(recibirDatosFV, 3000);
                }

                catch (e) {
                    var d = new Date();
                    s = d.getSeconds()
                    t = d.getHours() + ':' + d.getMinutes() + ':' + s;

                 
                    grafica_t_real.setTitle({
                        text: 'SIN RESPUESTA - Hora=' + t,
                    });

                }
            },

            // código a ejecutar sin importar si falla o no la petición
            complete: function (xhr, status) {
                //setTimeout(recibirDatosFV, t_refresco);
				setTimeout(recibirDatosFV, 300000);
            },

            cache: false
        });
    }

    function round(value, precision) {
        var multiplier = Math.pow(10, precision || 0);
        return Math.round(value * multiplier) / multiplier;
    }

});

</script>

<?php
include("pie.inc");
?>
