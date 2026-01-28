# Protocolo para editar el manual

_(Los comandos de git se pueden ejecutar desde el terminal o usar cualquier programa de manejo de git)_

1. **Registro**
   1. Registro github.com
   2. Pasar usuario para autorizarlo
   3. Aceptar la invitación
2. **Bajar el repositorio por primera vez**
   1. `git clone https://github.com/PVControl/PVControl.git carpeta_destino`
   2. `git checkout -b rama-nueva-para-mis-cambios`, con esto creamos una rama nueva y cambiamos a ella.
3. **Bajar los cambios antes de editar, si no es la primera vez**
   1. `git checkout desarrollo`
   2. `git pull`
   3. `git checkout -b rama-nueva-para-mis-cambios`, con esto creamos una rama nueva y cambiamos a ella.
4. **Edición**
   1. Los archivos del manual están en la carpeta **_manual/_**
   2. Se modifican con VSCode + plugin (Markdown All In One) o cualquier editor de markdown o texto.
   3. [Guía de Markdown de GitHub](https://docs.github.com/es/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
5. **Guardar cambios** (podemos hacerlo varias veces guardando los cambios que vayamos haciendo)
   1. `git add .` si se han creado/borrado archivos
   2. `git commit -m "mensaje descriptivo de los cambios"`, esto guarda los cambios en local
6. **Subir los cambios**
   1. `git push -u origin rama-nueva-para-mis-cambios`, esto sube la rama entera a GitHub.
7. **Pedir la integración**
   1. En la página https://github.com/PVControl/PVControl/pulls creamos una nueva "Pull request"
   2. Ahí elegimos "base": **_desarrollo_** y "compare": **_rama-nueva-para-mis-cambios_**, asignamos la etiqueta "documentacion" y se pueden dejar comentarios.
   3. Guardamos la "Pull request"
8. **Modificar código**
   1. El protocolo es el mismo, pero antes habría que crear una "issue" en https://github.com/PVControl/PVControl/issues, con título y descripción y asignarnosla.
   2. El nombre de la "Pull request" debe ser el número de "issue" y su título, separado por guiones "-".
9. **Notificar un error o plantear una posible mejora**
   1. Hay que crear una "issue" con la mayor información posible que describa el problema o lo que se quiere conseguir.
