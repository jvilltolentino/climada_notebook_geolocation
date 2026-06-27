from climada.util.api_client import Client
import inspect

c = Client()
print('get_hazard signature:')
print(inspect.signature(c.get_hazard))
print()
print('list_dataset_infos signature:')
print(inspect.signature(c.list_dataset_infos))
print()

# Try to list available datasets
try:
    infos = c.list_dataset_infos(data_type='hazard', name='river_flood')
    print('River flood datasets:')
    for info in infos[:5]:
        print(' ', info)
except Exception as e:
    print(f'Error: {e}')
