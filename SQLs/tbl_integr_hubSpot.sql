/*
El siguiente script tiene como objetivo poder generar la estructura de las tablas de la integracion con HubSpot
*/
USE AplicativosTDR
GO

DELETE [dbo].[tbl_integr_hubSpot_deals]
GO
-- DELETE [dbo].[tbl_integr_hubspot_pipelines]
-- GO
DELETE [dbo].[tbl_integr_hubspot_objects]
GO

CREATE TABLE [dbo].[tbl_integr_hubSpot_deals](
	[Id] [nvarchar](50) PRIMARY KEY NOT NULL,
	[Nombre] [nvarchar](255) NULL,
	[Create_Date] [datetime] NULL,
	[Close_Date] [datetime] NULL,
	[Deal_Stage] [nvarchar](80) NULL,
	[Pipeline] [nvarchar](80) NULL,
	[Deal_Type] [nvarchar](100) NULL,
	[Equipo_Colaborativo] [int] NULL,
	[Monto_forecast] [decimal](18, 2) NULL,
	[Is_Closed] [bit] NULL,
	[Last_Modified_Date] [datetime] NULL,
	[Industria] [nvarchar](100) NULL,
	[Numero_de_Operadores] [int] NULL,
	[Numero_de_Unidades] [int] NULL,
	[Operacion] [nvarchar](50) NULL,
	[Peso] [decimal](10, 2) NULL,
	[Semirremolques] [int] NULL,
	[Sucursal] [nvarchar](100) NULL,
	[Tipo_de_Operador] [nvarchar](50) NULL,
	[Tipo_de_Viaje] [nvarchar](50) NULL,
	[Deal_Owner] [nvarchar](50) NULL,
	[Deal_Owner_id] [bigint] NULL,
	CONSTRAINT FK_DEALS_OBJECTS FOREIGN KEY (Id)
		REFERENCES tbl_integr_hubspot_objects(Id)
)
GO


-- CREATE TABLE [dbo].[tbl_integr_hubspot_pipelines](
-- 	[Id] [int] PRIMARY KEY,
-- 	[Label] [nvarchar] (40),
-- 	[Pipeline] [nvarchar] (100),
-- 	[Pipeline_Id] [nvarchar] (40)
-- )
-- GO

CREATE TABLE [dbo].[tbl_integr_hubspot_objects](
	[Id] [nvarchar](50) PRIMARY KEY,
	[emails] [int] NOT NULL,
	[meetings] [int] NOT NULL,
	[calls] [int] NOT NULL,
	CONSTRAINT FK_OBJECTS_DEALS FOREIGN KEY(Id)
		REFERENCES tbl_integr_hubSpot_deals(Id)
)
GO