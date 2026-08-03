-- 購読者テーブル
-- ペイロードなし方式のため、暗号鍵(p256dh/auth)は保存しない＝保持する個人データが最小限
CREATE TABLE IF NOT EXISTS subscriptions (
  endpoint    TEXT PRIMARY KEY,
  min_scale   INTEGER NOT NULL DEFAULT 40,   -- 30=震度3, 40=震度4, 45=震度5弱
  region      TEXT    NOT NULL DEFAULT 'all',-- all / hokkaido / tohoku / kanto ...
  created_at  INTEGER NOT NULL,
  last_ok_at  INTEGER
);

CREATE INDEX IF NOT EXISTS idx_sub_scale ON subscriptions (min_scale);

-- 送信済みの地震ID（重複通知の防止）
CREATE TABLE IF NOT EXISTS sent_quakes (
  quake_id  TEXT PRIMARY KEY,
  sent_at   INTEGER NOT NULL,
  max_scale INTEGER,
  place     TEXT
);
