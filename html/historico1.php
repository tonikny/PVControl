<?php
$titulo="Historico 1 Dia";
include ("cabecera.inc");

require('conexion.php');

//Coger datos grafica historico general
$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, SOC, Ibat, Iplaca, Vbat, Vplaca, PWM, Wplaca,Vred, Wred, Temp,
          Wplaca - Vbat*Ibat - Wred as Wconsumo,
          Wh_placa/1000 as Kwh_placa, (Whp_bat-Whn_bat)/1000 as Kwh_bat,(Whp_red-Whn_red)/1000 as Kwh_red,
          (Wh_placa - Whp_bat + Whn_bat - Whp_red + Whn_red)/1000 as Kwh_consumo,
          Mod_bat * 1 as Modo, Aux1, Aux2
        FROM datos WHERE Tiempo >= (NOW()- INTERVAL 25 HOUR)
        ORDER BY Tiempo";

if($result = mysqli_query($link, $sql)){

  $i=0;
  while($row = mysqli_fetch_assoc($result)) {
        //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
        $rawdata[$i] = $row;
        $i++;
  }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

mysqli_close($link);

?>


<!-- Importo el archivo Javascript de Highcharts directamente desde la RPi 
<script src="js/jquery.js"></script>
<script src="js/stock/highstock.js"></script>
<script src="js/highcharts-more.js"></script>

<script src="js/themes/grid.js"></script>
-->


<!-- Importo el archivo Javascript directamente desde la webr -->
<!---->

<script src="https://code.jquery.com/jquery.js"></script>
<script src="http://code.highcharts.com/stock/highstock.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>

<!--
<div id="container12" style="width: auto; height: 600px; margin-left: 5;margin-right:5"></div>
-->
<div id="container12" style="width: 100%; height: 80vh; margin-left: 5; float: left"></div>

<br>


<script>
$(function () 
 {

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
      printChart: "Imprimir gráfico",
      loading: "Cargando..."
      }
    });

  var char = new Highcharts.StockChart ({
    chart: {
      renderTo: 'container12',
      zoomType: 'xy',
      alignTicks: false,
      panning: true,
      panKey: 'shift'
      },
    //title: {
    //  text: 'Grafica Diaria -- 1 DIA'
    //  },
    //subtitle: {
    //  text: 'Permite Zoom XY'
    //  },
    credits: {
      enabled: false
      },
    yAxis: [
     {// ########## 0 - Valores eje Intensidad ######################
      visible: Eje_Intensidad,
      opposite: false,
      min: Escala_intensidad_min,
      max: Escala_intensidad_max,
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
        text: 'Ibat',
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
     
     {// ########## 1 - Valores eje Vbat ######################
      visible: Eje_Vbat,
      opposite: false,
      min: Escala_Vbat_min,
      max: Escala_Vbat_max,
      tickInterval: 1,
      //gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Vbat',
        rotation: 0,
        y: -10
        },
      plotLines: [{
        // ########## Valores Linea Vabs #####################
        value: Vabs,
        width: 2,
        color: 'green',
        dashStyle: 'shortdash',
        label: {
          text: 'Vabs'
          }
       },{
        
        // ########## Valores Linea Vflot ######################
        value: Vflot,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
          text: 'Vflot'
          }
       }]
     },
     
     {// ########## 2 - Valores eje SOC ######################
      visible: Eje_SOC,
      opposite: true,
      min: 20,
      max: 100 ,
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
        text: 'SOC',
        rotation: 0,
        y: -10
        },
      plotLines: [{
        value: 100,
        width: 2,
        color: 'green',
        dashStyle: 'shortdash',
        label: {
          text: '100%'
          }
       },{
        value: 80,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
          text: '80%'
          }
       }]
      },
      
     {// ########## 3 - Valores eje PWM ######################
      visible: Eje_PWM,
      opposite: true,
      min: 0,
      max: Escala_PWM_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'PWM',
        rotation: 0,
        y: -10
        },
                  
     },
      
     {// ########## 4 - Valores eje Vplaca ######################
      visible: Eje_Vplaca,
      opposite: false,
      min: 0,
      max: Escala_Vplaca_max,
      tickInterval: 20,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      title: {
        align: 'high',
        offset: 0,
        text: 'Vplaca',
        rotation: 0,
        y: -5
        },
      },
   
     {// ########## 5 - Valores eje Wplaca, Wred, Wconsumo #################
      visible: Eje_Wplaca,
      opposite: true,
      min: Escala_Wred_min,
      max: Escala_Wred_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Wplaca',
        rotation: 0,
        y: -10
        },
      },
            
     
     {// ########## 6 - Valores eje Vred ######################
      visible: Eje_Vred,
      opposite: true,
      min: Escala_Vred_min,
      max: Escala_Vred_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Vred',
        rotation: 0,
        y: -10
        },
      },
          
     {// ########## 7 - Valores eje Kwh_placa ######################
      visible: Eje_Kwh_placa,
      opposite: true,
      min: 0,
      max: Kwh_placa_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Kwh_placa',
        rotation: 0,
        y: -10
        },
      },
  
     {// ########## 8 - Valores eje Kwh_bat ######################
      visible: Eje_Kwh_bat,
      opposite: true,
      min: Kwh_bat_min,
      max: Kwh_bat_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Kwh_bat',
        rotation: 0,
        y: -10
        },
      },
            
     {// ########## 9 - Valores eje Kwh_red ######################
      visible: Eje_Kwh_red,
      opposite: true,
      min: Kwh_red_min,
      max: Kwh_red_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Kwh_red',
        rotation: 0,
        y: -10
        },
      },
   
     {// ########## 10 - Valores eje Kwh_consumo ######################
      visible: Eje_Kwh_consumo,
      opposite: true,
      min: Kwh_consumo_min,
      max: Kwh_consumo_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Kwh_consumo',
        rotation: 0,
        y: -10
        },
      },
     
     {// ########## 11 - Valores eje Temp ######################
      visible: Eje_Temp,
      opposite: true,
      min: Temp_min,
      max: Temp_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Temp',
        rotation: 0,
        y: -10
        },
      },
     
     {// ########## 12 - Valores eje Modo ######################
      visible: Eje_Modo,
      opposite: true,
      min: 2,
      max: Modo_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Temp',
        rotation: 0,
        y: -10
        },
      },
    
     {// ########## 13 - Valores eje Aux1  ######################
      visible: Eje_Aux1,
      opposite: true,
      min: Aux1_min,
      max: Aux1_max,
      tickInterval: 1,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      title: {
        align: 'high',
        offset: 0,
        text: Nombre_Aux1, 
        rotation: 0,
        y: -5
        },
      },
    
     {// ########## 14 - Valores eje Aux2  ######################
      visible: Eje_Aux2,
      opposite: true,
      min: Aux2_min,
      max: Aux2_max,
      tickInterval: 1,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      title: {
        align: 'high',
        offset: 0,
        text: Nombre_Aux2,
        rotation: 0,
        y: -5
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
        count: 6,
        text: '6h'
       }, {
        type: 'hour',
        count: 12,
        text: '12h'
       }, {
        type: 'day',
        count: 1,
        text: '1día'
       }, {
        type: 'all',
        text: 'Todo'
       }],
      selected: 1
      },
    tooltip: {
      split: true,
      distance: 30,
      padding: 1,
      outside: true,
      shared: true,
      valueDecimals: 2
      },
    navigator: {
      enabled: true // false
      },
    series: [
     {name: 'Ibat',
      type: 'spline',
      visible: Ibat_visible,
      color: Highcharts.getOptions().colors[2],
      tooltip: {
        valueSuffix: ' A',
        valueDecimals: 1,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Ibat"];?>]);
            <?php } ?>
          return data;
        })()
     },
     {name: 'Iplaca',
      type: 'spline',
      visible: Iplaca_visible,
      color: Highcharts.getOptions().colors[3],
      tooltip: {
        valueSuffix: ' A',
        valueDecimals: 1,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Iplaca"];?>]);
            <?php } ?>
          return data;
        })()
     },
     {name: 'Vbat',
      type: 'spline',
      visible: Vbat_visible,
      yAxis: 1,
      color: Highcharts.getOptions().colors[0],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vbat"];?>]);
            <?php } ?>
          return data;
        })()
     },
     {name: 'SOC',
      type: 'spline',
      visible: SOC_visible,
      yAxis: 2,
      color: Highcharts.getOptions().colors[1],
      tooltip: {
        valueSuffix: ' %',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
              data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["SOC"];?>]);
              <?php } ?>
            return data;
        })()
     },
     {name: 'PWM',
      type: 'spline',
      visible: PWM_visible,
      yAxis: 3,
      color: Highcharts.getOptions().colors[5],
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["PWM"];?>]);
          <?php } ?>
        return data;
        })()  
        
     },
     {name: 'Vplaca',
      type: 'spline',
      visible: Vplaca_visible,
      yAxis: 4,
      color: '#632D2D', //Highcharts.getOptions().colors[20],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vplaca"];?>]);
          <?php } ?>
        return data;
        })()
     },   
     {name: 'Wplaca',
      type: 'spline',
      visible: Wplaca_visible,
      yAxis: 5,
      color: '#E55FE5',
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Wplaca"];?>]);
          <?php } ?>
        return data;
        })()
      },     
     {name: 'Wred',
      type: 'spline',
      visible: Wred_visible,
      yAxis: 5,
      color: '#D882C9',
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Wred"];?>]);
          <?php } ?>
        return data;
        })()
      },             
     {name: 'Wconsumo',
      type: 'spline',
      visible: Wconsumo_visible,
      yAxis: 5,
      color: '#F39610',
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Wconsumo"];?>]);
          <?php } ?>
        return data;
        })()
      },         
     
     {name: 'Vred',
      type: 'spline',
      visible: Vred_visible,
      yAxis: 6,
      color: '#C55FE5',
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vred"];?>]);
          <?php } ?>
        return data;
        })()
      },     

     {name: 'Kwh_placa',
      type: 'area',
      visible: Kwh_placa_visible,
      yAxis: 7,
      fillOpacity: 0.2,
      color: "#E55FE5",
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Kwh_placa"];?>]);
          <?php } ?>
        return data;
        })()
      },     
     {name: 'Kwh_bat',
      type: 'area',
      visible: Kwh_bat_visible,
      yAxis: 8,
      fillOpacity: 0.2,
      color: "#7C75D7",
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Kwh_bat"];?>]);
          <?php } ?>
        return data;
        })()
      },     
     {name: 'Kwh_red',
      type: 'area',
      visible: Kwh_red_visible,
      yAxis: 9,
      fillOpacity: 0.2,
      color: "#D882C9",
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Kwh_red"];?>]);
          <?php } ?>
        return data;
        })()
      },
     {name: 'Kwh_consumo',
      type: 'area',
      visible: Kwh_consumo_visible,
      yAxis: 10,
      fillOpacity: 0.2,
      color: "#F39610",
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Kwh_consumo"];?>]);
          <?php } ?>
        return data;
        })()
      },
  
     {name: 'Temp',
      type: 'spline',
      visible: Temp_visible,
      yAxis: 11,
      color: 'black',
      tooltip: {
        valueSuffix: ' ºC',
        valueDecimals: 1,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Temp"];?>]);
          <?php } ?>
        return data;
        })()
      },
     
     {name: 'Modo',
      type: 'spline',
      visible: Modo_visible,
      yAxis: 12,
      color: '#1604FA',
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Modo"];?>]);
          <?php } ?>
        return data;
        })()
      },
       
     {name: Nombre_Aux1,
      type: 'spline',
      visible: Aux1_visible,
      yAxis: 13,
      color: Highcharts.getOptions().colors[6],
      tooltip: {
        valueSuffix: Unidades_Aux1,
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Aux1"];?>]);
          <?php } ?>
        return data;
        })()
      },     
     {name: Nombre_Aux2,
      type: 'spline',
      visible: Aux2_visible,
      yAxis: 14,
      color: Highcharts.getOptions().colors[8],
      tooltip: {
        valueSuffix: Unidades_Aux2,
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Aux2"];?>]);
          <?php } ?>
        return data;
        })()
      },
          
    ]
    });
  });
</script>

<?php
include ("pie.inc");
?>
