-- PetClinic schema (TRACE demo excerpt)
-- 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 Owner/Pet/Vet/Visit + 합성 Billing 도메인.
-- 의도적 충돌 맥락(Ground Truth):
--   * owners.telephone 은 VARCHAR(10)        -> 요구(20)와 불일치            (충돌 C-1)
--   * owners 에 email 컬럼 없음               -> 요구(email 필수) 미반영      (충돌 C-3)
--   * visits.description 은 VARCHAR(8192)     -> 명세(255)와 불일치           (충돌 C-4)
--   * invoices.amount 는 DECIMAL(8,2)         -> 명세 DECIMAL(10,2)와 불일치  (충돌 C-7)

CREATE TABLE IF NOT EXISTS owners (
    id         INTEGER      NOT NULL PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(30)  NOT NULL,
    last_name  VARCHAR(30)  NOT NULL,
    address    VARCHAR(255),        -- 충돌 C-8: 명세는 필수(NOT NULL)이나 여기서는 nullable
    city       VARCHAR(80),
    telephone  VARCHAR(10)          -- 충돌 C-1: 요구는 20자, 여기는 10자
    -- 충돌 C-3: email 컬럼 없음 (요구 email 필수 미반영)
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

CREATE TABLE IF NOT EXISTS vets (
    id         INTEGER     NOT NULL PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(30) NOT NULL,
    last_name  VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS specialties (
    id   INTEGER     NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(80)
);

-- 충돌 C-5: 명세는 수의사당 최소 1개 전문분야 필수이나, 스키마에 최소 개수 제약 없음(0행 허용).
CREATE TABLE IF NOT EXISTS vet_specialties (
    vet_id       INTEGER NOT NULL,
    specialty_id INTEGER NOT NULL,
    FOREIGN KEY (vet_id)       REFERENCES vets (id),
    FOREIGN KEY (specialty_id) REFERENCES specialties (id)
);

CREATE TABLE IF NOT EXISTS visits (
    id          INTEGER       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    visit_date  DATE          NOT NULL,   -- 충돌 C-6: 과거일자 예약 금지 제약 없음
    description VARCHAR(8192),            -- 충돌 C-4: 명세는 255자, 여기는 8192자
    pet_id      INTEGER       NOT NULL,
    FOREIGN KEY (pet_id) REFERENCES pets (id)
);

CREATE TABLE IF NOT EXISTS invoices (
    id        INTEGER       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    owner_id  INTEGER       NOT NULL,
    issued_on DATE          NOT NULL,
    amount    DECIMAL(8,2)  NOT NULL,     -- 충돌 C-7: 명세는 DECIMAL(10,2), 여기는 (8,2)
    FOREIGN KEY (owner_id) REFERENCES owners (id)
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id          INTEGER      NOT NULL PRIMARY KEY AUTO_INCREMENT,
    invoice_id  INTEGER      NOT NULL,
    description VARCHAR(255),
    amount      DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices (id)
);
