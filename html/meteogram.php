<?php
include ("cabecera.inc");

$municipio = "Els Hostalets de Pierola";
$codigo_aemet = "hostalets-de-pierola-els-id08162";
$latitud = "41.543424";
$longitud = "1.812539";
?>

<h1 style="text-align: center"><?php echo $municipio; ?></h1>

<link href="http://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css" rel="stylesheet">

<!-- Grafico B -->
<iframe width="600" height="400" src="https://embed.windy.com/embed2.html?lat=<?php echo $latitud; ?>&lon=<?php echo $longitud; ?>&zoom=5&level=surface&overlay=clouds&menu=&message=true&marker=true&calendar=&pressure=true&type=map&location=coordinates&detail=true&detailLat=<?php echo $latitud; ?>&detailLon=<?php echo $longitud; ?>&metricWind=default&metricTemp=default&radarRange=-1" frameborder="1"></iframe>

<iframe width="600" height="400" src="https://embed.windy.com/embed2.html?lat=<?php echo $latitud; ?>&lon=<?php echo $longitud; ?>&zoom=4&level=surface&overlay=clouds&menu=&message=true&marker=true&calendar=&pressure=true&type=map&location=coordinates&detail=&detailLat=<?php echo $latitud; ?>&detailLon=<?php echo $longitud; ?>&metricWind=default&metricTemp=default&radarRange=-1" frameborder="1"></iframe>

<!-- Grafico A 
<div id="tyt_wdgt_1512176376814" style="overflow:hidden;width:500px;height:317px;float: left" data-options="color=azul&text=&content=1111000&temp_unit=c&wind_unit=kmh">
<script src="http://tiempoytemperatura.es/widgets/js/biggest-6day/3108060/tyt_wdgt_1512176376814/?v=0"></script>
</div>
-->

<!-- Grafico AEMET -->
<script type='text/javascript' 
src="http://www.aemet.es/es/eltiempo/prediccion/municipios/launchwidget/<?php echo $codigo_aemet; ?>">
</script>

<noscript><a target='_blank' style='font-weight: bold;font-size: 1.20em;' href='http://www.aemet.es/es/eltiempo/prediccion/municipios/hostalets-de-pierola-els-id08162'>
El Tiempo. predicción de la AEMET para <?php echo $municipio; ?></a>
</noscript>

<!-- Grafico tiempo.com
<div id="cont_01e7bd88df44d8bc0c5a0eaa2fc9f061" style="overflow:hidden;width:500px;height:317px;float: right">
<script type="text/javascript" async src="https://www.tiempo.com/wid_loader/01e7bd88df44d8bc0c5a0eaa2fc9f061"></script>
</div>
--> 

<!-- Grafico eltiempo.es 
<div id="c_a0a84bca4cb50feab7b496631356390e" class="completo; float: left">
<script type="text/javascript" src="https://www.eltiempo.es/widget/widget_loader/a0a84bca4cb50feab7b496631356390e"></script>
</div>
-->

<?php
include ("pie.inc");
?>
