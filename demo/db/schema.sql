-- PetClinic schema (TRACE demo excerpt)
-- 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 Owner/Pet 만 발췌·개변.
-- 의도적 충돌 맥락:
--   * owners.telephone 은 VARCHAR(10)  -> 요구(20)와 불일치 (충돌 C-1)
--   * owners 에 email 컬럼 없음         -> 요구 REQ-2(email 필수) 미반영 (충돌 C-3)

CREATE TABLE IF NOT EXISTS owners (
    id         INTEGER      NOT NULL PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(30)  NOT NULL,
    last_name  VARCHAR(30)  NOT NULL,
    address    VARCHAR(255),
    city       VARCHAR(80),
    telephone  VARCHAR(10)          -- 충돌 C-1: 요구는 20자, 여기는 10자
    -- 충돌 C-3: email 컬럼 없음 (요구 REQ-2 미반영)
);

CREATE TABLE IF NOT EXISTS types (
    id   INTEGER     NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(80)
);

CREATE TABLE IF NOT EXISTS pets (
    id         INTEGER     NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name       VARCHAR(30) NOT NULL,
    birth_date DATE,                -- 충돌 C-2: 미래일자 제약을 스키마 차원에서 걸지 않음
    type_id    INTEGER     NOT NULL,
    owner_id   INTEGER     NOT NULL,
    FOREIGN KEY (type_id)  REFERENCES types (id),
    FOREIGN KEY (owner_id) REFERENCES owners (id)
);

CREATE INDEX IF NOT EXISTS idx_pets_owner ON pets (owner_id);
