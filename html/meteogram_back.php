<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body>

<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
<script src="http://code.highcharts.com/highcharts.js"></script>
<link href="http://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css" rel="stylesheet">

<!-- Grafico B -->
<iframe width="600" height="400" src="https://embed.windy.com/embed2.html?lat=40.13751&lon=-3.530851&zoom=5&level=surface&overlay=clouds&menu=&message=true&marker=true&calendar=&pressure=true&type=map&location=coordinates&detail=true&detailLat=40.13751&detailLon=-3.530851&metricWind=default&metricTemp=default&radarRange=-1" frameborder="0"></iframe>


<iframe width="600" height="400" src="https://embed.windy.com/embed2.html?lat=40.13751&lon=-3.530851&zoom=4&level=surface&overlay=clouds&menu=&message=&marker=&calendar=&pressure=&type=map&location=coordinates&detail=&detailLat=40.13751&detailLon=-3.530851&metricWind=default&metricTemp=default&radarRange=-1" frameborder="0"></iframe>

<!-- Grafico A 
<div id="tyt_wdgt_1512176376814" style="overflow:hidden;width:500px;height:317px;float: left" data-options="color=azul&text=&content=1111000&temp_unit=c&wind_unit=kmh">
<script src="http://tiempoytemperatura.es/widgets/js/biggest-6day/3108060/tyt_wdgt_1512176376814/?v=0"></script>
</div>
-->

<!-- Grafico AEMET -->
<script type='text/javascript' 
src='http://www.aemet.es/es/eltiempo/prediccion/municipios/launchwidget/titulcia-id28147?w=g4p01111001ohmffffffw898z224x4f86d9t95b6e9r1s8n2'>
</script>
<noscript><a target='_blank' style='font-weight: bold;font-size: 1.20em;' href='http://www.aemet.es/es/eltiempo/prediccion/municipios/titulcia-id28147'>
El Tiempo. Consulte la predicción de la AEMET para Titulcia</a>
</noscript>



<!-- Grafico HC -->
<div id="container" style="width: 800px; height: 270px; float:center; margin: auto ">
        <div style="margin-top: 0px; text-align: center" id="loading">
                <i class="fa fa-spinner fa-spin"></i> Cargando datos desde una fuente externa
        </div>
</div>

<div style="margin: 0 auto; width:100%; height:300px;">
    <object type="text/html" data="meteogram_w.php"
            style="width:100%; height:100%; margin:0%;">
    </object>
</div>

<!-- Camara Valdemoro 
<a name="lkr-timelapse" data-id="1399316319" data-play="day" href="https://lookr.com/es/lookout/1399316319-Valdemoro#action-play-day" target="_blank">Valdemoro: 24 horas</a>
<script async type="text/javascript" src="https://api.lookr.com/link/script/timelapse.js"></script>
-->

<!-- tiempoytemperatura
<div id="tyt_wdgt_1512429681817" style="overflow:hidden;width:500px;height:340px;float: left" data-options="color=azul&text=&content=1111100&temp_unit=c&wind_unit=kmh">
<script src="http://tiempoytemperatura.es/widgets/js/biggest-6day/3108060/tyt_wdgt_1512429681817/?v=0"></script>
</div>
 -->




<!-- Grafico tiempo.com--> 
<div id="cont_01e7bd88df44d8bc0c5a0eaa2fc9f061" style="overflow:hidden;width:500px;height:317px;float: right">
<script type="text/javascript" async src="https://www.tiempo.com/wid_loader/01e7bd88df44d8bc0c5a0eaa2fc9f061"></script>
</div>


<!-- Grafico eltiempo.es 
<div id="c_a0a84bca4cb50feab7b496631356390e" class="completo; float: left">
<script type="text/javascript" src="https://www.eltiempo.es/widget/widget_loader/a0a84bca4cb50feab7b496631356390e"></script>
</div>
-->
<script type="text/javascript">

