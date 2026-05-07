-- PixelShare – Azure SQL Schema
-- Run this in Azure SQL Query Editor after creating your database

CREATE TABLE Users (
    userId      VARCHAR(50)  PRIMARY KEY DEFAULT NEWID(),
    email       VARCHAR(255) NOT NULL UNIQUE,
    displayName VARCHAR(100) NOT NULL,
    createdAt   DATETIME2    NOT NULL DEFAULT GETUTCDATE(),
    isActive    BIT          NOT NULL DEFAULT 1
);

CREATE TABLE MediaAuditLog (
    logId       INT          IDENTITY(1,1) PRIMARY KEY,
    mediaId     VARCHAR(50)  NOT NULL,
    userId      VARCHAR(50)  NOT NULL,
    action      VARCHAR(20)  NOT NULL,  -- 'UPLOAD', 'UPDATE', 'DELETE'
    actionAt    DATETIME2    NOT NULL DEFAULT GETUTCDATE(),
    details     NVARCHAR(MAX)
);

-- Insert a default test user
INSERT INTO Users (email, displayName)
VALUES ('raduan@pixelshare.com', 'Raduan Islam');

-- View all users
-- SELECT * FROM Users;
-- View audit log
-- SELECT * FROM MediaAuditLog ORDER BY actionAt DESC;
