create database carmesamadb;
GRANT ALL PRIVILEGES ON carmesamadb.* to ohgiraffers@'%';
USE carmesamadb;

-- 지역 테이블 생성
CREATE TABLE IF NOT EXISTS tbl_region
(
    REG_ID            INT NOT NULL AUTO_INCREMENT COMMENT '지역번호',
    REGION            VARCHAR(50) NOT NULL COMMENT '지역',
    SUBREGION         VARCHAR(50) NOT NULL COMMENT '시군구',
    CONSTRAINT pk_region PRIMARY KEY (REG_ID)
) ENGINE=INNODB COMMENT '지역';

-- 인구 테이블 생성
CREATE TABLE IF NOT EXISTS tbl_population
(
    REG_ID            INT NOT NULL COMMENT '지역번호',
    YEAR              INT NOT NULL COMMENT '년도',
    POPULATION        INT NOT NULL COMMENT '인구수',
    CONSTRAINT pk_region PRIMARY KEY (REG_ID, YEAR),
	CONSTRAINT fk_region FOREIGN KEY (REG_ID) REFERENCES tbl_region (REG_ID)
) ENGINE=INNODB COMMENT '인구';

-- 자동차 테이블 생성
CREATE TABLE IF NOT EXISTS tbl_car
(
    REG_ID            INT NOT NULL COMMENT '지역번호',
    YEAR              INT NOT NULL COMMENT '년도',
    CAR               INT NOT NULL COMMENT '자동차수',
    CONSTRAINT pk_car PRIMARY KEY (REG_ID, YEAR),
	CONSTRAINT fk_car FOREIGN KEY (REG_ID) REFERENCES tbl_region (REG_ID)
) ENGINE=INNODB COMMENT '자동차';

-- 매장 테이블 생성
CREATE TABLE IF NOT EXISTS tbl_supplier
(
    SUP_ID            INT NOT NULL AUTO_INCREMENT COMMENT '매장번호',
    REG_ID            INT NOT NULL COMMENT '지역번호',
    YEAR              INT NOT NULL COMMENT '년도',
    SUPPLIER          VARCHAR(50) NOT NULL COMMENT '매장명',
    CONSTRAINT pk_supplier PRIMARY KEY (SUP_ID),
	CONSTRAINT fk_supplier FOREIGN KEY (REG_ID) REFERENCES tbl_region (REG_ID)
) ENGINE=INNODB COMMENT '매장';

-- 가맹점 테이블 생성
CREATE TABLE IF NOT EXISTS tbl_vendor
(
    VENDOR_NAME       VARCHAR(100) NOT NULL COMMENT '매장명',
    ADDRESS           VARCHAR(255) NOT NULL COMMENT '주소',
    PHONE             VARCHAR(50) NOT NULL COMMENT '전화번호',
    CONSTRAINT pk_vendor PRIMARY KEY (VENDOR_NAME)
) ENGINE=INNODB COMMENT '가맹점';

-- FAQ 테이블 생성
CREATE TABLE IF NOT EXISTS tbl_faq
(
    FAQ_ID            INT NOT NULL AUTO_INCREMENT COMMENT 'FAQ번호',
    CATEGORY          VARCHAR(50) NOT NULL COMMENT '카테고리',
    QUESTION          VARCHAR(50) NOT NULL COMMENT '질문',
    ANSWER            VARCHAR(1000) NOT NULL COMMENT '답변',
    CONSTRAINT pk_faq PRIMARY KEY (FAQ_ID)
) ENGINE=INNODB COMMENT 'FAQ';