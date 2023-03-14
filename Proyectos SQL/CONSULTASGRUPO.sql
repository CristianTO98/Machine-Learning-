
--1 Mostrar el nombre, apellido y código de los reclusos que estén en la cárcel alcaraz, seguido de su celda.

SELECT p.nombre AS "Nombre", p.apellidos AS "Apellidos", r.nif AS "NIF", c.id_celda AS "Celda", ca.nombre
FROM UBD3707.persona p 
INNER JOIN UBD3707.recluso r on r.nif=p.nif
INNER JOIN UBD3707.celda c ON c.id_celda = r.id_celda
INNER JOIN UBD3707.modulo m on m.id_modulo=c.id_modulo
INNER JOIN UBD3707.carcel ca on ca.cod_carcel = m.cod_carcel 
WHERE ca.nombre = 'ALCARAZ';

-- 2 Mostar el recluso con mayor numero de visitas 

SELECT P.NOMBRE, P.APELLIDOS, COUNT(*)
FROM UBD3707.PERSONA P
JOIN UBD3707.RECLUSO R ON P.NIF = R.NIF
JOIN UBD3707.VISITA V ON V.NIF_RECLUSO = R.NIF
GROUP BY P.NIF, P.NOMBRE, P.APELLIDOS
HAVING COUNT(*) IN (
    SELECT MAX(VISITAS) FROM (SELECT COUNT(*) AS VISITAS FROM UBD3707.PERSONA P1
    JOIN UBD3707.RECLUSO R1 ON P1.NIF = R1.NIF
    JOIN UBD3707.VISITA V1 ON V1.NIF_RECLUSO = R1.NIF
    GROUP BY P1.NIF, P1.NOMBRE, P1.APELLIDOS));

--3 Visuliazar el gasto medio de cada recluso 

SELECT ROUND(AVG(C.CANTIDAD*P.PRECIO), 2) "MEDIA GASTADA POR RECLUSO"
FROM UBD3707.COMPRA C, UBD3707.PRODUCTO P
WHERE P.ID_PRODUCTO = C.ID_PRODUCTO
GROUP BY C.RECLUSO_NIF;

-- 4 Mostrar los reclusos que no hayan comprado el producto con codigo ni 1 el codigo 2

SELECT P.NOMBRE, P.APELLIDOS
FROM UBD3707.RECLUSO R INNER JOIN UBD3707.PERSONA P ON P.NIF=R.NIF
WHERE R.NIF NOT IN (
    SELECT C.RECLUSO_NIF
    FROM UBD3707.COMPRA C
    WHERE C.ID_PRODUCTO IN (1,2)
    GROUP BY C.RECLUSO_NIF);

-- 5 Mostrar los reclusos recluidos en el mismo año que otro con el nombre de ambos.
SELECT P1.NOMBRE "PRIMER NOMBRE", P1.APELLIDOS "PRIMER APELLIDO", P2.NOMBRE "SEGUNDO NOMBRE", P2.APELLIDOS "SEGUNDO APELLIDO"
FROM UBD3707.PERSONA P1, UBD3707.INGRESO_EGRESO E1, UBD3707.INGRESO_EGRESO E2, UBD3707.PERSONA P2
WHERE E1.NIF < E2.NIF
    AND (months_between(E1.FECHA_ENTRADA, E2.FECHA_ENTRADA) / 12) < 1
    AND (months_between(E1.FECHA_ENTRADA, E2.FECHA_ENTRADA) / 12) > -1
    AND P1.NIF = E1.NIF AND P2.NIF = E2.NIF;
    
-- 6 Calcular la media de meses de condena por delito cometido por uno de nuestros reclusos
SELECT  SUM(months_between(E.FECHA_SALIDA, E.FECHA_ENTRADA))/COUNT(D.ID) "Meses de media"
FROM UBD3707.DELITOS D, UBD3707.INGRESO_EGRESO E;

-- 7 Visualizar las celdas o celda con más delitos acumulados por sus reclusos
select c.*, agg.DELITOS  from UBD3707.celda c 
inner join 
(
    select c1.id_celda ID_CELDA, count(d1.nif) DELITOS from UBD3707.celda c1
    inner join UBD3707.recluso r1 on c1.id_celda = r1.id_celda
    inner join UBD3707.delitos d1 on r1.nif = d1.nif
    group by c1.id_celda
    having count(d1.nif)= 
        (
            select max("delitosCount") from(
            select c2.id_celda, count(d2.nif) "delitosCount" from UBD3707.celda c2 
            inner join UBD3707.recluso r2 on c2.id_celda = r2.id_celda
            inner join UBD3707.delitos d2 on r2.nif = d2.nif
            group by c2.id_celda)
        )
) agg on c.id_celda = agg.ID_CELDA;


-- 8 Mostrar la lista de reclusos voluntarios y subcontratados distinguibles
select p.nombre, p.apellidos, 'Recluso' "Empleado/Recluso" 
from UBD3707.persona p
inner join UBD3707.recluso r on p.nif = r.nif
inner join UBD3707.subcontrata_voluntario sv on sv.nif = r.nif

union

select p.nombre, p.apellidos, 'Empleado' "Empleado/Recluso" 
from UBD3707.persona p
inner join UBD3707.empleado e on p.nif = e.nif
inner join UBD3707.subcontrata_voluntario sv on sv.nif = e.nif
;

-- 9 Visualizar los sueldos del mes de diciembre de cada empleado y su NIF
select NIF, sum(SUELDO)"Sueldo Diciembre" from (
select e.nif , count(*) * e.euros_horas_noche * 8 "SUELDO"
from UBD3707.empleado e
inner join UBD3707.turno t on e.nif = t.nif
where cast(to_char(t.entrada,'HH24') as integer) >=0
    and cast(to_char(t.salida,'HH24') as integer) <=8
    and t.entrada >= to_date('01-12-2022','DD-MM-YYYY')
    and t.salida <=to_date('01-01-2023','DD-MM-YYYY')
group by e.nif,e.euros_horas_noche

union

select e.nif , count(*) * e.euros_hora * 8 
from UBD3707.empleado e
inner join UBD3707.turno t on e.nif = t.nif
where cast(to_char(t.entrada,'HH24') as integer) >= 8
    and cast(to_char(t.salida,'HH24') as integer) <= 23
    and t.entrada >= to_date('01-12-2022','DD-MM-YYYY')
    and t.salida <=to_date('01-01-2023','DD-MM-YYYY')
group by e.nif, e.euros_hora
)
group by nif;

--10 Mostrar las parejas de reclusos sin delitos comunes
select p1.nombre "NOMBRE 1", p1.apellidos "APELLIDOS 1", p2.nombre "NOMBRE 2", p2.apellidos "APELLIDOS 2" from UBD3707.recluso r1 
inner join UBD3707.persona p1 on r1.nif = p1.nif
join UBD3707.recluso r2 on r1.nif < r2.nif
inner join UBD3707.persona p2 on r2.nif = p2.nif
where 
    not exists(
        select d1.tipo_delito from UBD3707.delitos d1 
        where d1.nif = p1.nif

        intersect 

        select d2.tipo_delito from UBD3707.delitos d2
        where d2.nif = p2.nif
)
order by p1.nombre, p1.apellidos, p2.nombre,p2.apellidos;