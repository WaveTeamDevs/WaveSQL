CREATE TABLE log_colors (
    id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(12) NOT NULL UNIQUE
)ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

INSERT INTO 
    log_colors (
        name
    ) VALUES 
    ("GREEN"),
    ("LIGHTGREEN"),
    ("YELLOW"),
    ("LIGHTYELLOW"),
    ("RED"),
    ("LIGHTRED"),
    ("CYAN"),
    ("LIGHTCYAN"),
    ("BLUE"),
    ("LIGHTBLUE"),
    ("MAGENTA"),
    ("LIGHTMAGENTA"),
    ("WHITE"),
    ("LIGHTWHITE"),
    ("BLACK"),
    ("LIGHTBLACK");

CREATE TABLE log_levels (
    id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(16) NOT NULL UNIQUE,
    color_id TINYINT UNSIGNED NOT NULL,
    CONSTRAINT fk_log_colors FOREIGN KEY (color_id)
        REFERENCES log_colors(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

INSERT INTO 
    log_levels (
        name,
        color_id
    ) VALUES 
('INFO', (SELECT id FROM log_colors WHERE name = "CYAN" LIMIT 1)),
('DEBUG', (SELECT id FROM log_colors WHERE name = "MAGENTA" LIMIT 1)),
('OK', (SELECT id FROM log_colors WHERE name = "GREEN" LIMIT 1)),
('FAILURE', (SELECT id FROM log_colors WHERE name = "RED" LIMIT 1)),
('WARNING', (SELECT id FROM log_colors WHERE name = "YELLOW" LIMIT 1)),
('EXPECTED ERROR', (SELECT id FROM log_colors WHERE name = "RED" LIMIT 1)),
('UNEXPECTED ERROR', (SELECT id FROM log_colors WHERE name = "RED" LIMIT 1)),
('ERROR', (SELECT id FROM log_colors WHERE name = "RED" LIMIT 1)),
('FATAL ERROR', (SELECT id FROM log_colors WHERE name = "LIGHTRED" LIMIT 1));

CREATE TABLE logs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    level_id TINYINT UNSIGNED,
    date TIMESTAMP NOT NULL DEFAULT NOW(),
    module VARCHAR(255) NOT NULL DEFAULT "DATABASE",
    message TEXT,
    traceback TEXT,
    INDEX(level_id),
    INDEX(date),
    INDEX(module),
    CONSTRAINT fk_log_levels FOREIGN KEY (level_id)
        REFERENCES log_levels(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE TABLE archived_logs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    level_id TINYINT UNSIGNED,
    date TIMESTAMP NOT NULL DEFAULT NOW(),
    module VARCHAR(255) NOT NULL DEFAULT "DATABASE",
    message TEXT,
    traceback TEXT,
    INDEX(level_id),
    INDEX(date),
    INDEX(module),
    CONSTRAINT fk_arh_log_levels FOREIGN KEY (level_id)
        REFERENCES log_levels(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- PROCEDURES

DELIMITER $$
CREATE PROCEDURE insert_log (
    IN p_level_id TINYINT UNSIGNED,
    IN p_module VARCHAR(255),
    IN p_message TEXT,
    IN p_traceback TEXT
)
BEGIN
    DECLARE v_log_id INT UNSIGNED;

    START TRANSACTION;

        IF EXISTS (
            SELECT 1 FROM log_levels WHERE id = p_level_id LIMIT 1
        ) THEN

            INSERT INTO logs (level_id, module, message, traceback)
            VALUES (p_level_id, p_module, p_message, p_traceback);

            SELECT 
                LAST_INSERT_ID() INTO v_log_id;

            SELECT 
                l.date AS log_date,
                ll.name AS log_level_name,
                lc.name AS log_level_color_name,
                l.module AS log_module,
                l.message AS log_message,
                l.traceback AS log_traceback
            FROM logs AS l
            JOIN log_levels AS ll ON l.level_id = ll.id
            JOIN log_colors AS lc ON lc.id = ll.color_id
            WHERE l.id = v_log_id;

        ELSE
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'The logging level was not found!';
        END IF;
    COMMIT;
END$$
DELIMITER ;



DELIMITER $$

CREATE EVENT delete_old_logs
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ошибка при удалении логов';

    INSERT INTO archived_logs (level_id, date, module, message, traceback)
    SELECT level_id, date, module, message, traceback
    FROM logs
    WHERE date < NOW() - INTERVAL 30 DAY;

    DELETE FROM logs
    WHERE date < NOW() - INTERVAL 30 DAY;

    DELETE FROM archived_logs
    WHERE date < NOW() - INTERVAL 60 DAY;
END$$
DELIMITER ;
