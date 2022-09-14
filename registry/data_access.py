import pymongo


def insert_services(services):
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
    registry_db = mongo_client['registry']
    services_col = registry_db['services']
    inserted_ids = services_col.insert_many(services)
    mongo_client.close()
    return inserted_ids


def remove_services():
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
    registry_db = mongo_client['registry']
    services_col = registry_db['services']
    deleted_ids = services_col.delete_many({})
    services_col.drop()
    mongo_client.close()
    return deleted_ids


def get_services(query):
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
    registry_db = mongo_client['registry']
    services_col = registry_db['services']
    cursor = services_col.find(query)
    services = []
    for service in cursor:
        services.append(service)
    mongo_client.close()
    return services
