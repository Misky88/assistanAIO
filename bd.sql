CREATE OR REPLACE PACKAGE toolkit AS
  FUNCTION encriptar    (p_texto IN VARCHAR2, p_clave IN VARCHAR2) RETURN RAW;
  FUNCTION desencriptar (p_raw   IN RAW, p_clave IN VARCHAR2)      RETURN VARCHAR2;
END toolkit;
/

CREATE OR REPLACE PACKAGE BODY toolkit AS
  g_pad_chr VARCHAR2(1) := '~';
  PROCEDURE padstring (p_texto IN OUT VARCHAR2);
  -- --------------------------------------------------
  FUNCTION encriptar (p_texto IN VARCHAR2, p_clave IN VARCHAR2) RETURN RAW IS
  -- --------------------------------------------------
  l_texto      VARCHAR2(32767) := p_texto;
  g_key        RAW(32767)      := UTL_RAW.cast_to_raw(p_clave);
  l_encriptado RAW(32767);
  BEGIN
    padstring(l_texto);
    DBMS_OBFUSCATION_TOOLKIT.desencrypt(input          => UTL_RAW.cast_to_raw(l_texto),
                                        key            => g_key,
                                        encrypted_data => l_encriptado);
    RETURN l_encriptado;
  END;
  -- --------------------------------------------------

  -- --------------------------------------------------
  FUNCTION desencriptar (p_raw IN RAW, p_clave in VARCHAR2) RETURN VARCHAR2 IS
  -- --------------------------------------------------
  l_desencriptado VARCHAR2(32767);
  g_key           RAW(32767) := UTL_RAW.cast_to_raw(p_clave);
  BEGIN
    if p_raw is not null then 
        DBMS_OBFUSCATION_TOOLKIT.desdecrypt(input => p_raw,
                                            key   => g_key,
                                            decrypted_data => l_desencriptado);
    end if;
    RETURN RTrim(UTL_RAW.cast_to_VARCHAR2(l_desencriptado), g_pad_chr);
  END;
  -- --------------------------------------------------

  -- --------------------------------------------------
  PROCEDURE padstring (p_texto IN OUT  VARCHAR2) IS
  -- --------------------------------------------------
  l_unidades NUMBER;
  BEGIN
    IF LENGTH(p_texto) MOD 8 > 0 THEN
      l_unidades := TRUNC(LENGTH(p_texto)/8) + 1;
      p_texto    := RPAD(p_texto, l_unidades * 8, g_pad_chr);
    END IF;
  END;
  -- --------------------------------------------------
END toolkit;
/

/* SECUENCIAS */
CREATE SEQUENCE   "CLIENTES_SEQ"  MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE
/
CREATE SEQUENCE   "USUARIOS_SEQ"  MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE
/
CREATE SEQUENCE   "EMPRESAS_SEQ"  MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE
/

/* FUNCIONES */
create or replace FUNCTION AUTENTIFICACION (p_username IN VARCHAR2,  
                                        p_password IN VARCHAR2)  
RETURN BOOLEAN  
IS  
    l_clave_alm VARCHAR2(4000);  
    l_count     NUMBER;      
BEGIN  
    SELECT COUNT(*) INTO l_count FROM USUARIOS  
    WHERE upper(usu_nombre) = upper(p_username);  
    apex_debug.message('Usuario: '||p_username||', Clave: '||p_password||', Count: '||l_count);
    IF l_count > 0 THEN
        SELECT usu_clave  
        INTO l_clave_alm  
        FROM USUARIOS  
        WHERE upper(usu_nombre) = upper(p_username);  
        IF toolkit.encriptar(p_password,'AIO987654') = l_clave_alm THEN
            RETURN TRUE;
        ELSE RETURN FALSE;
        END IF;
    ELSE RETURN FALSE;
    END IF;  
END;

/* TABLAS */
CREATE TABLE  "CLIENTES" 
   (	"CLI_ID" NUMBER(10,0) NOT NULL ENABLE, 
	"CLI_DNI" VARCHAR2(20), 
	"CLI_NOMBRE" VARCHAR2(255), 
	"CLI_CLAVE" VARCHAR2(255), 
	"CLI_ACTIVO" VARCHAR2(1), 
	"CLI_EMAIL" VARCHAR2(255), 
	"CLI_TELEFONO" VARCHAR2(255), 
	"CLI_DIRECCION" VARCHAR2(255), 
	"CLI_TIPO" VARCHAR2(1), 
	"CLI_EMPRESA" NUMBER(10,0), 
	 CONSTRAINT "CLIENTES_PK" PRIMARY KEY ("CLI_ID") ENABLE
   )
/

CREATE OR REPLACE TRIGGER  "BI_CLIENTES" 
  before insert on "CLIENTES"               
  for each row  
begin   
  if :NEW."CLI_ID" is null then 
    select "CLIENTES_SEQ".nextval into :NEW."CLI_ID" from sys.dual; 
  end if; 
end; 

/
ALTER TRIGGER  "BI_CLIENTES" ENABLE
/

CREATE TABLE  "EMPRESAS" 
   (	"EMP_ID" NUMBER(10,0), 
	"EMP_NOMBRE" VARCHAR2(50), 
	"EMP_CAPACIDAD" NUMBER(10,2), 
	"EMP_USADO" NUMBER(10,2), 
	"EMP_ESTADO" VARCHAR2(30), 
	 CONSTRAINT "EMPRESAS_PK" PRIMARY KEY ("EMP_ID") ENABLE
   )
/

CREATE OR REPLACE TRIGGER  "BI_EMPRESAS" 
  before insert on "EMPRESAS"               
  for each row  
begin   
  if :NEW."EMP_ID" is null then 
    select "EMPRESAS_SEQ".nextval into :NEW."EMP_ID" from sys.dual; 
  end if; 
end; 

/
ALTER TRIGGER  "BI_EMPRESAS" ENABLE
/

CREATE TABLE  "USUARIOS" 
   (	"USU_ID" NUMBER(10,0), 
	"USU_NOMBRE" VARCHAR2(255), 
	"USU_CLAVE" VARCHAR2(255), 
	"USU_TIPO" VARCHAR2(1), 
	 CONSTRAINT "USUARIOS_PK" PRIMARY KEY ("USU_ID") ENABLE
   )
/

CREATE OR REPLACE TRIGGER  "BI_USUARIOS" 
  before insert on "USUARIOS"               
  for each row  
begin   
  if :NEW."USU_ID" is null then 
    select "USUARIOS_SEQ".nextval into :NEW."USU_ID" from sys.dual; 
  end if; 
end; 

/
ALTER TRIGGER  "BI_USUARIOS" ENABLE
/

CREATE TABLE  "EQUIPOS" 
   (	"EQU_ID" NUMBER(10,0), 
	"EQU_EMP" NUMBER(10,0), 
	"EQU_NOMBRE" VARCHAR2(30), 
	"EQU_IP" VARCHAR2(15), 
	"EQU_UBICACION" VARCHAR2(100), 
	"EQU_ACTIVO" VARCHAR2(1), 
	"EQU_ESTADO" VARCHAR2(30), 
	 CONSTRAINT "EQUIPOS_PK" PRIMARY KEY ("EQU_ID") ENABLE
   )
/

CREATE OR REPLACE TRIGGER  "BI_EQUIPOS" 
  before insert on "EQUIPOS"               
  for each row  
begin   
  if :NEW."EQU_ID" is null then 
    select "EQUIPOS_SEQ".nextval into :NEW."EQU_ID" from sys.dual; 
  end if; 
end; 

/
ALTER TRIGGER  "BI_EQUIPOS" ENABLE
/