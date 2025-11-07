CREATE TYPE USERROLE AS ENUM ('Ученик', 'Репетитор');

CREATE TABLE IF NOT EXISTS user (
    user_id SERIAL PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    telegram VARCHAR(100),
    vk VARCHAR(100),
    avatar_path VARCHAR(1000),
    interests TEXT,
    role USERROLE NOT NULL,
    email VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(500) NOT NULL
);

CREATE UNIQUE INDEX idx_user_email ON user (email);
CREATE INDEX idx_user_lastname ON user (last_name);
CREATE INDEX idx_user_firstname ON user (first_name);
CREATE INDEX idx_user_phone ON user (phone);


CREATE TABLE IF NOT EXISTS course (
    course_id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    created_at DATE NOT NULL,
    link_to_vector_db VARCHAR(1000) NOT NULL,
    input_test_json JSON
);

CREATE INDEX idx_course_title ON course(title);
CREATE INDEX idx_course_created_at ON course(created_at);


CREATE TABLE IF NOT EXISTS user_course (
    user_course_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    course_id INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    knowledge_gaps TEXT,
    graph_json JSON,
    output_test_json JSON
);

CREATE UNIQUE INDEX idx_user_course_unique ON user_course(user_id, course_id);
CREATE INDEX idx_user_course_user_id ON user_course(user_id);
CREATE INDEX idx_user_course_course_id ON user_course(course_id);
CREATE UNIQUE INDEX idx_one_course_for_student
ON user_course(user_id)
WHERE (
    SELECT role FROM "user"
    WHERE "user".user_id = user_course.user_id
) = 'Ученик';


CREATE TABLE IF NOT EXISTS material (
    material_id SERIAL PRIMARY KEY,
    file_path VARCHAR(1000) NOT NULL
);

CREATE UNIQUE INDEX idx_material_filepath ON material(file_path);


CREATE TABLE IF NOT EXISTS course_material (
    course_id INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    material_id INT NOT NULL REFERENCES material(material_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_course_material_unique ON course_material(course_id, material_id);
CREATE INDEX idx_course_material_course_id ON course_material(course_id);
CREATE INDEX idx_course_material_material_id ON course_material(material_id);


CREATE TABLE IF NOT EXISTS topic (
    topic_id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description_text TEXT
);

CREATE INDEX idx_topic_title ON topic(title);


CREATE TABLE IF NOT EXISTS course_topic (
    course_id INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    topic_id INT NOT NULL REFERENCES topic(topic_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_course_topic_unique ON course_topic(course_id, topic_id);
CREATE INDEX idx_course_topic_course_id ON course_topic(course_id);
CREATE INDEX idx_course_topic_topic_id ON course_topic(topic_id);


CREATE TABLE IF NOT EXISTS lesson (
    lesson_id SERIAL PRIMARY KEY,
    theory_text TEXT,
    reading_text TEXT,
    speaking_text TEXT,
    lesson_test_json JSON,
    lesson_test_results_json JSON,
    lesson_notes TEXT,
    results_json JSON,
    is_access BOOL NOT NULL DEFAULT false,
    is_ended BOOL NOT NULL DEFAULT false
);
