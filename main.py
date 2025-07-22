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

def get_deals_data(url_endpoint):
    paging = True
    page = ''
    deals = []
    deals_objects = []
    pipelines_por_ejecutar = []
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
        
        pipeline_url = os.getenv("API_URL") + os.getenv("API_PIPELINES_ENDPOINT")
        # get_deals_pipelines(pipeline_url)
        pipelines = get_deals_pipelines(pipeline_url)
        
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
                    
                    for pipeline in pipelines:
                        for stage in pipeline.get('data', []):
                            if propierties.get("dealstage") == stage.get('id'):
                                pipeline_id = pipeline.get('pipeline', 'Unknown Pipeline')
                                stage_label = stage.get('label', 'Unknown Stage')
                                break

                    data = {
                        "Id": propierties["hs_object_id"],
                        "Nombre": propierties["dealname"],
                        "Create_Date": safe_datetime(propierties.get("createdate")),
                        "Close_Date": safe_datetime(propierties.get("closedate")),
                        "Deal_Stage": stage_label,
                        "Pipeline": pipeline_id,
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
                    deals.append(data)


                    # Obtain deal objects
                    if pipeline_id == 'Pipeline de ventas' and stage_label != 'Cierre perdido':
                        deals_objects.append(propierties["hs_object_id"])
                        # deal_objects = get_deals_objects(os.getenv("API_URL"), propierties["hs_object_id"])
                        # deals_objects.append(deal_objects)
                        # count += 1
                        # print(count)

                # Check if there is a next page
                pagination = results.json().get('paging')
                if not pagination:
                    paging = False
                else:
                    page = f'&after={pagination["next"]["after"]}'
        
        save_to_file(deals, 'deals.json')
        save_to_database(deals, os.getenv("QUERY_INSERT_DEAL"))
        # save_to_file(deals_objects, 'deals_objects.json')
        return deals_objects
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
            pipeline_data = {
                "pipeline": pipeline.get('label', 'Unknown'),
                "data": []
            }
            for stage in stages:
                data = {
                    "id": stage.get('id', 'Unknown'),
                    "label": stage.get('label', 'Unknown')
                }
                # data = {
                #     "Id": stage.get('id', 'Unknown'),
                #     "Label": stage.get('label', 'Unknown'),
                #     "Pipeline": pipeline.get('label', 'Unknown'),
                #     "Pipeline_Id": pipeline.get('id', 'Unknown')
                # }
                # pipeline_data[pipeline.get('label', 'Unknown')].extend(data)
                pipeline_data["data"].append(data)
            return_data.append(pipeline_data)


        # save_to_file(pipelines, 'pipelines.json')
        # save_to_database(return_data, os.getenv("QUERY_INSERT_PIPELINE"))
        
        
        # save_to_file(return_data, 'pipelines.json')
        return return_data
    except Exception as e:
        print(f"Error fetching deal pipelines: {e}")
        return {}

def get_deals_objects(url, deal_id):
    """
    Fetch deal objects from HubSpot API.
    :return: JSON response containing deal objects.
    """
    
    objects = ['emails', 'meetings', 'calls']
    header = {
        'Authorization': f'Bearer {os.getenv("API_TOKEN")}',
    }
    object_names = []
    try:
        for obj in objects:
            paging = True
            page = ''
            count = 0
            while paging:
                url_endpoint = f"{url}/crm/v4/objects/deals/{deal_id}/associations/{obj}?limit=500{page}"
                response = requests.get(url_endpoint, headers=header)
                for object_result in response.json().get('results', []):
                    count += 1
                
                # Check if there is a next page
                pagination = response.json().get('paging')
                if not pagination:
                    paging = False
                else:
                    page = f'&after={pagination["next"]["after"]}'
                    
            data = {
                obj : count
            }
            object_names.append(data)
            
        object_numbers = {
            "deal_id": deal_id,
            "emails": object_names[0].get('emails', 0),
            "meetings": object_names[1].get('meetings', 0),
            "calls": object_names[2].get('calls', 0)
        }
        
        # save_to_file(object_numbers, 'objects.json')
        # save_to_database(object_names, os.getenv("QUERY_INSERT_OBJECTS"))
        
        
        
        return object_numbers
    except Exception as e:
        print(f"Error fetching deal objects: {e}")
        return {}

def save_to_database(data, query):
    """
    Save the fetched data to a database.
    :param data: The data to save.
    """
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
            data1 = registro.values()
            cursor.execute(query, tuple(registro.values()))
        # Confirmar cambios
        conn.commit()
        print("Datos insertados correctamente en SQL Server.")

    except Exception as e:
        print("Error al guardar en SQL Server:", e)

    finally:
        # Cerrar conexión
        conn.close()

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
    
deals_url = os.getenv("API_URL") + os.getenv("API_DEALS_ENDPOINT") + os.getenv("API_DEALS_PARAMS")
estatus = get_deals_data(deals_url)
object_deals = []
count = 0
for deal in estatus:
    print(deal + " - " + str(count))
    count += 1
    object_deals.append(get_deals_objects(url, deal))
save_to_file(object_deals, 'deals_objects.json')
save_to_database(object_deals, os.getenv("QUERY_INSERT_OBJECTS"))




# pipeline_url = os.getenv("API_URL") + os.getenv("API_PIPELINES_ENDPOINT")
# get_deals_pipelines(pipeline_url)


# get_deals_objects(url, '39978390407')

# url_endpoint = f"{url}{endpoint}{os.getenv('API_PARAMS1')}"
# estatus = get_deals_data(url_endpoint)
# save_to_database(estatus["data"])
# with open('estatus.json', 'w', encoding='utf-8') as f:
#     json.dump(estatus, f, indent=4, ensure_ascii=False)
# print("Data fetched and saved to estatus.json")
# print(estatus["data"][1]["propiedades"]["industria"])
