import requests
import json
import csv

# GLOBAL VARIABLES:
# Name of file information is saved to
OUT_FILENAME = "recently_sold_redfin.csv"

# Max number of days in the past
TIME_RANGE = 90;


# CLASSES:
class Counter(object):
    """
    A class for generating incrementing numbers.

    Attributes:
        x (int): number of times the next function has been called
    """

    x = 0

    def next(self):
        """
        Increments and returns current count.

        Returns:
            int: number of times next has been called
        """

        self.x += 1
        return self.x


# FUNCTIONS:
def create_sold_property_csv(filename):
    """
    Opens a templated csv file for storing sold property data.

    Includes fields property_id, date_sold, price, square_footage, lot_size,\
    number_bedrooms, number_bathrooms, year_built, latitude, longitude,\
    property_type, street_number, street_name, neighborhood, city, state,\
    zip_code and time_until_sold.

    Parameters:
        filename (string): name of output file

    Returns:
        (file, csv.DictWriter): file object and writer for newly created csv file
    """

    csvFile = open(filename, "w", newline="")
    fields = ["property_id", "date_sold", "price", "square_footage", "lot_size",\
        "number_bedrooms", "number_bathrooms", "year_built", "latitude",\
        "longitude", "property_type", "street_number", "street_name",\
        "neighborhood", "city", "state", "zip_code", "time_until_sold"]
    csvWriter = csv.DictWriter(csvFile, fieldnames=fields, restval="")
    csvWriter.writeheader()
    return (csvFile, csvWriter)

def get_sold_property_json(id, days):
    """
    Makes an HTTP request to redfin.com for a JSON containing data of properties
    withing input region id that were sold in the past input number of days.

    Searching by region id is the broadest search I'm aware of on refin.com that
    also won't contain repeated properties in multiple searches.

    Parameters:
        id (int): redfin region id to query for properties in
        days (int): number of days into the past the data will go

    Returns:
        dict: the content of the JSON file returned by redfin.com
    """

    # This url is approved for bots in redfin.com/txt, so its unnecessary to
    # include sleep logic as they won't block your IP
    url = "https://www.redfin.com/stingray/do/gis-search?al=1&num_homes=10000&region_id="+str(id)+"&region_type=6&sold_within_days="+str(days)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers)
        jsonData = json.loads(r.content[4:])
    except (requests.ConnectionError, json.decoder.JSONDecodeError):
        # Failed to connect or read JSON properly. Skip this one.
        return
    return jsonData

def parse_sold_property_json(csvWriter, jsonData, cnt):
    """
    Parses JSON redfin.com sold property data and appends it to CSV file.

    Parameters:
        csvWriter (csv.DictWriter): writer to desired csv file
        jsonData (dict): data from redfin.com sold property JSON
        cnt (Counter): generates auto incrementing keys
    """

    # Return if JSON is empty or an error occured while being retreived
    if jsonData == None:
        return
    if jsonData["errorMessage"] != "Success":
        return

    # Construct and write new row for every property listed in the JSON
    for property in jsonData["payload"]["search_result"]:
        row = {"property_id" : cnt.next()}

        # For every field, check if it exists before adding it to prevent an exception
        if "date" in property:
            row.update(date_sold = property["date"])
            if "listing_added" in property:
                row.update(time_until_sold = int(property["date"])\
                    - int(property["listing_added"]))
        if "price" in property:
            row.update(price = property["price"])
        if "sqft" in property:
            row.update(square_footage = property["sqft"])
        if "lotsize" in property:
            row.update(lot_size = property["lotsize"])
        if "beds" in property:
            row.update(number_bedrooms = property["beds"])
        if "baths" in property:
            row.update(number_bathrooms = property["baths"])
        if "year_built" in property:
            row.update(year_built = property["year_built"])
        if "type" in property:
            row.update(property_type = property["type"])
        if "neighborhood" in property:
            row.update(neighborhood = property["neighborhood"])
        if "parcel" in property:
            if "latitude" in property["parcel"]:
                row.update(latitude = property["parcel"]["latitude"])
            if "longitude" in property["parcel"]:
                row.update(longitude = property["parcel"]["longitude"])
        if "address_data" in property:
            address = property["address_data"]
            if "number" in address:
                row.update(street_number = address["number"])
            if "street" in address and "type" in address:
                row.update(street_name = address["street"] + " "\
                    + address["type"])
            if "city" in address:
                row.update(city = address["city"])
            if "state" in address:
                row.update(state = address["state"])
            if "zip" in address:
                row.update(zip_code = address["zip"])

            # Write the row to the CSV file
            csvWriter.writerow(row)


# MAIN CODE:
if __name__ == "__main__":
    # Create CSV file
    (csvFile, csvWriter) = create_sold_property_csv(OUT_FILENAME)

    # Although unclear what the region ids on redfin.com represent, they all
    # fall within the range [243, 35952]
    (minId, maxId) = (243, 35952)

    # Instantiate Counter to make auto incrementing unique ids for properties in the CSV
    propertyIdCnt = Counter()

    # Loop through all property ids and write all properties sold within them to CSV
    for id in range(minId, maxId+1):
        # Request properties sold within the last 90 days with this region id
        jsonData = get_sold_property_json(id, TIME_RANGE)

        # Append data from JSON to the CSV file
        parse_sold_property_json(csvWriter, jsonData, propertyIdCnt)
        csvFile.flush()

        # Print progress
        print("Processed "+str(1+id-minId)+" out of "+str(maxId-minId)+".", end="\r")

    print("\nCompleted!")

    csvFile.close();
