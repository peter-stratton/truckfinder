import time
import json
import random
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
Truck = namedtuple('Truck', 'vin, features, stage, sticker_url, vehicle_url, bodycolor')
Prices = namedtuple('Prices', 'msrp, allx, az, az_applicable, dealer_price')

# While the url parameter for this is dealer_slug, in truth it's an access token and needs to regenerated every 24 hours
# by visiting http://shop.ford.com/inventory/f150/results?zipcode=19027&Radius=20&Dealer=01306&Order=Distance, opening
# the dev console, and examining the XHR requests to find a new token.
DEALER_SLUG = "nd%2FAWM1AAElHQrPMX95ycVN1SkErOOyg3%2Fwwz6OkoF7xEB04CUom2HuHtYmky2R%2B"

DEALER_SRC_URL = "http://shop.ford.com/aemservices/cache/inventory/dealer/dealers?make=Ford&market=US&inventoryType=Radius&maxDealerCount=150&model=f-150&segment=Truck&zipcode=19027"
INVENTORY_URL = "http://shop.ford.com/aemservices/cache/inventory/dealer-lot?dealerSlug={}&make=Ford&market=US&Cab=supcrew_cab&Dealer={}&Drive=4x4&Engine=v_6_ecoboost&Order=Distance&Radius=100&inventoryType=Radius&model=f-150&modeltrim=F-150_F24-XLT&segment=Truck&year=2017&zipcode=19027"
INVENTORY_DETAIL = "http://shop.ford.com/aemservices/cache/inventory/dealer-lot?dealerSlug={0}&make=Ford&market=US&Cab=supcrew_cab&Dealer={1}&Drive=4x4&Engine=v_6_ecoboost&Order=Distance&Radius=100&beginIndex={2}&endIndex={3}&inventoryType=Radius&model=f-150&modeltrim=F-150_F24-XLT&return=MoreVehicles&year=2017&zipcode=19027"
VEHICLE_DETAIL = "http://shop.ford.com/services/inventory/VehicleDetails.json?appContext=BP2&make=Ford&model=F-150&year=2017&vin={}&dealerPACode={}&planType=MSRP&postalCode=19027&staging=false&partClass=ModelGroup%3BCab%3BBox+Length%3BEngine%3BTransmissions%3BDrive&returnAttributes=BP2_ModelSlices_Definers%3BBP2_Pages_VehicleName_Summary%3BBP2_Pages_VehicleName_Disclaimer%3BBP3_Settings_ConfigText_DefinerOverride%3BBP2_Pages_Style_Definers%3BBP2_Pages_Models_TileDefiners%3BBP2_VehicleName_NamePlate%3BNGB_Nameplate_DisplayName%3BNGB_Nameplate_Definers%3BBP3CC_SPC_ModelListParam_Label%3BBP3CC_SPC_TrimName_Label%3BBP3CC_SPC_Settings_ShowTradeInLink.*%3BBP3CC_SPC_Settings_ShowCreditLink.*%3BBP3CC_SPC_Settings_TradeIn_Link.*%3BBP3CC_SPC_Settings_ShowDisclaimer%3BBP3CC_SPC_Settings_FinanceTermFilter%3BIQQV2_ModelSlices%3BIQQV2_Settings_ModelListParam_Model%3BBP3CC_SPC_BiWeeklyLeaseToggle_CA%3BST_FriendsFamily_Toggle%3B&partAttributes=BP2_PartDescriptions_.*%3B&showPaymentEstimatorV2=true&vehicleStageFilter=inproduction%3Bonlot%3Bintransit"
VEHICLE_URL = "http://shop.ford.com/inventory/f150/details/{}?zipcode=19027&year=2017&ownerPACode={}"

PACKAGE_ID = '302A'
FX4_DESIGNATOR = '.55A.'
CHUNK_SIZE = 12

USER_AGENTS_FILE = './data/user_agents.txt'


def load_user_agents(uafile=USER_AGENTS_FILE):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)
    return uas