function Meteogram(xml, container) {
    // Parallel arrays for the chart data, these are populated as the XML/JSON file 
    // is loaded
    this.symbols = [];
    this.symbolNames = [];
    this.precipitations = [];
    this.windDirections = [];
    this.windDirectionNames = [];
    this.windSpeeds = [];
    this.windSpeedNames = [];
    this.temperatures = [];
    this.pressures = [];

    // Initialize
    this.xml = xml;
    this.container = container;

    // Run
    this.parseYrData();
}
/**
 * Return weather symbol sprites as laid out at http://om.yr.no/forklaring/symbol/
 */
Meteogram.prototype.getSymbolSprites = function (symbolSize) {
    return {
        '01d': {
            x: 0,
            y: 0
        },
        '01n': {
            x: symbolSize,
            y: 0
        },
        '16': {
            x: 2 * symbolSize,
            y: 0
        },
        '02d': {
            x: 0,
            y: symbolSize
        },
        '02n': {
            x: symbolSize,
            y: symbolSize
        },
        '03d': {
            x: 0,
            y: 2 * symbolSize
        },
        '03n': {
            x: symbolSize,
            y: 2 * symbolSize
        },
        '17': {
            x: 2 * symbolSize,
            y: 2 * symbolSize
        },
        '04': {
            x: 0,
            y: 3 * symbolSize
        },
        '05d': {
            x: 0,
            y: 4 * symbolSize
        },
        '05n': {
            x: symbolSize,
            y: 4 * symbolSize
        },
        '18': {
            x: 2 * symbolSize,
            y: 4 * symbolSize
        },
        '06d': {
            x: 0,
            y: 5 * symbolSize
        },
        '06n': {
            x: symbolSize,
            y: 5 * symbolSize
        },
        '07d': {
            x: 0,
            y: 6 * symbolSize
        },
        '07n': {
            x: symbolSize,
            y: 6 * symbolSize
        },
        '08d': {
            x: 0,
            y: 7 * symbolSize
        },
        '08n': {
            x: symbolSize,
            y: 7 * symbolSize
        },
        '19': {
            x: 2 * symbolSize,
            y: 7 * symbolSize
        },
        '09': {
            x: 0,
            y: 8 * symbolSize
        },
        '10': {
            x: 0,
            y: 9 * symbolSize
        },
        '11': {
            x: 0,
            y: 10 * symbolSize
        },
        '12': {
            x: 0,
            y: 11 * symbolSize
        },
        '13': {
            x: 0,
            y: 12 * symbolSize
        },
        '14': {
            x: 0,
            y: 13 * symbolSize
        },
        '15': {
            x: 0,
            y: 14 * symbolSize
        },
        '20d': {
            x: 0,
            y: 15 * symbolSize
        },
        '20n': {
            x: symbolSize,
            y: 15 * symbolSize
        },
        '20m': {
            x: 2 * symbolSize,
            y: 15 * symbolSize
        },
        '21d': {
            x: 0,
            y: 16 * symbolSize
        },
        '21n': {
            x: symbolSize,
            y: 16 * symbolSize
        },
        '21m': {
            x: 2 * symbolSize,
            y: 16 * symbolSize
        },
        '22': {
            x: 0,
            y: 17 * symbolSize
        },
        '23': {
            x: 0,
            y: 18 * symbolSize
        }
    };
};


/**
 * Function to smooth the temperature line. The original data provides only whole degrees,
 * which makes the line graph look jagged. So we apply a running mean on it, but preserve
 * the unaltered value in the tooltip.
 */
Meteogram.prototype.smoothLine = function (data) {
    var i = data.length,
        sum,
        value;
    while (i--) {
        data[i].value = value = data[i].y; // preserve value for tooltip

        // Set the smoothed value to the average of the closest points, but don't allow
        // it to differ more than 0.5 degrees from the given value
        sum = (data[i - 1] || data[i]).y + value + (data[i + 1] || data[i]).y;
        data[i].y = Math.max(value - 0.5, Math.min(sum / 3, value + 0.5));
    }
};

/**
 * Callback function that is called from Highcharts on hovering each point and returns
 * HTML for the tooltip.
 */
Meteogram.prototype.tooltipFormatter = function (tooltip) {

    // Create the header with reference to the time interval
    var index = tooltip.points[0].point.index,
        ret = '<small>' + Highcharts.dateFormat('%A, %b %e, %H:%M', tooltip.x) + '-' +
            Highcharts.dateFormat('%H:%M', tooltip.points[0].point.to) + '</small><br>';

    // Cielo
    if (this.symbolNames[index] == 'Clear sky') {
        this.symbolNames[index] = 'Despejado';
    }
    if (this.symbolNames[index] == 'Fair') {
        this.symbolNames[index] = 'Claro';
    }
    if (this.symbolNames[index] == 'Partly cloudy') {
        this.symbolNames[index] = 'Parcialmente nuboso';
    }
    if (this.symbolNames[index] == 'Cloudy') {
        this.symbolNames[index] = 'Nuboso';
    }
    if (this.symbolNames[index] == 'Light rain showers') {
        this.symbolNames[index] = 'Chubascos ligeros';
    }
    if (this.symbolNames[index] == 'Rain showers') {
        this.symbolNames[index] = 'Chubascos';
    }
    if (this.symbolNames[index] == 'Heavy rain showers') {
        this.symbolNames[index] = 'Fuertes chubascos';
    }
    if (this.symbolNames[index] == 'Light rain showers and thunder') {
        this.symbolNames[index] = 'Chubascos ligeros con tormentas';
    }
    if (this.symbolNames[index] == 'Rain showers and thunder') {
        this.symbolNames[index] = 'Chubascos con tormentas';
    }
    if (this.symbolNames[index] == 'Heavy rain showers and thunder') {
        this.symbolNames[index] = 'Fuertes chubascos con tormentas';
    }
    if (this.symbolNames[index] == 'Light sleet showers') {
        this.symbolNames[index] = 'Chubascos ligeros de aguanieve';
    }
    if (this.symbolNames[index] == 'Sleet showers') {
        this.symbolNames[index] = 'Chubascos de aguanieve';
    }
    if (this.symbolNames[index] == 'Heavy sleet showers') {
        this.symbolNames[index] = 'Fuertes chubascos de aguanieve';
    }
    if (this.symbolNames[index] == 'Light sleet showers and thunder') {
        this.symbolNames[index] = 'Chubascos ligeros de aguanieve con tormentas';
    }
    if (this.symbolNames[index] == 'Sleet showers and thunder') {
        this.symbolNames[index] = 'Chubascos de aguanieve con tormentas';
    }
    if (this.symbolNames[index] == 'Heavy sleet showers and thunder') {
        this.symbolNames[index] = 'Fuertes chubascos de aguanieve con tormentas';
    }
    if (this.symbolNames[index] == 'Light snow showers') {
        this.symbolNames[index] = 'Chubasco ligero de nieve';
    }
    if (this.symbolNames[index] == 'Snow showers') {
        this.symbolNames[index] = 'Chubascos de nieve';
    }
    if (this.symbolNames[index] == 'Heavy snow showers') {
        this.symbolNames[index] = 'Fuertes chubascos de nieve';
    }
    if (this.symbolNames[index] == 'Light snow showers and thunder') {
        this.symbolNames[index] = 'Chubasco ligero de nieve con tormentas';
    }
    if (this.symbolNames[index] == 'Snow showers and thunder') {
        this.symbolNames[index] = 'Chubascos de nieve con tormentas';
    }
    if (this.symbolNames[index] == 'Heavy snow showers and thunder') {
        this.symbolNames[index] = 'Fuertes chubascos de nieve con tormentas';
    }
    if (this.symbolNames[index] == 'Light rain') {
        this.symbolNames[index] = 'Lluvia fina';
    }
    if (this.symbolNames[index] == 'Rain') {
        this.symbolNames[index] = 'Lluvia';
    }
    if (this.symbolNames[index] == 'Heavy rain') {
        this.symbolNames[index] = 'Fuertes lluvias';
    }
    if (this.symbolNames[index] == 'Light rain and thunder') {
        this.symbolNames[index] = 'Lluvia fina con tormentas';
    }
    if (this.symbolNames[index] == 'Rain and thunder') {
        this.symbolNames[index] = 'Lluvia con tormentas';
    }
    if (this.symbolNames[index] == 'Heavy rain and thunder') {
        this.symbolNames[index] = 'Fuertes lluvias con tormentas';
    }
    if (this.symbolNames[index] == 'Light sleet') {
        this.symbolNames[index] = 'Ligera aguanieve';
    }
    if (this.symbolNames[index] == 'Sleet') {
        this.symbolNames[index] = 'Aguanieve';
    }
    if (this.symbolNames[index] == 'Heavy sleet') {
        this.symbolNames[index] = 'Fuerte aguanieve';
    }
    if (this.symbolNames[index] == 'Light sleet and thunder') {
        this.symbolNames[index] = 'Ligera aguanieve con tormentas';
    }
    if (this.symbolNames[index] == 'Sleet and thunder') {
        this.symbolNames[index] = 'Aguanieve con tormentas';
    }
    if (this.symbolNames[index] == 'Heavy sleet and thunder') {
        this.symbolNames[index] = 'Fuerte aguanieve con tormentas';
    }
    if (this.symbolNames[index] == 'Light snow') {
        this.symbolNames[index] = 'Nieve ligera';
    }
    if (this.symbolNames[index] == 'Snow') {
        this.symbolNames[index] = 'Nieve';
    }
    if (this.symbolNames[index] == 'Heavy snow') {
        this.symbolNames[index] = 'Fuertes nevadas';
    }
    if (this.symbolNames[index] == 'Light snow and thunder') {
        this.symbolNames[index] = 'Nieve ligera con tormentas';
    }
    if (this.symbolNames[index] == 'Snow and thunder') {
        this.symbolNames[index] = 'Nieve con tormentas';
    }
    if (this.symbolNames[index] == 'Heavy snow and thunder') {
        this.symbolNames[index] = 'Fuertes nevadas con tormentas';
    }
    if (this.symbolNames[index] == 'Fog') {
        this.symbolNames[index] = 'Niebla';
    }


    // Nombres de los vientos segun velocidad
    if (this.windSpeedNames[index] == 'Calm') {
        this.windSpeedNames[index] = 'Calma';
    }
    if (this.windSpeedNames[index] == 'Light air') {
        this.windSpeedNames[index] = 'Brisa suave';
    }
    if (this.windSpeedNames[index] == 'Light breeze') {
        this.windSpeedNames[index] = 'Brisa muy débil';
    }
    if (this.windSpeedNames[index] == 'Gentle breeze') {
        this.windSpeedNames[index] = 'Brisa débil';
    }
    if (this.windSpeedNames[index] == 'Moderate breeze') {
        this.windSpeedNames[index] = 'Brisa moderada';
    }
    if (this.windSpeedNames[index] == 'Fresh breeze') {
        this.windSpeedNames[index] = 'Brisa fresca';
    }
    if (this.windSpeedNames[index] == 'Strong breeze') {
        this.windSpeedNames[index] = 'Frisa fuerte';
    }
    if (this.windSpeedNames[index] == 'Near gale') {
        this.windSpeedNames[index] = 'Viento fuerte';
    }
    if (this.windSpeedNames[index] == 'Gale') {
        this.windSpeedNames[index] = 'Galerna';
    }
    if (this.windSpeedNames[index] == 'Strong gale') {
        this.windSpeedNames[index] = 'Galerna fuerte';
    }
    if (this.windSpeedNames[index] == 'Storm') {
        this.windSpeedNames[index] = 'Tormenta';
    }
    if (this.windSpeedNames[index] == 'Violent storm') {
        this.windSpeedNames[index] = 'Tormenta violenta';
    }
    if (this.windSpeedNames[index] == 'Hurricane') {
        this.windSpeedNames[index] = 'Huracán';
    }

    // Direcciones de los vientos
    if (this.windDirectionNames[index] == 'North') {
        this.windDirectionNames[index] = 'Norte';
    }
    if (this.windDirectionNames[index] == 'Northeast') {
        this.windDirectionNames[index] = 'Noreste';
    }
    if (this.windDirectionNames[index] == 'East') {
        this.windDirectionNames[index] = 'Este';
    }
    if (this.windDirectionNames[index] == 'Southeast') {
        this.windDirectionNames[index] = 'Sureste';
    }
    if (this.windDirectionNames[index] == 'South') {
        this.windDirectionNames[index] = 'Sur';
    }
    if (this.windDirectionNames[index] == 'Southwest') {
        this.windDirectionNames[index] = 'Suroeste';
    }
    if (this.windDirectionNames[index] == 'West') {
        this.windDirectionNames[index] = 'Oeste';
    }
    if (this.windDirectionNames[index] == 'Northwest') {
        this.windDirectionNames[index] = 'Noroeste';
    }
    if (this.windDirectionNames[index] == 'North-northeast') {
        this.windDirectionNames[index] = 'Nornoreste';
    }
    if (this.windDirectionNames[index] == 'North-northwest') {
        this.windDirectionNames[index] = 'Nornoroeste';
    }
    if (this.windDirectionNames[index] == 'East-northeast') {
        this.windDirectionNames[index] = 'Estenoreste';
    }
    if (this.windDirectionNames[index] == 'East-southeast') {
        this.windDirectionNames[index] = 'Estesureste';
    }
    if (this.windDirectionNames[index] == 'South-southeast') {
        this.windDirectionNames[index] = 'Sursureste';
    }
    if (this.windDirectionNames[index] == 'South-southwest') {
        this.windDirectionNames[index] = 'Sursuroeste';
    }
    if (this.windDirectionNames[index] == 'West-northwest') {
        this.windDirectionNames[index] = 'Oesnoroeste';
    }
    if (this.windDirectionNames[index] == 'West-southwest') {
        this.windDirectionNames[index] = 'Oesuroeste';
    }


    // Symbol text
    ret += '<b>' + this.symbolNames[index] + '</b>';

    ret += '<table>';

    // Add all series
    Highcharts.each(tooltip.points, function (point) {
        var series = point.series;
        ret += '<tr><td><span style="color:' + series.color + '">\u25CF</span> ' + series.name +
            ': </td><td style="white-space:nowrap">' + Highcharts.pick(point.point.value, point.y) +
            series.options.tooltip.valueSuffix + '</td></tr>';
    });

    // Add wind
    ret += '<tr><td style="vertical-align: top">\u25CF Viento:</td><td style="white-space:nowrap">' + this.windDirectionNames[index] +
        '<br>' + this.windSpeedNames[index] + ' (' +
        Highcharts.numberFormat(this.windSpeeds[index], 1) + ' m/s)</td></tr>';

    // Close
    ret += '</table>';


    return ret;
};

