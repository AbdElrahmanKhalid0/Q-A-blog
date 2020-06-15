CREATE TABLE users (
    username VARCHAR(22) NOT NULL PRIMARY KEY,
    password VARCHAR(94) Not Null,
    role VARCHAR(10) DEFAULT 'user'
);

CREATE TABLE questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ask_time DATE NOT NULL,
    body VARCHAR(200) NOT NULL,
    asker_username VARCHAR(22) NOT NULL,
    asked_username VARCHAR(22) NOT NULL,
    status VARCHAR(15) DEFAULT 'not answered',
    CONSTRAINT asker_fk FOREIGN KEY(asker_username) REFERENCES users(username),
    CONSTRAINT asked_fk FOREIGN KEY(asked_username) REFERENCES users(username)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE answers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    body VARCHAR(200) NOT NULL,
    question_id INT NOT NULL,
    answer_owner VARCHAR(22) NOT NULL,
    CONSTRAINT question_fk FOREIGN KEY(question_id) REFERENCES questions(id),
    CONSTRAINT owner_fk FOREIGN KEY(answer_owner) REFERENCES users(username)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);