USE loteria_mazahua;

SET SQL_SAFE_UPDATES = 0;

DELETE e1 FROM elementos e1
JOIN elementos e2
  ON e1.nombre_espanol = e2.nombre_espanol
 AND e1.id > e2.id;

SET SQL_SAFE_UPDATES = 1;

SELECT COUNT(*) FROM elementos;

ALTER TABLE elementos
  ADD UNIQUE KEY uq_nombre_espanol (nombre_espanol);
  
  SELECT COUNT(*) AS con_imagen FROM elementos WHERE imagen IS NOT NULL;
SELECT COUNT(*) AS con_audio  FROM elementos WHERE audio_mazahua IS NOT NULL;