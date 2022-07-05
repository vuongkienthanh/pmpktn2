-- Bệnh nhân
CREATE TABLE IF NOT EXISTS patients (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  gender GENDER NOT NULL,
  birthdate DATE NOT NULL,
  address TEXT,
  phone TEXT,
  past_history TEXT -- bệnh nền
);

-- Danh sách chờ
CREATE TABLE IF NOT EXISTS queuelist (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    added_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (patient_id)
      REFERENCES patients (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- để search bn
CREATE INDEX IF NOT EXISTS patient_name
  ON patients (name);

-- Lượt khám
CREATE TABLE IF NOT EXISTS visits (
  id INTEGER PRIMARY KEY,
  exam_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
  diagnosis TEXT NOT NULL,
  weight DECIMAL NOT NULL,
  days INTEGER NOT NULL,
  recheck INTEGER NOT NULL,
  patient_id INTEGER NOT NULL,
  vnote TEXT, -- bệnh sử
  follow TEXT,
  FOREIGN KEY (patient_id)
    REFERENCES patients (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  CHECK (days >= 0 AND weight >=0 )
);

-- Kho thuốc
CREATE TABLE IF NOT EXISTS warehouse (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  element TEXT NOT NULL, -- thành phần thuốc
  quantity INTEGER NOT NULL, -- số lượng trong kho
  usage_unit TEXT NOT NULL, -- đơn vị sử dụng
  usage TEXT NOT NULL, -- cách sử dụng
  sale_unit TEXT, -- đơn vị bán
  purchase_price INTEGER NOT NULL,
  sale_price INTEGER NOT NULL,
  expire_date DATE,
  made_by TEXT,
  note TEXT,
  CONSTRAINT shortage_of_warehouse
    CHECK ( quantity >= 0 ),
  CONSTRAINT price_check 
    CHECK (( sale_price >= purchase_price) AND (purchase_price >= 0))
);

-- để search thuốc
CREATE INDEX IF NOT EXISTS drug_name
  ON warehouse(name);
CREATE INDEX IF NOT EXISTS drug_element 
  ON warehouse(element);

-- Toa thuốc
CREATE TABLE IF NOT EXISTS linedrugs (
  id INTEGER PRIMARY KEY,
  drug_id INTEGER NOT NULL,
  dose TEXT NOT NULL, -- liều 1 cữ
  times INTEGER NOT NULL,-- số cữ
  quantity INTEGER NOT NULL, -- số lượng bán ra
  visit_id INTEGER NOT NULL,
  note TEXT, -- thay thế cách dùng mặc định
  FOREIGN KEY (visit_id)
    REFERENCES visits (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  FOREIGN KEY (drug_id)
    REFERENCES warehouse (id)
      ON DELETE RESTRICT
      ON UPDATE NO ACTION,
  CHECK ( quantity > 0 AND times > 0 AND dose != '')
);

CREATE TABLE IF NOT EXISTS sampleprescription (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS linesampleprescription (
  id INTEGER PRIMARY KEY,
  drug_id INTEGER NOT NULL,
  sample_id INTEGER NOT NULL,
  dose TEXT NOT NULL,
  times INTEGER NOT NULL,
  FOREIGN KEY (drug_id)
    REFERENCES warehouse (id)
      ON DELETE RESTRICT
      ON UPDATE NO ACTION,
  FOREIGN KEY (sample_id)
    REFERENCES sample (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  CHECK (times > 0 AND dose != '')
);

CREATE TRIGGER IF NOT EXISTS linedrug_insert 
BEFORE INSERT ON linedrugs
BEGIN
UPDATE warehouse SET quantity = quantity - NEW.quantity
WHERE id = NEW.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_delete
BEFORE DELETE ON linedrugs
BEGIN
UPDATE warehouse SET quantity = quantity + OLD.quantity
WHERE id = OLD.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_update
BEFORE UPDATE ON linedrugs
WHEN NEW.drug_id = OLD.drug_id
BEGIN
UPDATE warehouse SET quantity = quantity + OLD.quantity - NEW.quantity
WHERE id = OLD.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS visit_insert
BEFORE INSERT ON visits
BEGIN
DELETE FROM queuelist WHERE patient_id = NEW.patient_id;
END;