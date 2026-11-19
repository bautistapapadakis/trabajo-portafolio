-- Base de datos del portfolio (MySQL / Clever Cloud).
CREATE DATABASE IF NOT EXISTS portfolio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE portfolio_db;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS perfil (
    id INT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    email VARCHAR(255),
    telefono VARCHAR(100),
    ubicacion VARCHAR(255),
    github VARCHAR(500),
    linkedin VARCHAR(500),
    cv VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS estudios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    institucion VARCHAR(255),
    periodo VARCHAR(120),
    descripcion TEXT,
    orden INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS experiencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    puesto VARCHAR(255) NOT NULL,
    empresa VARCHAR(255),
    periodo VARCHAR(120),
    descripcion TEXT,
    orden INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tecnologias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    nivel VARCHAR(100),
    icono VARCHAR(200),
    orden INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS proyectos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tecnologias VARCHAR(500),
    url VARCHAR(500),
    imagen VARCHAR(500),
    orden INT NOT NULL DEFAULT 0
);

ALTER TABLE perfil
    MODIFY nombre VARCHAR(200) NOT NULL,
    MODIFY titulo VARCHAR(255) NOT NULL,
    MODIFY email VARCHAR(255),
    MODIFY telefono VARCHAR(100),
    MODIFY ubicacion VARCHAR(255),
    MODIFY github VARCHAR(500),
    MODIFY linkedin VARCHAR(500),
    MODIFY cv VARCHAR(500);

ALTER TABLE estudios
    MODIFY titulo VARCHAR(255) NOT NULL,
    MODIFY institucion VARCHAR(255),
    MODIFY periodo VARCHAR(120);

ALTER TABLE experiencias
    MODIFY puesto VARCHAR(255) NOT NULL,
    MODIFY empresa VARCHAR(255),
    MODIFY periodo VARCHAR(120);

ALTER TABLE tecnologias
    MODIFY nombre VARCHAR(120) NOT NULL,
    MODIFY nivel VARCHAR(100),
    MODIFY icono VARCHAR(200);

ALTER TABLE proyectos
    MODIFY titulo VARCHAR(255) NOT NULL,
    MODIFY tecnologias VARCHAR(500),
    MODIFY url VARCHAR(500),
    MODIFY imagen VARCHAR(500);

-- Usuario inicial: admin / admin123 (hash scrypt de Werkzeug).
INSERT IGNORE INTO usuarios (id, username, password_hash) VALUES
(1, 'admin', 'scrypt:32768:8:1$nabWjcwCth3YPCVC$ddd963ab43a89f5f6a204f10815d5a188a52ec081e0cc31dd637fc53742e71edaadff37ac03ca5614d86516dc0b78dcbe18157af022c9fc03de82a11d6762337');

INSERT IGNORE INTO perfil (id, nombre, titulo, descripcion, email, telefono, ubicacion, github, linkedin, cv) VALUES
(1,
 'Mía Fernández',
 'Desarrolladora Full Stack',
 'Soy una desarrolladora full stack apasionada por crear productos web claros, accesibles y con buena experiencia de usuario. Me gusta aprender, trabajar en equipo y convertir ideas en soluciones concretas.',
 'mia.fernandez@email.com',
 '+54 9 11 5555-1234',
 'Buenos Aires, Argentina',
 'https://github.com/tu-usuario',
 'https://www.linkedin.com/in/tu-usuario',
 'CV.pdf');

INSERT IGNORE INTO estudios (id, titulo, institucion, periodo, descripcion, orden) VALUES
(1, 'Tecnicatura en Programación', 'UTN - Facultad Regional Buenos Aires', '2022 - 2025', 'Formación en desarrollo de software, bases de datos y trabajo en proyectos.', 1),
(2, 'Curso de Desarrollo Web Full Stack', 'CoderHouse', '2024', 'HTML, CSS, JavaScript, Flask y MySQL aplicados a un proyecto final.', 2),
(3, 'Secundario Orientado a Ciencias Naturales', 'Escuela Nacional N° 7', '2016 - 2021', 'Bachillerato con orientación en ciencias naturales.', 3);

INSERT IGNORE INTO experiencias (id, puesto, empresa, periodo, descripcion, orden) VALUES
(1, 'Desarrolladora Web Junior', 'Freelance', '2025 - Actualidad', 'Creación y mantenimiento de sitios web con Flask, MySQL y diseño responsive.', 1),
(2, 'Prácticas en Soporte IT', 'Estudio Digital', '2024', 'Soporte a usuarios, carga de datos y documentación de procesos internos.', 2);

INSERT IGNORE INTO tecnologias (id, nombre, nivel, icono, orden) VALUES
(1, 'Python', 'Avanzado', 'fa-brands fa-python', 1),
(2, 'Flask', 'Intermedio', 'fa-solid fa-flask', 2),
(3, 'MySQL', 'Intermedio', 'fa-solid fa-database', 3),
(4, 'HTML & CSS', 'Avanzado', 'fa-brands fa-html5', 4),
(5, 'JavaScript', 'Intermedio', 'fa-brands fa-js', 5),
(6, 'Git & GitHub', 'Intermedio', 'fa-brands fa-github', 6);

INSERT IGNORE INTO proyectos (id, titulo, descripcion, tecnologias, url, imagen, orden) VALUES
(1, 'Portfolio personal', 'Sitio web full stack con login, panel de edición y base de datos MySQL.', 'Flask, Jinja2, MySQL', 'https://github.com/tu-usuario', 'proyecto-1.svg', 1),
(2, 'Gestor de tareas', 'Aplicación para organizar tareas con filtros, estados y persistencia en base de datos.', 'Python, Flask, MySQL', 'https://github.com/tu-usuario', 'proyecto-2.svg', 2),
(3, 'Landing de cafetería', 'Página responsive con animaciones, formulario de contacto y mapa embebido.', 'HTML, CSS, JavaScript', 'https://github.com/tu-usuario', 'proyecto-3.svg', 3);
