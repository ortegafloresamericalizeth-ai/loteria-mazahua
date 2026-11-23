CREATE DATABASE IF NOT EXISTS loteria_mazahua
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE loteria_mazahua;

CREATE TABLE IF NOT EXISTS elementos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre_espanol VARCHAR(100) NOT NULL,
  nombre_mazahua VARCHAR(100) NOT NULL,
  descripcion TEXT,
  categoria VARCHAR(50),
  imagen VARCHAR(255),
  audio_mazahua VARCHAR(255),
  uid_rfid VARCHAR(20) NULL UNIQUE
);

INSERT INTO elementos (nombre_espanol, nombre_mazahua, categoria) VALUES
('Triste', 'Juejme', 'emociones'),
('Tortilla', 'T''zeyi', 'alimentos y cultivos'),
('Tierra', 'Jomi', 'naturaleza'),
('Sol', 'Jyaru', 'naturaleza'),
('Silla', 'Tjujnu', 'objetos'),
('Rodilla', 'Ngomu', 'cuerpo'),
('Río', 'B''a''ə / B''öö', 'naturaleza'),
('Lápiz', 'Jphündi', 'objetos'),
('Pie', 'Nua', 'cuerpo'),
('Perro', 'Dyoo', 'animales'),
('Pájaro', 'Kawaju', 'animales'),
('Padre', 'Tata', 'familia'),
('Noche', 'Xons''i', 'naturaleza'),
('Niño', 'B''ezo', 'familia'),
('Niña', 'B''ezche', 'familia'),
('Montaña', 'T''omi', 'naturaleza'),
('Milpa', 'Trjota', 'alimentos y cultivos'),
('Mesa', 'Mexa', 'objetos'),
('Mariposa', 'Pes''i', 'animales'),
('Mano', 'Ngomu', 'cuerpo'),
('Maíz', 'Trjo''o', 'alimentos y cultivos'),
('Madre', 'Nana', 'familia'),
('Luna', 'Zana', 'naturaleza'),
('Lluvia', 'K''əə / K''öö', 'naturaleza'),
('Libro', 'Skuama', 'objetos'),
('Leche', 'Lechek''i~', 'alimentos y cultivos'),
('Hola', '-Kimiji', 'saludos'),
('Hermano', 'Kjuarma', 'familia'),
('Hermana', '-Kjujue', 'familia'),
('Gato', 'Mixi', 'animales'),
('Gallo', 'Tare', 'animales'),
('Gallina', 'Pji', 'animales'),
('Fuego', 'Chji', 'naturaleza'),
('Frijol', 'Mbero', 'alimentos y cultivos'),
('Flor', 'Nxubi', 'naturaleza'),
('Feliz', 'Májä', 'emociones'),
('Estrella', 'S’eje', 'naturaleza'),
('Enojado', 'Úd''ú', 'emociones'),
('Correr', 'Kuañi', 'acciones'),
('Corazón', 'Mëst''ë', 'cuerpo'),
('Cielo', 'Mezhe-Mëzhe', 'naturaleza'),
('Cerdo', 'Ts''imi', 'animales'),
('Casa', 'Ngumi', 'lugares'),
('Camino', 'Mañi', 'lugares'),
('Caminar', 'Nzhodú', 'acciones'),
('Cabeza', 'B''ə', 'cuerpo'),
('Caballo', 'Ts''ints''u', 'animales'),
('Borrego', 'D''ëmë', 'animales'),
('Árbol', 'Za''a', 'naturaleza'),
('Agua', 'Ndeje', 'naturaleza'),
('Adiós', 'Maxko', 'saludos'),
('Abuelo', 'Tita', 'familia'),
('Abuela', 'Nita', 'familia'),
('Vaca', 'Baka', 'animales');

-- Verificación
SELECT COUNT(*) FROM elementos;   -- debe dar 54
SELECT * FROM elementos LIMIT 5;
SELECT COUNT(*) FROM elementos;
ALTER TABLE elementos
  ADD UNIQUE KEY uq_nombre_espanol (nombre_espanol);
