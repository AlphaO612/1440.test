\c tickets_1440;

CREATE TABLE IF NOT EXISTS status_enum (
    status VARCHAR(53) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS type_enum (
    type VARCHAR(53) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Users (
    id VARCHAR(53) PRIMARY KEY,
    access_token VARCHAR(255),
    dt_token_update TIMESTAMPTZ,
    expire_in INTERVAL,
    email VARCHAR(128) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Tickets(
    guid_ticket UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author VARCHAR(53) REFERENCES Users(id),
    status VARCHAR(53) REFERENCES status_enum(status)
);

CREATE TABLE IF NOT EXISTS Actions (
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(53) REFERENCES type_enum(type),
    guid_ticket UUID REFERENCES Tickets(guid_ticket),
    author VARCHAR(53) REFERENCES Users(id),
    data JSONB
);

CREATE INDEX IF NOT EXISTS idx_user_access_token ON Users (access_token);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON Tickets (status);
CREATE INDEX IF NOT EXISTS idx_actions_timestamp ON Actions (timestamp);


INSERT INTO "status_enum" (status)
VALUES ('open'),
       ('processing'),
       ('closed_success'),
       ('closed_fail')
ON CONFLICT (status) DO NOTHING;

INSERT INTO "type_enum" (type)
VALUES ('open_ticket'),
       ('log_in'),
       ('change_state'),
       ('error')
ON CONFLICT (type) DO NOTHING;

CREATE OR REPLACE FUNCTION insert_into_actions()
RETURNS TRIGGER AS $$
BEGIN

    INSERT INTO Actions (author, type, guid_ticket, data)
    VALUES (NEW.author, 'open_ticket', NEW.guid_ticket, NULL);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_insert_into_actions
AFTER INSERT ON Tickets
FOR EACH ROW
EXECUTE FUNCTION insert_into_actions();

-- todo It can't be done, cuz u won't be able to verify the person who did it! but interesting code ^-^
-- CREATE OR REPLACE FUNCTION update_tickets_status()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     IF OLD.status != NEW.status THEN
--         INSERT INTO Actions (author, type, guid_ticket, data)
--         VALUES (NEW.author, 'change_state', NEW.guid_ticket,
--         to_json(concat('{"old_status":"', OLD.status, '", "new_status":"', NEW.status, '"}'::text)));
--     END IF;
--
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER trigger_update_tickets_status
-- AFTER UPDATE ON Tickets
-- FOR EACH ROW
-- EXECUTE FUNCTION update_tickets_status();