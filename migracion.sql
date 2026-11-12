-- Ejecutar una sola vez en phpMyAdmin sobre la base institucion.
-- Los registros antiguos reciben identificaciones temporales PENDIENTE-<id>.
USE institucion;

ALTER TABLE estudiantes
    ADD COLUMN identificacion VARCHAR(30) NULL;

UPDATE estudiantes
SET identificacion = CONCAT('PENDIENTE-', id)
WHERE identificacion IS NULL;

ALTER TABLE estudiantes
    MODIFY identificacion VARCHAR(30) NOT NULL,
    ADD CONSTRAINT uq_estudiantes_identificacion UNIQUE (identificacion);
