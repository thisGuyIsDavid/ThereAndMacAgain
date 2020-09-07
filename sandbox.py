import json
import datetime
from app.LocalDatabaseService import LocalDatabaseService

results = LocalDatabaseService().get_all_rows(
    """
    SELECT id, name FROM mac_individuals_bu WHERE name != ''
    """
)
print(results)

LocalDatabaseService().update_many(
    """
    UPDATE mac_individuals SET name = %(name)s WHERE id=%(id)s
    """,
    [
        {
            'id': result[0],
            'name': result[1]
        } for result in results
    ]
)