CREATE TABLE
    IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
        user_email VARCHAR(255) NOT NULL UNIQUE,
        user_name VARCHAR(255) NOT NULL,
        password VARCHAR(72) NOT NULL,
        is_deleted BOOLEAN NOT NULL DEFAULT 0
    );

INSERT INTO users (user_email, user_name, password) VALUES ('openai', 'openai', 'openai');

CREATE TABLE IF NOT EXISTS rooms (
    room_id VARCHAR(36) PRIMARY KEY NOT NULL,
    owner_id INT NOT NULL,
    room_name VARCHAR(255) NOT NULL UNIQUE,
    room_type VARCHAR(10) NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

INSERT INTO rooms (room_id, owner_id, room_name, room_type, is_deleted) VALUES ('dev', 1, 'room_test', 'dev', 1);


CREATE TABLE
    IF NOT EXISTS chat_messages (
        message_id VARCHAR(36) PRIMARY KEY NOT NULL,
        message_type VARCHAR(10) CHECK (
            type = 'regular' OR type = 'ai'
        ) NOT NULL,
        room_id VARCHAR(36) NOT NULL,
        user_id INT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP,
        /* created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, */
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES rooms(room_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );

CREATE TABLE 
    IF NOT EXISTS gpt_responses (
        response_id VARCHAR(36) PRIMARY KEY NOT NULL,
        datetime TIMESTAMP NOT NULL,
        answer TEXT NOT NULL,
        prompt_tokens INT NOT NULL,
        response_tokens INT NOT NULL,
        room_id VARCHAR(36) NOT NULL,
        asker_id INT NOT NULL,
        api_key VARCHAR(255) NOT NULL,
        FOREIGN KEY (room_id) REFERENCES rooms(room_id),
        FOREIGN KEY (asker_id) REFERENCES users(user_id)
);

CREATE TABLE
    IF NOT EXISTS gpt_messages (
        response_id VARCHAR(36) NOT NULL,
        role VARCHAR(10) CHECK (
            role = 'assistant' or role = 'user'
        ) NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY (response_id) REFERENCES gpt_responses(response_id)
);