/**
 * Draw the weather symbols on top of the temperature series. The symbols are sprites of a single
 * file, defined in the getSymbolSprites function above.
 */
Meteogram.prototype.drawWeatherSymbols = function (chart) {
    var meteogram = this,
        symbolSprites = this.getSymbolSprites(30);

    $.each(chart.series[0].data, function(i, point) {
        var sprite,
            group;

        if (meteogram.resolution > 36e5 || i % 2 === 0) {

            sprite = symbolSprites[meteogram.symbols[i]];
            if (sprite) {

                // Create a group element that is positioned and clipped at 30 pixels width and height
                group = chart.renderer.g()
                    .attr({
                        translateX: point.plotX + chart.plotLeft - 15,
                        translateY: point.plotY + chart.plotTop - 30,
                        zIndex: 5
                    })
                    .clip(chart.renderer.clipRect(0, 0, 30, 30))
                    .add();

                // Position the image inside it at the sprite position
                chart.renderer.image(
                    'http://www.highcharts.com/samples/graphics/meteogram-symbols-30px.png',
                    -sprite.x,
                    -sprite.y,
                    90,
                    570
                )
                    .add(group);
            }
        }
    });
};

/**
 * Create wind speed symbols for the Beaufort wind scale. The symbols are rotated
 * around the zero centerpoint.
 */
