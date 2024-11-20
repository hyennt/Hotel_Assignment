from dataclasses import dataclass, asdict
import json
import argparse
from dataclasses import dataclass
from typing import List, Dict
import requests
from abc import ABC, abstractmethod


import requests
@dataclass
class Location:
    latitude: float
    longitude: float
    address: str
    country: str

@dataclass
class Amenities:
    general: List
    room: List

@dataclass
class Images:
    rooms: List[str]
    amenities: List[str]

@dataclass
class Hotel:
    id: str
    destination_id: str
    name: str
    description: str
    location: Location
    amenities: Amenities
    images: Images
    booking_conditions: List[str]
    
LIST_AMENITIES = {
    "general": ["outdoor pool", "indoor pool", "business center", "childcare", "wifi", "dry cleaning", "breakfast"],
    "room": ["aircon", "tv", "coffee machine", "kettle", "hair dryer", "iron", "bathtub"]
    
} 
RAW_DATA_LIST_AMENITIES = {
    "general": [each_gen.replace(" ","") for each_gen in LIST_AMENITIES["general"]] ,
    "room" : [each_room.replace(" ","")  for each_room in LIST_AMENITIES["room"]]
}

MAPPING_RAW_DATA_AMENITIES = {}


for category in LIST_AMENITIES:
    for raw, original in zip(RAW_DATA_LIST_AMENITIES[category], LIST_AMENITIES[category]):
        MAPPING_RAW_DATA_AMENITIES[raw] = original

class BaseSupplier:
    def endpoint():
        """URL to fetch supplier data"""
        pass

    def parse(obj: dict) -> Hotel:
        """Parse supplier-provided data into Hotel object"""
        pass
    def fetch(self):
        url = self.endpoint()
        resp = requests.get(url)
        return [self.parse(dto) for dto in resp.json()]

class Acme(BaseSupplier):
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/acme'

    @staticmethod
    def parse(dto: dict) -> Hotel:
        amenities = [facility.strip().replace(" ","").lower() for facility in dto.get('Facilities') or []]
        
        filtered_general = [MAPPING_RAW_DATA_AMENITIES[val_gen] for val_gen in amenities if val_gen in RAW_DATA_LIST_AMENITIES["general"]]
        filtered_room = [MAPPING_RAW_DATA_AMENITIES[val_room] for val_room in amenities if val_room in RAW_DATA_LIST_AMENITIES["room"]]

        return Hotel(
            id=dto['Id'],
            destination_id=dto['DestinationId'],
            name=dto['Name'],
            location=Location(
                latitude=dto.get('Latitude'),
                longitude=dto.get('Longitude'),
                address=dto.get('Address'),
                country=dto.get('Country')
            ),
            amenities = Amenities(
                general=filtered_general,
                room=filtered_room
            ),
            description= dto.get("description"),
            images= dto.get("images"),
            booking_conditions=dto.get("booking_conditions")
        )
    

class Paperflies(BaseSupplier):
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/paperflies'

    @staticmethod
    def parse(dto: dict) -> Hotel:
        return Hotel(
            id=dto['hotel_id'],
            destination_id=dto['destination_id'],
            name=dto['hotel_name'],
            location=Location(
                latitude= dto["location"].get("latitude"),
                longitude=dto["location"].get("Longitude"),
                address=dto["location"]["address"],
                country=dto["location"]["country"]
            ) if dto.get("location") else None,
            amenities = Amenities(
               general=dto.get("amenities").get("general"),
               room=dto.get("amenities").get("room"),
            ) if dto.get("amenities") else None,
            description= dto.get("details"),
            images= dto.get("images"),
            booking_conditions=dto.get("booking_conditions")
            
        )
        
class Patagonia(BaseSupplier):
    
    @staticmethod
    def endpoint():
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/patagonia'

    @staticmethod
    def parse(dto: dict) -> Hotel:
        
        amenities = [facility.strip().replace(" ","").lower() for facility in dto.get('amenities')or []]
        
        filtered_general = [MAPPING_RAW_DATA_AMENITIES[val_gen] for val_gen in amenities if val_gen in RAW_DATA_LIST_AMENITIES["general"]]
        filtered_room = [MAPPING_RAW_DATA_AMENITIES[val_room] for val_room in amenities if val_room in RAW_DATA_LIST_AMENITIES["room"]]

        return Hotel(
            id=dto['id'],
            destination_id=dto['destination'],
            name=dto['destination'],
            location=Location(
                latitude= dto.get("lat"),
                longitude=dto.get("lng"),
                address=dto.get("address"),
                country=dto.get("country"),
            ),
            amenities = Amenities(
                general=filtered_general,
                room=filtered_room
            ),
            description= dto.get("details"),
            images= dto.get("images"),
            booking_conditions=dto.get("booking_conditions")    
        )
        
