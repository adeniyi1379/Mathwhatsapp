-- Create database tables for SolveWithMe platform

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    school VARCHAR(200),
    grade_level VARCHAR(10) DEFAULT 'SS2',
    preferred_language VARCHAR(20) DEFAULT 'english',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL, -- text, image, voice
    language VARCHAR(20) DEFAULT 'english',
    topic VARCHAR(100),
    difficulty_level VARCHAR(20),
    is_resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Responses table
CREATE TABLE IF NOT EXISTS responses (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions(id),
    response_text TEXT NOT NULL,
    confidence_score DECIMAL(3,2),
    response_type VARCHAR(20) DEFAULT 'ai', -- ai, peer, teacher
    responder_id INTEGER REFERENCES users(id),
    is_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Peer discussions table
CREATE TABLE IF NOT EXISTS peer_discussions (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions(id),
    title VARCHAR(200),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, closed
    moderator_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Discussion participants table
CREATE TABLE IF NOT EXISTS discussion_participants (
    id SERIAL PRIMARY KEY,
    discussion_id INTEGER REFERENCES peer_discussions(id),
    user_id INTEGER REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- WAEC/JAMB questions database
CREATE TABLE IF NOT EXISTS exam_questions (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    explanation TEXT,
    source VARCHAR(20) NOT NULL, -- WAEC, JAMB
    year INTEGER,
    subject VARCHAR(50) DEFAULT 'Mathematics',
    topic VARCHAR(100),
    difficulty_level VARCHAR(20),
    question_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User activity logs
CREATE TABLE IF NOT EXISTS user_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    activity_type VARCHAR(50), -- question_asked, response_received, discussion_joined
    activity_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schools table (for pilot program)
CREATE TABLE IF NOT EXISTS schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    is_pilot_school BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teacher moderators table
CREATE TABLE IF NOT EXISTS teacher_moderators (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    school_id INTEGER REFERENCES schools(id),
    subject_specialization VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_questions_user_id ON questions(user_id);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);
CREATE INDEX IF NOT EXISTS idx_responses_question_id ON responses(question_id);
CREATE INDEX IF NOT EXISTS idx_exam_questions_topic ON exam_questions(topic);
CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities(user_id);
