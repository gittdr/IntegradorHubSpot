USE ControlPresupuestal
CREATE TABLE tbl_integr_hubSpot(
    id INT IDENTITY PRIMARY KEY,
    Close_Date DATETIME,
    Create_Date DATETIME,
    Nombre NVARCHAR(255),
    Deal_Stage NVARCHAR(80),
    Deal_Type NVARCHAR(100),
    Equipo_Colaborativo INT,
    Monto_forecast DECIMAL(18, 2),


    hs_lastmodifieddate DATETIME,
    dealname NVARCHAR(255),
    hs_is_closed_count BIT,
    hs_object_id BIGINT,
    industria NVARCHAR(100),
    numero_de_operadores INT,
    numero_de_unidades INT,
    operacion NVARCHAR(50),
    peso_ton DECIMAL(10, 2),
    semirremolques INT,
    sucursall NVARCHAR(100),
    tipo_de_operador NVARCHAR(50),
    tipo_de_viaje NVARCHAR(50),
    unidades NVARCHAR(100)  -- Puede quedar NULL o como INT si sabes que es numérico
);