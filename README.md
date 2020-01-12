# Data Enrichment Service
Adds the number of school in the vicinity of a given location, based on data from [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Main_Page).

# Prerequisites
- Docker

# Usage
## Initializing the Server
```bash
docker-compose -p enrichment build && docker-compose -p enrichment up
```

The server runs on `http://localhost:80/`

## Example Payload
```json
POST /api/enrich
{
    "data": [
        {
            "Suburb": "Footscray",
            "Rooms": 3,
            "Date": "2016-03-12",
            "Postcode": 3011,
            "Bedroom2": 3,
            "Bathroom": 1,
            "Car": 1,
            "Landsize": 292,
            "YearBuilt": 1900,
            "Latitude": -37.797,
            "Longitude": 144.9051,
            "Address": "9 Lynch St 3011, Melbourne, Australia"
        }
    ]
}
```

## Example Response
```json
{
    "data": [
        {
            "Suburb": "Footscray",
            "Rooms": 3,
            "Date": "2016-03-12",
            "Postcode": 3011,
            "Bedroom2": 3,
            "Bathroom": 1,
            "Car": 1,
            "Landsize": 292,
            "YearBuilt": 1900,
            "Latitude": -37.797,
            "Longitude": 144.9051,
            "Address": "9 Lynch St 3011, Melbourne, Australia",
            "Schools": 4
        }
    ]
}
```


## Error Handling
If an error occured during handling of the dataset, an "Errors" element will be added with list of faulty data-points and their respective errors.

```json
REQUEST 
{
    "data": [
        {
            "Suburb": "Footscray",
            "Rooms": 3,
            ...
            "Latitude": -192,
            "Longitude": 144.9051,
        }
    ]
}

RESPONSE
REQUEST 
{
    "data": [
        {
            "Suburb": "Footscray",
            "Rooms": 3,
            ...
            "Latitude": -192,
            "Longitude": 144.9051,
        }
    ]
    "Errors": [
        {
            "item": 0,
            "error": "Illegal coordinates (-192, 144.9051)"
        }
    ]
}
```

## Notes
According to OSM, [schools should idealy tagged with a way](https://help.openstreetmap.org/questions/17168/display-of-amenity-symbol-for-buildings) (encompassing the entire school area), and not a node. However, as the database is maintained by volunteers, it is hard to enforce those standards, and schools are sometimes [nodes, ways or relations](https://taginfo.openstreetmap.org/tags/amenity=school). Also, it is common to find multiple tags of different types, on the same location, curropting the data and resulting in a higher number of elements then actually exist. 

In this implementation I have chosen to address one of those issues - where both a way and a node mark the same location. This is based on purely on the location of the node and way overlapping. We can further enchance this by examaning the various tags a location has, although this is very unconsistent and varies between countries and areas, depending on the maintainers.

## Further Improvments
In order to handle a large amount of rows, the data-set must be clustered into nearby locations, such that every group of locations is handled with a single query to the OSM service. The returned data needs to be parsed and each amenity will be checked to see if it is within the bounding box defining each data-point. We can use a coordinates search data-structure to speed up this part.

If the data is too sparse, we will have to use query-per-location, in the same manner as currently implemented. 

## Additional Data-Enrichment Sources
- [Air Quality.](https://breezometer.com/products/air-quality-api)
- [Crime Rate.](https://www.crimeometer.com/crime-data-api)