def get_prices(truck, dealer_price):
    msrp = truck['pricing']['defaultPaymentPrices']['MSRP']['adjustedPrice']
    allx = truck['pricing']['defaultPaymentPrices']['ALLX']['adjustedPrice']
    az = truck['pricing']['defaultPaymentPrices']['AZ']['adjustedPrice']
    az_applicable = truck['pricing']['isAZPlanApplicable']
    return Prices(msrp=msrp, allx=allx, az=az, az_applicable=az_applicable, dealer_price=dealer_price)


def build_url(vin, d_code):
    return VEHICLE_URL.format(vin, d_code)


def randomize_header(agent_list):
    return {"Connection": "close", "User-Agent": random.choice(agent_list)}

def run():
    metric_dict = {'v_count': 0,
                   'e_27L_count': 0,
                   'e_35L_count': 0,
                   'sum_msrp': 0,
                   'sum_allx': 0,
                   'sum_az': 0,
                   'error_count': 0}

    user_agents = load_user_agents()

    res = requests.get(DEALER_SRC_URL, headers=randomize_header(user_agents))
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

        inv = requests.get(INVENTORY_URL.format(DEALER_SLUG, dealer.code), headers=randomize_header(user_agents))
        vcount = json.loads(inv.content)['data']['filterResults']['ExactMatch']['totalCount']
        dealership = get_or_create_dealership(dealer)

        chunk_ends = list(range(0, vcount, CHUNK_SIZE))
        chunk_ends.append(vcount)
        for end in enumerate(chunk_ends):
            try:
                trucks = requests.get(INVENTORY_DETAIL.format(DEALER_SLUG, dealership.code, chunk_ends[end[0]], chunk_ends[end[0] + 1]), headers=randomize_header(user_agents))
                for vehicle in json.loads(trucks.content)['data']['filterResults']['ExactMatch']['vehicles']:
                    # if vehicle['rawPackageGroupId'] == PACKAGE_ID and vehicle['imageToken'].find(FX4_DESIGNATOR) > 0:
                    if vehicle['imageToken'].find(FX4_DESIGNATOR) > 0:
                        print("Processing Vehicle: {}".format(vehicle['vin']))
                        try:
                            d_price = float(json.loads(requests.get(VEHICLE_DETAIL.format(vehicle['vin'], dealership.code),
                                                              headers=randomize_header(user_agents)).content)['Response']['InventoryVehicle']['Pricing']['DealerPrice'])
                        except KeyError as e:  # DealerPrice not in the result, likely because STOCKINPLANT
                            d_price = None
                        time.sleep(random.randint(1, 3))  # best not let them know we're automating this

                        metric_dict['v_count'] += 1
                        prices = get_prices(vehicle, d_price)
                        truck = get_or_create_vehicle(Truck(vin=vehicle['vin'],
                                                            features=vehicle['keyDisplayFeatures'],
                                                            stage=vehicle['vehicleStage'],
                                                            sticker_url=vehicle['windowStickerURL'],
                                                            vehicle_url=build_url(vehicle['vin'], dealership.code),
                                                            bodycolor=vehicle['vehicleFeatures']['ExteriorColor']['displayName']),
                                                      dealership)
                        price = create_price_for_vehicle(prices, truck)
                        metric_dict['sum_msrp'] += price.msrp_adjusted
                        metric_dict['sum_allx'] += price.allx_adjusted
                        metric_dict['sum_az'] += price.az_adjusted
                        if truck.f_engine.find('2.7L') >= 0:
                            metric_dict['e_27L_count'] += 1
                        else:
                            metric_dict['e_35L_count'] += 1
            except IndexError:  # if we fall off the end we're done with that dealership
                pass
            except Exception as e:
                metric_dict['error_count'] += 1
                print("TODO: Use Sentry Here In Prod!!!!")
                print("= = = = = = = = = = = = = = = = =")
                print(e)
    create_daily_metrics(metric_dict)

if __name__ == "__main__":
    run()
