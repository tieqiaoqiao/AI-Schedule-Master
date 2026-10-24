import os
import json
import pymysql
from pymysql.cursors import DictCursor  # 替代原来的 sqlite3.Row
from datetime import datetime
from contextlib import closing

# ============================================================
# 数据库配置：替换为你刚才连接成功的本地 MySQL 信息
# ============================================================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),       # 在 Docker 里会自动读取为 mysql_db
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'ai_agent_db'),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor # 注意：要确保你上面有 from pymysql.cursors import DictCursor
}

# ============================================================
# 获取数据库连接
# ============================================================
def get_db_connection():
    # 注意：pymysql 默认不自动提交，我们在执行 commit 时会手动提交
    conn = pymysql.connect(**DB_CONFIG)
    return conn

# ============================================================
# 初始化数据库：建 messages（消息）和 sessions（会话元数据）两张表
# ============================================================
def init_db():
    with closing(get_db_connection()) as conn:
        with conn.cursor() as cursor:
            # MySQL 建表：自增关键字改为 AUTO_INCREMENT，推荐使用 InnoDB 引擎
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    thread_id VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content LONGTEXT NOT NULL,
                    created_at VARCHAR(50) NOT NULL,
                    INDEX idx_thread_id (thread_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    thread_id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    uid VARCHAR(255),
                    updated_at VARCHAR(50) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        conn.commit()

# ============================================================
# 保存一条消息
# ============================================================
def save_message(thread_id: str, role: str, content: str):
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)
    with closing(get_db_connection()) as conn:
        try:
            with conn.cursor() as cursor:
                # 占位符改为 %s
                cursor.execute(
                    "INSERT INTO messages (thread_id, role, content, created_at) VALUES (%s, %s, %s, %s)",
                    (thread_id, role, content, datetime.now().isoformat(timespec="seconds")),
                )
            conn.commit()
        except Exception as e:
            conn.rollback()  # MySQL 写入失败时回滚，防止锁表
            print(f"保存消息失败: {e}")

# ============================================================
# 按 thread_id 读取全部历史消息
# ============================================================
def load_history(thread_id: str):
    with closing(get_db_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, thread_id, role, content, created_at FROM messages WHERE thread_id = %s ORDER BY id ASC",
                (thread_id,),
            )
            rows = cursor.fetchall()
    # 因为使用了 DictCursor，返回的已经是字典列表
    return rows

# ============================================================
# 查询所有出现过的 thread_id
# ============================================================
def load_all_thread_ids():
    with closing(get_db_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT thread_id FROM messages ORDER BY thread_id"
            )
            rows = cursor.fetchall()
    return [r["thread_id"] for r in rows]

# ============================================================
# 新增或更新会话元数据
# ============================================================
def upsert_session(thread_id: str, title: str, uid: str = None):
    with closing(get_db_connection()) as conn:
        try:
            with conn.cursor() as cursor:
                # MySQL 的 UPSERT 语法（ON DUPLICATE KEY UPDATE）与原逻辑完全一致
                cursor.execute("""
                    INSERT INTO sessions (thread_id, title, uid, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        title = VALUES(title),
                        uid = COALESCE(VALUES(uid), sessions.uid),
                        updated_at = VALUES(updated_at)
                """, (thread_id, title, uid, datetime.now().isoformat(timespec="seconds")))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"更新会话失败: {e}")

# ============================================================
# 读取单个会话的元数据
# ============================================================
def get_session(thread_id: str):
    with closing(get_db_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT thread_id, title, uid, updated_at FROM sessions WHERE thread_id = %s",
                (thread_id,),
            )
            row = cursor.fetchone()
    return row if row else None

# ============================================================
# 读取所有会话元数据（按更新时间倒序）
# ============================================================
def load_all_sessions():
    with closing(get_db_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT thread_id, title, uid, updated_at FROM sessions ORDER BY updated_at DESC"
            )
            rows = cursor.fetchall()
    return rows

# ============================================================
# 删除一个会话
# ============================================================
def delete_session(thread_id: str):
    with closing(get_db_connection()) as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM messages WHERE thread_id = %s", (thread_id,))
                cursor.execute("DELETE FROM sessions WHERE thread_id = %s", (thread_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"删除会话失败: {e}")