Meteogram.prototype.windArrow = function (name) {
    var level,
        path;

    // The stem and the arrow head
    path = [
        'M', 0, 7, // base of arrow
        'L', -1.5, 7,
        0, 10,
        1.5, 7,
        0, 7,
        0, -10 // top
    ];

    level = $.inArray(name, ['Calm', 'Light air', 'Light breeze', 'Gentle breeze', 'Moderate breeze',
        'Fresh breeze', 'Strong breeze', 'Near gale', 'Gale', 'Strong gale', 'Storm',
        'Violent storm', 'Hurricane']);

    if (level === 0) {
        path = [];
    }

    if (level === 2) {
        path.push('M', 0, -8, 'L', 4, -8); // short line
    } else if (level >= 3) {
        path.push(0, -10, 7, -10); // long line
    }

    if (level === 4) {
        path.push('M', 0, -7, 'L', 4, -7);
    } else if (level >= 5) {
        path.push('M', 0, -7, 'L', 7, -7);
    }

    if (level === 5) {
        path.push('M', 0, -4, 'L', 4, -4);
    } else if (level >= 6) {
        path.push('M', 0, -4, 'L', 7, -4);
    }

    if (level === 7) {
        path.push('M', 0, -1, 'L', 4, -1);
    } else if (level >= 8) {
        path.push('M', 0, -1, 'L', 7, -1);
    }

    return path;
};

