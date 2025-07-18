import requests
import os
import json
import sys
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
# Load environment variables from .env file
load_dotenv()

url = os.getenv("API_URL") 
endpoint = os.getenv("API_ENDPOINT")

def get_deals_data(url_endpoint):
    paging = True
    page = ''
    estatus = []
    """
    Fetch data from HubSpot API.
    :param api_key: Your HubSpot API key.
    :param endpoint: The specific API endpoint to query.
    :return: JSON response from the HubSpot API.
    """
    
    header = {
        'Authorization': f'Bearer {os.getenv("API_TOKEN")}',
    }
    url_owners = os.getenv("API_URL") + os.getenv("API_OWNERS_ENDPOINT") + os.getenv("API_OWNERS_PARAMS")
    owners = get_deal_owners(url_owners)
    try:
        
        while paging:
            url = f"{url_endpoint}{page}"
            results = requests.get(url, headers=header)
            if results.status_code == 200:
                for result in results.json().get('results'):
                    propierties = result.get("properties", {})
                    owner_id = propierties.get("hubspot_owner_id")
                    deal_owner = owners.get(owner_id, "Unknown Owner")
                    # print(result)
                    # if result["properties"]["hs_is_closed_count"] == "0":
                    #     data = {
                    #         "nombre": result["properties"]["dealname"],
                    #         "propiedades" : result["properties"],
                    #     }
                    #     estatus["data"].append(data)
                        
                    data = {
                        "Id_Objeto": propierties["hs_object_id"],
                        "Nombre": propierties["dealname"],
                        "Create_Date": safe_datetime(propierties.get("createdate")),
                        "Close_Date": safe_datetime(propierties.get("closedate")),
                        "Deal_Stage": propierties.get("dealstage"),
                        "Deal_Type": propierties.get("dealtype"),
                        "Equipo_Colaborativo": safe_int(propierties.get("equipo_colaborativo")),
                        "Monto_forecast": safe_float(propierties.get("hs_forecast_amount")),
                        "Is_Closed": safe_int(propierties.get("hs_is_closed_count")),
                        "Last_Modified_Date": safe_datetime(propierties.get("hs_lastmodifieddate")),
                        "Industria": propierties.get("industria"),
                        "Numero_de_Operadores": safe_int(propierties.get("numero_de_operadores")),
                        "Numero_de_Unidades": safe_int(propierties.get("numero_de_unidades")),
                        "Operacion": propierties.get("operacion"),
                        "Peso": safe_float(propierties.get("peso__ton_")),
                        "Semirremolques": safe_int(propierties.get("semirremolques")),
                        "Sucursal": propierties.get("sucursall"),
                        "Tipo_de_Operador": propierties.get("tipo_de_operador"),
                        "Tipo_de_Viaje": propierties.get("tipo_de_viaje"),
                        "Deal_owner": deal_owner,
                        "Deal_owner_id": safe_int(propierties.get("hubspot_owner_id"))
                    }
                    estatus.append(data)

                # Check if there is a next page
                pagination = results.json().get('paging')
                if not pagination:
                    paging = False
                else:
                    page = f'&after={pagination["next"]["after"]}'
        save_to_file(estatus, 'estatus.json')
        # return estatus
    except Exception as e:
        print(f"Error fetching data: {e}")
        results.raise_for_status()  # Raise an error for bad responses

def get_deal_owners(url_endpoint):
    owners = {}
    header = {
        'Authorization': f'Bearer {os.getenv("API_TOKEN")}',
    }
    try:
        url = f"{url_endpoint}{os.getenv('API_PARAMS2')}"
        results = requests.get(url, headers=header)
        for result in results.json().get('results'):
            name = result.get("firstName", "").strip() + " " + result.get("lastName", "").strip()
            owners[result.get("id")] = name
        with open('owners.json', 'w', encoding='utf-8') as f:
            json.dump(owners, f, indent=4, ensure_ascii=False)
        # print(owners)
        return owners
    except Exception as e:
        print(f"Error fetching deal owners: {e}")
        return owners

def get_deals_pipelines(url_endpoint):
    """
    Fetch deal pipelines from HubSpot API.
    :param url_endpoint: The API endpoint to query.
    :return: JSON response containing deal pipelines.
    """
    return_data = []
    header = {
        'Authorization': f'Bearer {os.getenv("API_TOKEN")}',
    }
    try:
        results = requests.get(url_endpoint, headers=header)
        results.raise_for_status()  # Raise an error for bad responses
        pipelines = results.json().get('results', [])
        
        for pipeline in pipelines:
            stages = pipeline.get('stages', [])
            for stage in stages:
                # data = {
                #     stage.get('id', 'Unknown'): stage.get('label', 'Unknown')
                # }
                data = {
                    "id": stage.get('id', 'Unknown'),
                    "label": stage.get('label', 'Unknown'),
                    "id_pipeline": pipeline.get('id', 'Unknown'),
                    "label_pipeline": pipeline.get('label', 'Unknown')
                }
                return_data.append(data)

        save_to_file(return_data, 'pipelines.json')
        # save_to_file(pipelines, 'pipelines.json')
        return results.json()
    except Exception as e:
        print(f"Error fetching deal pipelines: {e}")
        return {}

