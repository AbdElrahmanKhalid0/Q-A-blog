CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    password VARCHAR(94) Not Null,
    role VARCHAR(10) DEFAULT 'user'
);

CREATE TABLE questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ask_time DATE NOT NULL,
    body VARCHAR(200) NOT NULL,
    asker_id INT NOT NULL,
    asked_id INT NOT NULL,
    status VARCHAR(15) DEFAULT 'not answered',
    CONSTRAINT asker_fk FOREIGN KEY(asker_id) REFERENCES users(id),
    CONSTRAINT asked_fk FOREIGN KEY(asked_id) REFERENCES users(id)
);

CREATE TABLE answers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    answer_owner INT NOT NULL,
    CONSTRAINT question_fk FOREIGN KEY(question_id) REFERENCES questions(id),
    CONSTRAINT owner_fk FOREIGN KEY(answer_owner) REFERENCES users(id)
);