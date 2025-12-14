-- ============================================================
-- 更新 usage_logs 表结构
-- 支持保存解析结果、候选人信息、版本信息等
-- 
-- 在 Supabase SQL Editor 中执行此脚本
-- ============================================================

-- 添加新字段到 usage_logs 表
ALTER TABLE usage_logs 
ADD COLUMN IF NOT EXISTS filename VARCHAR(255),
ADD COLUMN IF NOT EXISTS candidate_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS candidate_phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS candidate_email VARCHAR(100),
ADD COLUMN IF NOT EXISTS result_json JSONB,
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'success',
ADD COLUMN IF NOT EXISTS error_message TEXT,
ADD COLUMN IF NOT EXISTS app_version VARCHAR(20),
ADD COLUMN IF NOT EXISTS client_info JSONB;

-- 为常用查询字段创建索引
CREATE INDEX IF NOT EXISTS idx_usage_logs_status ON usage_logs(status);
CREATE INDEX IF NOT EXISTS idx_usage_logs_candidate_name ON usage_logs(candidate_name);
CREATE INDEX IF NOT EXISTS idx_usage_logs_app_version ON usage_logs(app_version);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);

-- 添加注释
COMMENT ON COLUMN usage_logs.filename IS '原始简历文件名';
COMMENT ON COLUMN usage_logs.candidate_name IS '候选人姓名';
COMMENT ON COLUMN usage_logs.candidate_phone IS '候选人电话';
COMMENT ON COLUMN usage_logs.candidate_email IS '候选人邮箱';
COMMENT ON COLUMN usage_logs.result_json IS '完整的解析结果 JSON';
COMMENT ON COLUMN usage_logs.status IS '状态: success/error';
COMMENT ON COLUMN usage_logs.error_message IS '错误信息（仅当 status=error 时）';
COMMENT ON COLUMN usage_logs.app_version IS '应用版本号';
COMMENT ON COLUMN usage_logs.client_info IS '客户端信息 JSON（操作系统、机器名等）';

-- ============================================================
-- 查询示例
-- ============================================================

-- 查询所有解析记录（带候选人信息）
-- SELECT 
--     l.owner_name as "授权用户",
--     ul.candidate_name as "候选人",
--     ul.candidate_phone as "电话",
--     ul.filename as "文件名",
--     ul.status as "状态",
--     ul.app_version as "版本",
--     ul.created_at as "时间"
-- FROM usage_logs ul
-- LEFT JOIN licenses l ON ul.license_id = l.id
-- WHERE ul.action = 'parse_resume'
-- ORDER BY ul.created_at DESC;

-- 查询人才库（成功解析的简历）
-- SELECT 
--     candidate_name as "姓名",
--     candidate_phone as "电话",
--     candidate_email as "邮箱",
--     result_json->'基本信息'->>'年龄' as "年龄",
--     result_json->'工作经历'->0->>'岗位' as "当前岗位",
--     created_at as "入库时间"
-- FROM usage_logs
-- WHERE action = 'parse_resume' AND status = 'success'
-- ORDER BY created_at DESC;

-- 统计各版本使用量
-- SELECT 
--     app_version as "版本",
--     COUNT(*) as "解析次数",
--     COUNT(CASE WHEN status = 'success' THEN 1 END) as "成功次数",
--     COUNT(CASE WHEN status = 'error' THEN 1 END) as "失败次数"
-- FROM usage_logs
-- WHERE action = 'parse_resume'
-- GROUP BY app_version
-- ORDER BY app_version DESC;