def save_deals_to_database(data):
    """
    Save the fetched data to a database.
    :param data: The data to save.
    """
    url_owners = os.getenv("API_URL") + os.getenv("API_OWNERS_URL") + os.getenv("API_PARAMS2")
    owners = get_deal_owners(url_owners)
    try:
        # Establecer conexión a SQL Server
        conn = pyodbc.connect(
            f'DRIVER={os.getenv("BD_DRIVER")};'
            f'SERVER={os.getenv("bd_server")};'
            f'DATABASE={os.getenv("bd_database")};'
            f'UID={os.getenv("bd_username")};'
            f'PWD={os.getenv("bd_password")}'
        )
        cursor = conn.cursor()

        # Insertar los registros
        for registro in data:
            deal = registro["propiedades"]
            owner_id = deal.get("hubspot_owner_id")
            deal_owner = owners.get(owner_id, "Unknown Owner")
            cursor.execute("""
                INSERT INTO tbl_integr_hubSpot (
                    Id_Objeto,
                    Nombre,
                    Create_Date,
                    Close_Date,
                    Deal_Stage,
                    Deal_Type,
                    Equipo_Colaborativo,
                    Monto_forecast,
                    Is_Closed,
                    Last_Modified_Date,
                    Industria,
                    Numero_de_Operadores,
                    Numero_de_Unidades,
                    Operacion,
                    Peso,
                    Semirremolques,
                    Sucursal,
                    Tipo_de_Operador,
                    Tipo_de_Viaje,
                    Deal_owner,
                    Deal_owner_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                safe_datetime(deal.get("closedate")),
                safe_datetime(deal.get("createdate")),
                deal.get("dealname"),
                safe_deal_stage(deal.get("dealstage")),
                deal.get("dealtype"),
                safe_int(deal.get("equipo_colaborativo")),
                safe_float(deal.get("hs_forecast_amount")),
                safe_int(deal.get("hs_is_closed_count")),
                safe_datetime(deal.get("hs_lastmodifieddate")),
                safe_int(deal.get("hs_object_id")),
                deal.get("industria"),
                safe_int(deal.get("numero_de_operadores")),
                safe_int(deal.get("numero_de_unidades")),
                deal.get("operacion"),
                safe_float(deal.get("peso__ton_")),
                safe_int(deal.get("semirremolques")),
                deal.get("sucursall"),
                deal.get("tipo_de_operador"),
                deal.get("tipo_de_viaje"),
                deal_owner,
                safe_int(deal.get("hubspot_owner_id"))
            ))
            
        # Confirmar cambios
        conn.commit()
        print("Datos insertados correctamente en SQL Server.")

    except Exception as e:
        print("Error al guardar en SQL Server:", e)

    finally:
        # Cerrar conexión
        conn.close()

def safe_deal_stage(deal_stage):
    """
    Safely convert a deal stage to a string, returning 'Unknown' if conversion fails.
    :param deal_stage: The deal stage to convert.
    :return: The converted deal stage or 'Unknown' if conversion fails.
    """
    deals = {
        "3020163": "Lead",
        "8594776" : "Por Arrancar",
        "8594777" : "Cliente",
        "qualifiedtobuy" : "Lead Autorizado",
        "presentationscheduled" : "Negociacion",
        "42501700" : "Lead No Autorizado",
        "contractsent" : "Proceso de alta",
        "42501702" : "Firma Cotización",
        "decisionmakerboughtin" : "Contrato",
        "42501701": "Tarifa",
        "closedwon" : "Cierre comercial",
        "appointmentscheduled" : "Formato de cotización",
        "closedlost" : "Cierre perdido",
        "39686207" : "Inactivo"
    }
    if deal_stage in deals:
        return deals[deal_stage]
    try:
        return str(deal_stage)
    except (ValueError, TypeError):
        return 'Unknown'

def safe_int(value):
    """
    Safely convert a value to an integer, returning 0 if conversion fails.
    :param value: The value to convert.
    :return: The converted integer or 0 if conversion fails.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        # print(f"Error converting {value} to int, returning 0")
        return 0

def safe_float(value):
    """
    Safely convert a value to a float, returning 0.0 if conversion fails.
    :param value: The value to convert.
    :return: The converted float or 0.0 if conversion fails.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def safe_datetime(value):
    """
    Safely convert a value to a datetime object, returning None if conversion fails.
    :param value: The value to convert.
    :return: The converted datetime object or None if conversion fails.
    """
    try:
        if not value:
            return None
        date = datetime.fromisoformat(value.replace("Z", ""))
        date_sql = date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return date_sql
    except (ValueError, TypeError):
        return None

def save_to_file(data, filename):
    """
    save data to a JSON file.
    :param data: the data to be saved,
    :param filename: the name of the file to save the data, contains the extenion .json
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# pipeline_url = os.getenv("API_URL") + os.getenv("API_PIPELINES_ENDPOINT")
# get_deals_pipelines(pipeline_url)

deals_url = os.getenv("API_URL") + os.getenv("API_DEALS_ENDPOINT") + os.getenv("API_DEALS_PARAMS")
estatus = get_deals_data(deals_url)

# url_endpoint = f"{url}{endpoint}{os.getenv('API_PARAMS1')}"
# estatus = get_deals_data(url_endpoint)
# save_to_database(estatus["data"])
# with open('estatus.json', 'w', encoding='utf-8') as f:
#     json.dump(estatus, f, indent=4, ensure_ascii=False)
# print("Data fetched and saved to estatus.json")
# print(estatus["data"][1]["propiedades"]["industria"])
