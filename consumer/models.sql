CREATE TABLE
    IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
        user_email VARCHAR(255) NOT NULL UNIQUE,
        user_name VARCHAR(255) NOT NULL,
        password VARCHAR(72) NOT NULL
    );

CREATE TABLE IF NOT EXISTS rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    owner_id INT NOT NULL,
    room_name VARCHAR(255) NOT NULL UNIQUE,
    room_type VARCHAR(10) NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

CREATE TABLE
    IF NOT EXISTS chat_messages (
        message_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
        type VARCHAR(10) CHECK (
            type = "regular"
            OR type = "ai"
        ) NOT NULL,
        room_id INT NOT NULL,
        user_id INT NOT NULL,
        content TEXT NOT NULL,
        role VARCHAR(10) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES rooms(room_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );