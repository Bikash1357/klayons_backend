# Societies

## Get All Societies

Description: Get all registered societies.

### Request

Endpoint: `/core/societies`
Method: `POST`
Body: `None`
Required Body Fields: `[]`
Required Header Fields: `[]`

### Response

```json
{
    [
        {
        "id": 1,
        "name": "Shivalik",
        "city": "New Delhi",
        "state": "Delhi",
        "zipCode": "110017"
        },
        {
        "id": 2,
        "name": "GK-2",
        "city": "New Delhi",
        "state": "Delhi",
        "zipCode": "110048"
        },
        {
        "id": 3,
        "name": "IIT Delhi",
        "city": "New Delhi",
        "state": "Delhi",
        "zipCode": "110016"
        }
    ]
}
```