class HotelsService:
    
    def parsed_hotel_data(self, merged_name, current_name) -> str:
        if type(merged_name) == str and type(current_name) == str:
            merged_name = merged_name.strip()
            current_name = current_name.strip()
            if merged_name == current_name:
                pass
            elif merged_name == None or merged_name == "" or len(merged_name) < len(current_name):
                merged_name = current_name
        return merged_name
    
    def merge_hotels_same_id(self, hotels: List[Hotel]) -> Hotel:
        print()
        merged_hotel = hotels[0]
        for each_hotel in hotels[1:]:
            merged_hotel.name = self.parsed_hotel_data(merged_hotel.name, each_hotel.name)
            merged_hotel.location.address =  self.parsed_hotel_data(merged_hotel.location.address, each_hotel.location.address)
            merged_hotel.location.country =  self.parsed_hotel_data(merged_hotel.location.country, each_hotel.location.country)
            merged_hotel.location.latitude =  self.parsed_hotel_data(merged_hotel.location.latitude, each_hotel.location.latitude)
            # merged_hotel.location.city =  self.parsed_hotel_data(merged_hotel.location.city, each_hotel.location.city)
            merged_hotel.description =  self.parsed_hotel_data(merged_hotel.description, each_hotel.description)
            merged_hotel.amenities =  self.parsed_hotel_data(merged_hotel.amenities, each_hotel.amenities)
            merged_hotel.images =  self.parsed_hotel_data(merged_hotel.images, each_hotel.images)
            merged_hotel.booking_conditions =  self.parsed_hotel_data(merged_hotel.booking_conditions, each_hotel.booking_conditions)

        return merged_hotel
    
    
   
    def merge_and_save(self, all_supplier_data: List[Hotel]):
        hotel_supplier = {}
        for each_supp in all_supplier_data:
            hotel_id = each_supp.id
            if hotel_id in hotel_supplier:
                hotel_supplier[hotel_id].append(each_supp)
            else:
                hotel_supplier[hotel_id] = [each_supp]
        merged_hotels = []
        for hotel_id, hotel_values in hotel_supplier.items():
            merged_hotel = self.merge_hotels_same_id(hotel_values)
            merged_hotels.append(asdict(merged_hotel))
        return merged_hotels

def to_dict(hotels: List[Hotel]) -> dict:
    hotels_dict = []
    for hotel in hotels:
        hotels_dict.append(asdict(hotel))
        
    return hotels_dict

def fetch_hotels(hotel_ids, destination_ids):
    # Write your code here

    suppliers = [
        Acme(),
        Paperflies(),
        Patagonia(),
    ]
    # print(suppliers[1].fetch())

    # # Fetch data from all suppliers
    all_supplier_data = []
    for supp in suppliers:
        all_supplier_data.extend(supp.fetch())
    # print("Fetching supplier",all_supplier_data)

    # Merge all the data and save it in-memory somewhere
    svc = HotelsService()
    final_list = svc.merge_and_save(all_supplier_data)
    print('Final:', final_list)
    

    # # Fetch filtered data
    # filtered = svc.find(hotel_ids, destination_ids)

    # # Return as json
    with open('./output.json', 'w') as output:
        json.dump(final_list, output)
    
def main():
    # parser = argparse.ArgumentParser()
    
    # parser.add_argument("hotel_ids", type=str, help="Hotel IDs")
    # parser.add_argument("destination_ids", type=str, help="Destination IDs")
    
    # # Parse the arguments
    # args = parser.parse_args()
    
    # hotel_ids = args.hotel_ids
    # destination_ids = args.destination_ids
    
    # result = fetch_hotels(hotel_ids, destination_ids)
    result = fetch_hotels(None, None)
    print(result)

if __name__ == "__main__":
    main()