/**
 * Draw the wind arrows. Each arrow path is generated by the windArrow function above.
 */
Meteogram.prototype.drawWindArrows = function (chart) {
    var meteogram = this;

    $.each(chart.series[0].data, function(i, point) {
        var sprite, arrow, x, y;

        if (meteogram.resolution > 36e5 || i % 2 === 0) {

            // Draw the wind arrows
            x = point.plotX + chart.plotLeft + 7;
            y = 255;
            if (meteogram.windSpeedNames[i] === 'Calm') {
                arrow = chart.renderer.circle(x, y, 10).attr({
                    fill: 'none'
                });
            } else {
                arrow = chart.renderer.path(
                    meteogram.windArrow(meteogram.windSpeedNames[i])
                ).attr({
                    rotation: parseInt(meteogram.windDirections[i], 10),
                    translateX: x, // rotation center
                    translateY: y // rotation center
                });
            }
            arrow.attr({
                stroke: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black',
                'stroke-width': 1.5,
                zIndex: 5
            })
            .add();

        }
    });
};

/** 
 * Draw blocks around wind arrows, below the plot area
 */
Meteogram.prototype.drawBlocksForWindArrows = function (chart) {
    var xAxis = chart.xAxis[0],
        x,
        pos,
        max,
        isLong,
        isLast,
        i;

    for (pos = xAxis.min, max = xAxis.max, i = 0; pos <= max + 36e5; pos += 36e5, i ++) {

        // Get the X position
        isLast = pos === max + 36e5;
        x = Math.round(xAxis.toPixels(pos)) + (isLast ? 0.5 : -0.5);

        // Draw the vertical dividers and ticks
        if (this.resolution > 36e5) {
            isLong = pos % this.resolution === 0;
        } else {
            isLong = i % 2 === 0;
        }
        chart.renderer.path(['M', x, chart.plotTop + chart.plotHeight + (isLong ? 0 : 28),
            'L', x, chart.plotTop + chart.plotHeight + 32, 'Z'])
            .attr({
                'stroke': chart.options.chart.plotBorderColor,
                'stroke-width': 1
            })
            .add();
    }
};

/**
 * Get the title based on the XML data
 */
Meteogram.prototype.getTitle = function () {
    return 'Meteograma para '+ this.xml.location.name; // +', '+ this.xml.location.country;
};

/**
 * Build and return the Highcharts options structure
 */
