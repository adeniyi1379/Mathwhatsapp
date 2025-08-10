-- Additional tables for enhanced analytics

-- User engagement metrics
CREATE TABLE IF NOT EXISTS user_engagement_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    questions_asked INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    peer_interactions INTEGER DEFAULT 0,
    study_time_minutes INTEGER DEFAULT 0,
    engagement_score DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Topic performance tracking
CREATE TABLE IF NOT EXISTS topic_performance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    topic VARCHAR(100) NOT NULL,
    questions_attempted INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    average_confidence DECIMAL(3,2) DEFAULT 0.00,
    last_attempted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, topic)
);

-- School performance metrics
CREATE TABLE IF NOT EXISTS school_metrics (
    id SERIAL PRIMARY KEY,
    school_id INTEGER REFERENCES schools(id),
    date DATE NOT NULL,
    active_students INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    average_success_rate DECIMAL(3,2) DEFAULT 0.00,
    top_topics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, date)
);

-- Notification logs
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    notification_type VARCHAR(50) NOT NULL, -- reminder, summary, achievement
    channel VARCHAR(20) NOT NULL, -- whatsapp, sms
    status VARCHAR(20) DEFAULT 'sent', -- sent, failed, delivered
    message_content TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System health metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    metric_unit VARCHAR(20),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_user_engagement_date ON user_engagement_metrics(date);
CREATE INDEX IF NOT EXISTS idx_user_engagement_user_id ON user_engagement_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_topic_performance_user_topic ON topic_performance(user_id, topic);
CREATE INDEX IF NOT EXISTS idx_school_metrics_date ON school_metrics(date);
CREATE INDEX IF NOT EXISTS idx_notification_logs_user_type ON notification_logs(user_id, notification_type);
CREATE INDEX IF NOT EXISTS idx_system_metrics_name_time ON system_metrics(metric_name, recorded_at);
