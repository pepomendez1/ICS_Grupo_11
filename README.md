# ICS_Grupo_11
Este es el repositorio del grupo 11, de la materia Ingenieria y Calidad de Software, UTN FRC. Esta creado con el fin de aplicar los conceptos de gestión de configuración estudiados.

Tabla de Contenidos

Información General
Integrantes del Grupo
Repositorio del Proyecto
Estructura del Proyecto
Convenciones y Reglas de Nombrado
Ítems de Configuración
Línea Base del Proyecto
Glosario
Información General

Cátedra: Ingeniería y Calidad de Software
Curso: 4k1 Profesoras:

Titular: Ing. Judith Meles
Jefa de Trabajos Prácticos: Ing. Mickaela Crespo
Ayudante Alumno: Salvador Barbera
Integrantes del Grupo

Nombre	Legajo
Barzola Augusto	59247
Dagnino Dailly Facundo	94307
García Ignacio	97114
Martínez Dalke Facundo Andrés	98479
Méndez Carranza Pedro	94214
Novello Crivelli Pedro	75198
Pérez Carullo Lautaro	423349
Salguero Juan Román	96135
Succar Agustín	73540
Torres Gec Federico	85918
Repositorio del Proyecto

Repositorio GitHub

Estructura del Proyecto

README.md -> Informacion general del repositorio, integrantes del grupo y convenciones de uso del repositorio
Material_Teorico/
Apuntes/ -> resúmenes y notas de clase.
Bibliografia/ -> libros, artículos y papers.
Diapositivas/ -> presentaciones de las clases.
Trabajos_Practicos/
ISW_Enunciados TP evaluables 2025.pdf
TP1/
TP2/
TP3/
TP4/
TP5/
TP6/
TP7/
TP8/
TP9/
TP10/
TP11/
TP12/
TP13/
TP14/
TP14_Salida.pdf
Convenciones

Los trabajos practicos se guardan en carpetas con el formato TP* Ejemplo: 'TP1'. Se utiliza el carácter comodín * en la denominación TP* para representar un ítem de configuración genérico que agrupa a todos los trabajos prácticos (TP1, TP2, TP3, etc.).
Dentro de las carpetas de Trabajos practicos encontraremos las salidas de los mismos, junto a los items de configuracion necesarios.
Los archivos dentro de las carpetas TP* deben usar la convencion TP<n>_<NombreArchivo>.<extensión>. Si el nombre del archivo requiere más de una palabra, se utilizará guion bajo (_) como separador en lugar de los espacios.
Las diapositivas se deben guardar con el formato <nn>_<NombreDiapositiva>.<pdf> ejemplo: 01_SCM.pdf. Si el nombre de la diapositiva requiere más de una palabra, se utilizará guion bajo (_) como separador en lugar de los espacios.
La bibliografia se debe guardar con el siguiente formato <Tema>_<NombreDocumento>.<pdf>. El tema se escribe sin espacios ni caracteres especiales. En caso de requerir más de una palabra en el nombre del documento, se utilizará guion bajo (_) como separador.
Los apuntes se deben guardar con el siguiente formato <Fecha>_<NombreApunte>.<pdf>. Si el nombre del apunte requiere más de una palabra, se utilizará guion bajo (_) como separador en lugar de los espacios. La fecha se expresará en formato ISO 8601 (AAAA-MM-DD). Este formato permite un orden cronológico correcto y facilita la búsqueda.
Ítems de Configuración

Ítem de Configuración	Regla de Nombrado	Ubicación Física	Tipo de Ítem
README.md	README.md	/	Proyecto
Diapositivas	<nn>_<NombreDiapositiva>.<pdf>	/Material_Teorico/Diapositivas/	Documentación
Bibliografia	<Tema>_<NombreDocumento>.<pdf>	/Material_Teorico/Bibliografia/	Documentación
Apuntes	<Fecha>_<NombreApunte>.<pdf>	/Material_Teorico/Apuntes/	Documentación
ISW_Enunciados TP evaluables 2025	ISW_Enunciados TP evaluables 2025.pdf	/Trabajos_Practicos/	Proyecto
TP*	TP<n>_<NombreArchivo>.<extensión> (.pdf, .xlsx)	/Trabajos_Practicos/TP*/	Producto
Línea Base del Proyecto

La linea base del proyecto se establecera luego de la revision y/o aprobacion por parte del equipo docente de los trabajos practicos. Las modificaciones posteriores deben ser justificadas, ya sea por correcciones o cambios necesarios. Las líneas base se etiquetarán en el repositorio con la siguiente convención:

LB<n>_TP<n>_v<n>
Ejemplo: LB1_TP4_v1 → Primera línea base, correspondiente al TP4, primera versión aprobada.
Glosario

<nn> Número correlativo de dos dígitos que indica el orden.
Ejemplo: 00, 01, 02, ...
<n>Número entero usado como identificador. En algunos casos como trabajos practicos, se utiliza de forma correlativa mientras que otros casos como los trabajos prácticos evaluables, puede comenzar en un valor distinto y no seguir una correlación estricta.
Ejemplo dentro de la estructura: TP1, TP2, ..., TP10, ...
Ejemplo de Linea base: LB1_TP4_v1, LB1_TP4_v2, ...
<Fecha> fecha en la que se sube el archivo, expresada en formato ISO 8601 (AAAA-MM-DD).
<NombreApunte> describe contenido principal del apunte.
<Tema> se basará en el contenido central del documento subido (por ejemplo: TDD, Nexus, Kanban, Paper, etc).
<NombreDocumento> título descriptivo del archivo, según su contenido.
<NombreDiapositiva> indica el tema principal de la filmina.
<NombreArchivo> hace referencia al archivo de salida principal del TP, o a un nombre representativo del contenido del entregable.