Meteogram.prototype.getChartOptions = function () {

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


    var meteogram = this;

    return {
        chart: {
            renderTo: this.container,
            marginBottom: 70,
            marginRight: 40,
            marginTop: 50,
            plotBorderWidth: 1,
            width: 800,
            height: 310
        },

        title: {
            text: this.getTitle(),
            align: 'left'
        },

        credits: {
            text: 'Pronóstico de <a href="http://yr.no">yr.no</a>',
            href: this.xml.credit.link['@attributes'].url,
            position: {
                x: -40
            }
        },

        tooltip: {
            shared: true,
            useHTML: true,
            formatter: function () {
                return meteogram.tooltipFormatter(this);
            }
        },

        xAxis: [{ // Bottom X axis
            type: 'datetime',
            tickInterval: 2 * 36e5, // two hours
            minorTickInterval: 36e5, // one hour
            tickLength: 0,
            gridLineWidth: 1,
            gridLineColor: (Highcharts.theme && Highcharts.theme.background2) || '#F0F0F0',
            startOnTick: false,
            endOnTick: false,
            minPadding: 0,
            maxPadding: 0,
            offset: 30,
            showLastLabel: true,
            labels: {
                format: '{value:%H}'
            }
        }, { // Top X axis
            linkedTo: 0,
            type: 'datetime',
            tickInterval: 24 * 3600 * 1000,
            labels: {
                format: '{value:<span style="font-size: 12px; font-weight: bold">%a</span> %b %e}',
                align: 'left',
                x: 3,
                y: -5
            },
            opposite: true,
            tickLength: 20,
            gridLineWidth: 1
        }],

        yAxis: [{ // temperature axis
            title: {
                text: null
            },
            labels: {
                format: '{value}°',
                style: {
                    fontSize: '10px'
                },
                x: -3
            },
            plotLines: [{ // zero plane
                value: 0,
                color: '#BBBBBB',
                width: 1,
                zIndex: 2
            }],
            // Custom positioner to provide even temperature ticks from top down
            tickPositioner: function () {
                var max = Math.ceil(this.max) + 1,
                    pos = max - 12, // start
                    ret;

                if (pos < this.min) {
                    ret = [];
                    while (pos <= max) {
                        ret.push(pos++);
                    }
                } // else return undefined and go auto

                return ret;

            },
            maxPadding: 0.3,
            tickInterval: 1,
            gridLineColor: (Highcharts.theme && Highcharts.theme.background2) || '#F0F0F0'

        }, { // precipitation axis
            title: {
                text: null
            },
            labels: {
                enabled: false
            },
            gridLineWidth: 0,
            tickLength: 0

        }, { // Air pressure
            allowDecimals: false,
            title: { // Title on top of axis
                text: 'hPa',
                offset: 0,
                align: 'high',
                rotation: 0,
                style: {
                    fontSize: '10px',
                    color: Highcharts.getOptions().colors[2]
                },
                textAlign: 'left',
                x: 3
            },
            labels: {
                style: {
                    fontSize: '8px',
                    color: Highcharts.getOptions().colors[2]
                },
                y: 2,
                x: 3
            },
            gridLineWidth: 0,
            opposite: true,
            showLastLabel: false
        }],

        legend: {
            enabled: false
        },

        plotOptions: {
            series: {
                pointPlacement: 'between'
            }
        },

        series: [{
            name: 'Temperatura',
            data: this.temperatures,
            type: 'spline',
            marker: {
                enabled: false,
                states: {
                    hover: {
                        enabled: true
                    }
                }
            },
            tooltip: {
                valueSuffix: '°C'
            },
            zIndex: 1,
            color: '#FF3333',
            negativeColor: '#48AFE8'
        }, {
            name: 'Precipitaciones',
            data: this.precipitations,
            type: 'column',
            color: '#68CFE8',
            yAxis: 1,
            groupPadding: 0,
            pointPadding: 0,
            borderWidth: 0,
            shadow: false,
            dataLabels: {
                enabled: true,
                formatter: function () {
                    if (this.y > 0) {
                        return this.y;
                    }
                },
                style: {
                    fontSize: '8px'
                }
            },
            tooltip: {
                valueSuffix: 'mm'
            }
        }, {
            name: 'Presión Atm.',
            color: Highcharts.getOptions().colors[2],
            data: this.pressures,
            marker: {
                enabled: false
            },
            shadow: false,
            tooltip: {
                valueSuffix: ' hPa'
            },
            dashStyle: 'shortdot',
            yAxis: 2
        }]
    }
};

