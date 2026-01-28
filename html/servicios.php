<?php
$titulo = "Servicios";
include ("cabecera.inc");
$password = "3c77f4029be2e609c22bba665f13b101";
if ((!isset ($_POST['password']) || (md5($_POST['password'])) != $password) && !isset ($_SESSION['logged'])) {
    ?>
    <form name="form" method="post" action="">
        <input type="password" name="password">
        <input type="submit" value="Modo edición">
    </form>
    <?php
} else {
    $_SESSION['logged'] = "yes";
    ?>
    <form action="/logout.php" method="post">
        <input type="hidden" name="origen" value="/servicios.php">
        <input type="submit" value="Salir modo edición" />
    </form>
    <?php
}
?>

<br /><br />
<h2>
    Estado de servicios:
</h2>
<?php if (isset ($_SESSION['logged'])) { ?>
    <div style="font-size: small; font-style: italic">
        Para poder actuar sobre los servicios hay que dar permiso al servidor web:
        <br>
        Crear archivo:<strong>sudo visudo /etc/sudoers.d/010_www-data</strong> <br>
        Debe contener esta línea: <strong>www-data ALL=(ALL) NOPASSWD: /bin/systemctl</strong>
    </div><br />
<?php } ?>
<style type="text/css" media="screen">
    table,
    th,
    td {
        border: 1px solid black;
        border-collapse: collapse;
        padding: 5px;
    }
</style>
<table id="table" width="70%">
    <thead id="t-head">
        <tr>
            <th>Servicio</th>
            <th>Enabled</th>
            <th>Estado</th>
            <th>Sub-estado</th>
            <th>Uptime</th>
            <?php if (isset ($_SESSION['logged'])) { ?>
                <th>Start/Stop</th>
            <?php } ?>
        </tr>
    </thead>
    <tbody id="t-body">
        <tr>
            <td colspan="6" style="text-align:center; padding: 30px">
                Cargando ...
            </td>
        </tr>
    </tbody>
</table>
<script>
    const fetchData = async () => {
        const response = await fetch('/api/servicios.php');
        const data = await response.json();
        return data;
    }
    // send POST with name
    const start_stop = async (name) => {
        const cfg = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name }),
        }
        const response = await fetch('/api/servicios.php', cfg);
        const data = await response.json();
        return data.success;
    }
    const loadTableData = (items) => {
        const logged = "<?php echo isset ($_SESSION['logged']); ?>" ? true : false;
        const table = document.getElementById("t-body");
        table.innerHTML = '';
        items.forEach(item => {
            const color = (item.state === "active" && item.substate === "running") ?
                "LightGreen" : "Coral";
            let row = table.insertRow();
            row.style = `background-color:${color};`;
            let name = row.insertCell(0);
            name.innerHTML = item.name;
            let is_enabled = row.insertCell(1);
            is_enabled.innerHTML = item.is_enabled;
            let state = row.insertCell(2);
            state.innerHTML = item.state;
            let substate = row.insertCell(3);
            substate.innerHTML = item.substate;
            let uptime = row.insertCell(4);
            uptime.innerHTML = item.uptime;
            if (logged) {
                let action = row.insertCell(5);
                action.innerHTML = `<input type="button" onclick="start_stop('${item.name}')" value="Start/Stop" />`;
            }
        });
    }
    setInterval(async function () {
        const result = fetchData().then(result => {
            if (result.success) {
                loadTableData(result.data);
            }
        });
    }, 5000);
</script>

<?php
include_once "pie.inc";
?>
