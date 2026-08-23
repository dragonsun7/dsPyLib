/*
 为表添加触发器，用于更新updated(更新时间)字段
 用真实的表名替换table_name
 */
DROP TRIGGER IF EXISTS updated ON __table_name__;
CREATE TRIGGER updated
    BEFORE UPDATE
    ON __table_name__
    FOR EACH ROW
EXECUTE PROCEDURE update_updated();
