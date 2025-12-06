DROP DATABASE IF EXISTS reel_db;
CREATE DATABASE IF NOT EXISTS reel_db;

USE reel_db;

-- Admin: Applications table
-- Used by /admin/applications and /admin/applications/{id}
CREATE TABLE IF NOT EXISTS Applications (
    application_id    INT AUTO_INCREMENT PRIMARY KEY,
    applicant_name    VARCHAR(255) NOT NULL,
    email             VARCHAR(255) NOT NULL,
    portfolio_url     VARCHAR(500),

    status            VARCHAR(50) NOT NULL DEFAULT 'pending',
    admin_notes       TEXT,

    submitted_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- Admin: FlaggedActivities table
-- Used by /admin/flagged-activities routes
CREATE TABLE IF NOT EXISTS FlaggedActivities (
    flag_id           INT AUTO_INCREMENT PRIMARY KEY,

    -- what was flagged
    related_type      VARCHAR(50) NOT NULL,  -- e.g. 'post', 'project', 'message'
    related_id        INT NOT NULL,

    reason            TEXT NOT NULL,

    status            VARCHAR(50) NOT NULL DEFAULT 'open',
    resolution_notes  TEXT,

    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at       DATETIME NULL
);

-- Admin: Alerts table
-- Used by /admin/alerts routes
CREATE TABLE IF NOT EXISTS Alerts (
    alert_id      INT AUTO_INCREMENT PRIMARY KEY,

    alert_type    VARCHAR(50) NOT NULL,    -- e.g. 'system', 'moderation'
    message       TEXT NOT NULL,

    related_type  VARCHAR(50) NULL,
    related_id    INT NULL,

    status        VARCHAR(50) NOT NULL DEFAULT 'open',
    admin_notes   TEXT,

    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at   DATETIME NULL
);

-- POSTS TABLE
CREATE TABLE IF NOT EXISTS Posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    media_url VARCHAR(255),
    caption TEXT,
    tags VARCHAR(255),
    visibility ENUM('public', 'private') DEFAULT 'public',
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- POST INTERACTIONS TABLE
CREATE TABLE IF NOT EXISTS PostInteractions (
    interaction_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT,
    interaction_type ENUM('view', 'like', 'comment') NOT NULL,
    comment_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MESSAGES TABLE
CREATE TABLE IF NOT EXISTS Messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    is_starred BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    is_deleted_by_sender BOOLEAN DEFAULT FALSE,
    is_deleted_by_receiver BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);