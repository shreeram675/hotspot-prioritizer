-- Run in Postgres with PostGIS enabled

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(150) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role VARCHAR(20) DEFAULT 'citizen' CHECK (role IN ('citizen', 'admin')),
  created_at TIMESTAMP DEFAULT now()
);

-- Initial Admin Seed (Password: admin123)
-- Hash generated via passlib.hash.bcrypt.hash("admin123")
INSERT INTO users (name, email, password_hash, role) 
VALUES ('System Admin', 'admin@example.com', '$2b$12$TEsoByUo2vEHiI0Qh1Zh1u.XQv2YYhSrZn4qL49l/DSAnXLhBTguO', 'admin');

CREATE TABLE reports (
  report_id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(user_id),
  category VARCHAR(50) NOT NULL,
  title VARCHAR(200),
  description TEXT,
  location GEOMETRY(POINT,4326) NOT NULL,
  address VARCHAR(255),
  upvote_count INT DEFAULT 0,
  severity VARCHAR(20) DEFAULT 'Medium',
  road_importance INT DEFAULT 1,
  status VARCHAR(30) DEFAULT 'open',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE report_images (
  image_id SERIAL PRIMARY KEY,
  report_id INT REFERENCES reports(report_id) ON DELETE CASCADE,
  file_path VARCHAR(255) NOT NULL,
  uploaded_at TIMESTAMP DEFAULT now()
);

CREATE TABLE upvotes (
  report_id INT REFERENCES reports(report_id) ON DELETE CASCADE,
  user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
  upvoted_at TIMESTAMP DEFAULT now(),
  PRIMARY KEY(report_id, user_id)
);

CREATE INDEX idx_reports_location ON reports USING GIST(location);
CREATE INDEX idx_reports_created ON reports(created_at DESC);
