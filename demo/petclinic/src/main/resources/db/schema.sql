-- Spring PetClinic REST — 스키마 발췌 (데모용)
-- Owner 등록 관련 테이블. telephone 은 VARCHAR(10) 으로 정의된다.

CREATE TABLE IF NOT EXISTS owners (
    id         INTEGER IDENTITY PRIMARY KEY,
    first_name VARCHAR(30),
    last_name  VARCHAR(30),
    address    VARCHAR(255),
    city       VARCHAR(80),
    telephone  VARCHAR(10)      -- 전화번호 최대 10자리 (구현 기준)
);

CREATE INDEX owners_last_name ON owners (last_name);
