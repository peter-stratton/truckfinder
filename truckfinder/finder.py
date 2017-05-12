import time
import json
from collections import namedtuple

import requests
from tqdm import tqdm

from truckfinder.models.dealership import get_or_create_dealership
from truckfinder.models.vehicle import get_or_create_vehicle
from truckfinder.models.price import create_price_for_vehicle
from truckfinder.models.metric import create_daily_metrics
from truckfinder.app import create_app
create_app().app_context().push()

Dealer = namedtuple('Dealer', 'name, code, distance, phone, street, city, state, zip')
Truck = namedtuple('Truck', 'vin, features, stage, sticker_url, vehicle_url')
Prices = namedtuple('Prices', 'msrp, allx, az, az_applicable')

# While the url parameter for this is dealer_slug, in truth it's an access token and needs to regenerated every 24 hours
# by visiting http://shop.ford.com/inventory/f150/results?zipcode=19027&Radius=20&Dealer=01306&Order=Distance, opening
# the dev console, and examining the XHR requests to find a new token.
DEALER_SLUG = "9pTZ5jO83NqLHxrtXPJnZ9d7P61O4Y3LyYzMtdhjqMKEpFRPcSsQ0VSTRpAXkjLL"

DEALER_SRC_URL = "http://shop.ford.com/aemservices/cache/inventory/dealer/dealers?make=Ford&market=US&inventoryType=Radius&maxDealerCount=150&model=f-150&segment=Truck&zipcode=19027"
INVENTORY_URL = "http://shop.ford.com/aemservices/cache/inventory/dealer-lot?dealerSlug={}&make=Ford&market=US&Cab=supcrew_cab&Dealer={}&Drive=4x4&Engine=v_6_ecoboost&Order=Distance&Radius=100&inventoryType=Radius&model=f-150&modeltrim=F-150_F24-XLT&segment=Truck&year=2017&zipcode=19027"
VEHICLE_DETAIL = "http://shop.ford.com/aemservices/cache/inventory/dealer-lot?dealerSlug={0}&make=Ford&market=US&Cab=supcrew_cab&Dealer={1}&Drive=4x4&Engine=v_6_ecoboost&Order=Distance&Radius=100&beginIndex={2}&endIndex={3}&inventoryType=Radius&model=f-150&modeltrim=F-150_F24-XLT&return=MoreVehicles&year=2017&zipcode=19027"
VEHICLE_URL = "http://shop.ford.com/inventory/f150/details/{}?zipcode=19027&year=2017&ownerPACode={}"

PACKAGE_ID = '302A'
FX4_DESIGNATOR = '.55A.'
CHUNK_SIZE = 12


def get_prices(truck):
    msrp = truck['pricing']['defaultPaymentPrices']['MSRP']['adjustedPrice']
    allx = truck['pricing']['defaultPaymentPrices']['ALLX']['adjustedPrice']
    az = truck['pricing']['defaultPaymentPrices']['AZ']['adjustedPrice']
    az_applicable = truck['pricing']['isAZPlanApplicable']
    return Prices(msrp=msrp, allx=allx, az=az, az_applicable=az_applicable)


def build_url(vin, d_code):
    return VEHICLE_URL.format(vin, d_code)


def run():
    metric_dict = {'v_count': 0,
                   'e_27L_count': 0,
                   'e_35L_count': 0,
                   'sum_msrp': 0,
                   'sum_allx': 0,
                   'sum_az': 0,
                   'error_count': 0}

    res = requests.get(DEALER_SRC_URL)
    dealers_raw = json.loads(res.content)['data']['Response']
    dealers_list = [Dealer._make([x['Dealer']['dealerName'],
                                  x['Dealer']['dealerpaCode'],
                                  x['Dealer']['Distance'],
                                  x['Dealer']['dealerPhone'],
                                  x['Dealer']['Address']['Street1'],
                                  x['Dealer']['Address']['City'],
                                  x['Dealer']['Address']['State'],
                                  x['Dealer']['Address']['Postalcode'],
                                  ]) for x in dealers_raw]

    for dealer in tqdm(dealers_list):
        inv = requests.get(INVENTORY_URL.format(DEALER_SLUG, dealer.code))
        vcount = json.loads(inv.content)['data']['filterResults']['ExactMatch']['totalCount']
        dealership = get_or_create_dealership(dealer)

        chunk_ends = list(range(0, vcount, CHUNK_SIZE))
        chunk_ends.append(vcount)
        for end in enumerate(chunk_ends):
            try:
                trucks = requests.get(VEHICLE_DETAIL.format(DEALER_SLUG, dealership.code, chunk_ends[end[0]], chunk_ends[end[0] + 1]))
                for vehicle in json.loads(trucks.content)['data']['filterResults']['ExactMatch']['vehicles']:
                    if vehicle['rawPackageGroupId'] == PACKAGE_ID and vehicle['imageToken'].find(FX4_DESIGNATOR) > 0:
                        metric_dict['v_count'] += 1
                        prices = get_prices(vehicle)
                        truck = get_or_create_vehicle(Truck(vin=vehicle['vin'],
                                                            features=vehicle['keyDisplayFeatures'],
                                                            stage=vehicle['vehicleStage'],
                                                            sticker_url=vehicle['windowStickerURL'],
                                                            vehicle_url=build_url(vehicle['vin'], dealership.code)),
                                                      dealership)
                        price = create_price_for_vehicle(prices, truck)
                        metric_dict['sum_msrp'] += price.msrp_adjusted
                        metric_dict['sum_allx'] += price.allx_adjusted
                        metric_dict['sum_az'] += price.az_adjusted
                        if truck.f_engine.find('2.7L') >= 0:
                            metric_dict['e_27L_count'] += 1
                        else:
                            metric_dict['e_35L_count'] += 1
                time.sleep(1)
            except IndexError:  # if we fall off the end we're done with that dealership
                pass
            except Exception as e:
                metric_dict['error_count'] += 1
                print("TODO: Use Sentry Here In Prod!!!!")
                print("= = = = = = = = = = = = = = = = =")
                print(e)
        time.sleep(1)
    create_daily_metrics(metric_dict)

if __name__ == "__main__":
    run()
