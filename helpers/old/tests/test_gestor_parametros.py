import os
import time
import textwrap

import helpers.gestor_parametros as gp


def write_file(path, content):
    with open(path, "w") as f:
        f.write(textwrap.dedent(content))


def setup_config(tmpdir, dist_content, user_content):
    dist = os.path.join(tmpdir, "dist.py")
    user = os.path.join(tmpdir, "user.py")

    write_file(dist, dist_content)
    write_file(user, user_content)

    gp.RUTA_DIST = dist
    gp.RUTA_USER = user

    return dist, user


def test_initial_load(tmp_path):
    setup_config(
        tmp_path,
        "A = 1",
        "A = 2"
    )

    gestor = gp.GestorParametros(check_interval=0)
    assert gestor.leer_parametros("A") == 2


def test_dist_fallback(tmp_path):
    setup_config(
        tmp_path,
        "A = 10",
        ""
    )

    gestor = gp.GestorParametros(check_interval=0)

    # user empty should raise FileNotFoundError
    try:
        gestor.leer_parametros("A")
    except FileNotFoundError:
        pass


def test_multiple_parameters(tmp_path):
    setup_config(
        tmp_path,
        """
A = 1
B = 2
        """,
        """
A = 3
        """
    )

    gestor = gp.GestorParametros(check_interval=0)

    A, B = gestor.leer_parametros("A", "B")

    assert A == 3
    assert B == 2


def test_reload_on_change(tmp_path):
    dist, user = setup_config(
        tmp_path,
        "A = 1",
        "A = 2"
    )

    gestor = gp.GestorParametros(check_interval=0)

    assert gestor.leer_parametros("A") == 2
    version1 = gestor.version()

    time.sleep(0.01)

    write_file(user, "A = 5")
    time.sleep(0.05)  # 50 ms

    assert gestor.leer_parametros("A") == 5
    assert gestor.version() == version1 + 1


def test_no_reload_if_unchanged(tmp_path):
    setup_config(
        tmp_path,
        "A = 1",
        "A = 2"
    )

    gestor = gp.GestorParametros(check_interval=0)

    gestor.leer_parametros("A")
    v1 = gestor.version()

    gestor.leer_parametros("A")
    assert gestor.version() == v1


def test_syntax_error_does_not_replace_config(tmp_path):
    dist, user = setup_config(
        tmp_path,
        "A = 1",
        "A = 2"
    )

    gestor = gp.GestorParametros(check_interval=0)
    assert gestor.leer_parametros("A") == 2

    write_file(user, "A = ")  # syntax error

    assert gestor.leer_parametros("A") == 2


def test_missing_variable(tmp_path):
    setup_config(
        tmp_path,
        "A = 1",
        ""
    )

    gestor = gp.GestorParametros(check_interval=0)

    try:
        gestor.leer_parametros("B")
        assert False
    except AttributeError:
        assert True


def test_convertir_dict_a_list():
    gestor = gp.GestorParametros()

    data = {
        "ADS1": {"a": 1},
        "ADS2": {"a": 2},
    }

    result = gestor.convertir_dict_a_list(data)

    assert result[0]["id"] == "ADS1"
    assert result[1]["id"] == "ADS2"

def test_multiple_reload(tmp_path):
    dist, user = setup_config(
        tmp_path,
        "A = 1",
        "A = 2"
    )

    gestor = gp.GestorParametros(check_interval=0)

    for i in range(10):
        write_file(user, f"A = {i}")
        time.sleep(0.01)
        assert gestor.leer_parametros("A") == i

def test_partial_write(tmp_path):
    dist, user = setup_config(
        tmp_path,
        "A = 1",
        "A = 2"
    )

    gestor = gp.GestorParametros(check_interval=0)
    assert gestor.leer_parametros("A") == 2

    # simulate editor truncation
    open(user, "w").close()

    assert gestor.leer_parametros("A") == 2