/**
 * Post-process the chart from the callback function, the second argument to Highcharts.Chart.
 */
Meteogram.prototype.onChartLoad = function (chart) {

    this.drawWeatherSymbols(chart);
    this.drawWindArrows(chart);
    this.drawBlocksForWindArrows(chart);

};

/**
 * Create the chart. This function is called async when the data file is loaded and parsed.
 */
Meteogram.prototype.createChart = function () {
    var meteogram = this;
    this.chart = new Highcharts.Chart(this.getChartOptions(), function (chart) {
        meteogram.onChartLoad(chart);
    });
};

/**
 * Handle the data. This part of the code is not Highcharts specific, but deals with yr.no's
 * specific data format
 */
Meteogram.prototype.parseYrData = function () {

    var meteogram = this,
        xml = this.xml,
        pointStart;

    if (!xml || !xml.forecast) {
        $('#loading').html('<i class="fa fa-frown-o"></i> Error al cargar los datos, intente de nuevo más tarde');
        return;
    }

    // The returned xml variable is a JavaScript representation of the provided XML,
    // generated on the server by running PHP simple_load_xml and converting it to
    // JavaScript by json_encode.
    $.each(xml.forecast.tabular.time, function(i, time) {
        // Get the times - only Safari can't parse ISO8601 so we need to do some replacements
        var from = time['@attributes'].from +' UTC',
            to = time['@attributes'].to +' UTC';

        from = from.replace(/-/g, '/').replace('T', ' ');
        from = Date.parse(from);
        to = to.replace(/-/g, '/').replace('T', ' ');
        to = Date.parse(to);

        if (to > pointStart + 4 * 24 * 36e5) {
            return;
        }

        // If it is more than an hour between points, show all symbols
        if (i === 0) {
            meteogram.resolution = to - from;
        }

        // Populate the parallel arrays
        meteogram.symbols.push(time.symbol['@attributes']['var'].match(/[0-9]{2}[dnm]?/)[0]);
        meteogram.symbolNames.push(time.symbol['@attributes'].name);

        meteogram.temperatures.push({
            x: from,
            y: parseInt(time.temperature['@attributes'].value),
            // custom options used in the tooltip formatter
            to: to,
            index: i
        });

        meteogram.precipitations.push({
            x: from,
            y: parseFloat(time.precipitation['@attributes'].value)
        });
        meteogram.windDirections.push(parseFloat(time.windDirection['@attributes'].deg));
        meteogram.windDirectionNames.push(time.windDirection['@attributes'].name);
        meteogram.windSpeeds.push(parseFloat(time.windSpeed['@attributes'].mps));
        meteogram.windSpeedNames.push(time.windSpeed['@attributes'].name);

        meteogram.pressures.push({
            x: from,
            y: parseFloat(time.pressure['@attributes'].value)
        });

        if (i == 0) {
            pointStart = (from + to) / 2;
        }
    });

    // Smooth the line
    this.smoothLine(this.temperatures);

    // Create the chart when the data is loaded
    this.createChart();
};
// End of the Meteogram protype



 // On DOM ready...
// Set the hash to the yr.no URL we want to parse

if (!location.hash) {
        var place = 'Spania/Madrid/Titulcia';
        location.hash = 'http://www.yr.no/place/' + place + '/forecast_hour_by_hour.xml';

}

    // Then get the XML file through Highcharts' jsonp provider, see
    // https://github.com/highslide-software/highcharts.com/blob/master/samples/data/jsonp.php
    // for source code.

$.ajax({
    dataType: 'json',
    url: 'jsonp.php?url=' + location.hash.substr(1) + '&callback=?',
    success: function (xml) {
        window.meteogram = new Meteogram(xml, 'container');
    },
    error: Meteogram.prototype.error
});




</script>

</body>
</html>
