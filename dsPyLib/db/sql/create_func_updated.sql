/*
    用于触发器更新表的updated字段值(更新时间)
 */

CREATE OR REPLACE FUNCTION "update_updated"()
    RETURNS TRIGGER AS
$$
BEGIN
    NEW.updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated IS '用于触发器更新表的updated字段值';