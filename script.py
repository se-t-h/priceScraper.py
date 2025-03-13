#'424310W030'
#'PZ36400W01'
#'PTR0353085'
#'04152YZZA5'
# '9043012031' # oil washer
# '3517830010' # atf pan washer
# '3533050030' # atf pan filter
# '3516850010' # atf pan gasket
# 'PT39853141' # remote start

import argparse
import concurrent.futures
import json
import re
import requests
import sys
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
DEFAULT_THREADS = 20
DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3
ZIP_CODES = ['92882', '04401', '10001', '20103', '32244', '48228', '57106', '60007', '75001', '80904', '98550']

LEXUS_DEALERS = ['parkerlexus.com', 'iralexus.com', 'lexusofsantabarbara.com', 'lindsaylexusofalexandria.com', 'desertlexus.com', 'lexusoflakeway.com', 'lexusofmobile.com', 'stevinsonlexusoffrederick.com', 'arrowheadlexus.com', 'lexusneworleans.com', 'lexusofsouthfield.com', 'hoffmanlexus.com', 'lexusofsacramento.com', 'woodfieldlexus.com', 'lexusofwoodlandhills.com', 'kunilexusofportland.com', 'priceleblanclexus.com', 'chathamparkwaylexus.com', 'treasurecoastlexus.com', 'lexusofchandler.com', 'eskridgelexus.com', 'lexusofroute10.com', 'lexusofwesleychapel.com', 'lexusofnaperville.com', 'lexusofriverside.com', 'rallyelexus.com', 'serralexuslansing.com', 'nalleylexussmyrna.com', 'metrolexus.com', 'lexusofthousandoaks.com', 'hendricklexuscharlotte.com', 'germainlexusdublin.com', 'belllexusnorthscottsdale.com', 'lexusofroseville.com', 'lexusoftulsa.com', 'crownlexus.com', 'sterlingmccalllexusclearlake.com', 'lexusofpleasanton.com', 'lexusofbrooklyn.com', 'thompsonlexusdoylestown.com', 'lexusofoxnard.com', 'prioritylexusnewportnews.com', 'mungenastlexusofstlouis.com', 'baliselexus.com', 'willislexus.com', 'lexussandiego.com', 'fieldslexusglenview.com', 'lexusofmaplewood.com', 'cavenderlexusoflubbock.com', 'hendricklexusnorthlake.com', 'augustalexus.com', 'lexusofmerrillville.com', 'keyeslexus.com', 'lexusofwatertown.com', 'bergstromlexus.com', 'lexusofbrookfield.com', 'lexusofeaston.com', 'lexusoflakeside.com', 'lexusofmanhattan.com', 'tomwoodlexus.com', 'lexusofmemphis.com', 'prioritylexusvirginiabeach.com', 'lexusoforland.com', 'lexusofnorthborough.com', 'ourismanlexusofrockville.com', 'lexusofqueens.com', 'parkplacelexusplano.com', 'parkplacelexusgrapevine.com', 'fresnolexus.com', 'lexusorangecounty.com', 'lexuselcajon.com', 'haldemanlexusofprinceton.com', 'lexusofwarwick.com', 'lexusofwichita.com', 'hudsonlexus.com', 'lexuswestminster.com', 'lexusofarlington.com', 'lexusofrichmond.com', 'southbaylexus.com', 'rohrichlexus.com', 'lexusofconcord.com', 'stevinsonlexusoflakewood.com', 'earnhardtlexus.com', 'westsidelexus.com', 'freemanlexus.com', 'lexusofnaples.com', 'lexusofenglewood.com', 'lexusoflincoln.com', 'thompsonlexuswillowgrove.com', 'nalleylexusroswell.com', 'hiltonheadlexus.com', 'lexusoffortmyers.com', 'lexusoflexington.com', 'prestigelexus.com', 'lexusofsilverspring.com', 'tvlexus.com', 'lexusfremont.com', 'mcgrathlex.com', 'sheehylexusofannapolis.com', 'larryhmillerlexuslindon.com']

SUBARU_DEALERS = ['stevenscreeksubaru.com', 'mcgovernsubaruofacton.com', 'williamssubaru.com', 'cascadesubaru.net', 'hicksfamilysubaru.com', 'jenkinssubaruwv.com', 'northcoastsubaru.com', 'capitalofgreenville.com', 'hellosubarutemecula.com', 'sangerasubaru.com', 'mullersubaru.com', 'landersmclartysubaru.net', 'northreadingsubaru.com', 'subaruwesleychapel.com', 'westpalmsubaru.com', 'dreyerreinboldsubaru.com', 'delawaresubaru.com', 'subaruofwinchester.com', 'subaruofenglewood.com', 'royaleastsubaru.com', 'cascadesubaru.com', 'subaruofdaytona.com', 'victorysubaru.com', 'alexandersubaruinc.com', 'peninsulasubaru.com', 'colonialsubaruct.com', 'valleysubaru.com', 'reynoldssubaruoforange.com', 'dchsubaruthousandoaks.com', 'bobwadesubaru.com', 'subaruofpuyallup.com', 'evergreensubaru.com', 'tvsubaru.com', 'boardmansubaru.com', 'subaruoflasvegas.com', 'hodgessubaru.com', 'subaruofwichita.com', 'shinglespringssubaru.com', 'beardmoresubaru.com', 'fergusonsubaru.com', 'tacomasubaru.com', 'geraldsubarunaperville.com', 'charlestonsubaru.com', 'firstteamsubarunorfolk.com', 'royalmooresubaru.net', 'walser-subaru.com', 'prestigesubaru.com', 'mclaughlinsubaru.com', 'patrickssubaru.com', 'greshamsubaru.com', 'millersubaru.com', 'faulknersubaruharrisburg.com', 'camelbacksubaru.com', 'wagnersubaru.com', 'johnkennedysubaru.com', 'crosscreeksubaru.com', 'subaruspokane.com', 'subarumemphishackscross.com', 'parkersubaru.com', 'zeiglersubarumerrillville.com', 'subarubloomingtonnormal.com', 'qualitysubaru.com', 'brattleborosubaru.com', 'bedfordsubaru.com', 'annapolissubaru.com', 'armstrongsubaru.com', 'natewade.com', 'westhoustonsubaru.com', 'terrysubaru.com', 'cpsubaru.com', 'briggssubarutopeka.com', 'muscatellsubaru.com', 'ramseysubaru.com', 'carlsensubaru.com', 'devoesubaruofnaples.com', 'sheehysubarufredericksburg.com', 'gustmansubaru.com', 'libertysubaru.com', 'darrellwaltripsubaru.com', 'johnsonsubaruofcary.com', 'irvinesubaru.com', 'spanglersubaru.com', 'subaruofsantafe.com', 'donmillersubaruwest.com', 'greeleysubaru.com', 'sportsubaru.com', 'davewrightsubaru.com', 'adventuresubaru.com', 'foxsubarumacomb.com', 'currysubaru.com', 'stamfordsubaru.com', 'fairfieldsubaru.com', 'subaruofolathe.com', 'metrowestsubaru.com', 'raffertysubaru.com', 'columbussubaru.com', 'louisthomassubaru.com', 'walsersubarustpaul.com', 'grandsubaru.com', 'vanbortelsubaru.net', 'evanstonsubaru.com', 'elkgrovesubaru.com', 'dahlsubaru.com', 'subarugrapevine.net', 'ewingsubaruofplano.com', 'capcitysubaru.com', 'subarushermanoaks.com', 'goldrushsubaru.com', 'subaruofkennesaw.com', 'schallersubaru.com', 'secorsubaru.com', 'carrsubaru.com', 'subarusouthhills.com', 'subaruofnorthmiami.com', 'kirbysubaruofventura.com', 'subaruofcorvallis.com', 'newmotorssubaru.com', 'bkcars.com', 'subaruofsterling.com', 'busamsubaru.com', 'subaruofwakefield.com', 'npsubarudominion.com', 'subarufuccillo.com', 'stockersubaru.com', 'subaruoflittlerock.com', 'maitasubaru.com', 'autonationsubaruhiltonhead.com', 'chicosubaru.com', 'subaruofcherryhill.com', 'hughessubaru.com', 'gillmansubaru.com', 'gillmansubarusanantonio.com', 'huntersubaru.com', 'subarupacific.com', 'schompsubaru.com', 'belairsubaru.com', 'hileysubaru.com', 'bestbuysubaru.com', 'findlaysubaru.com', 'fuszsubaru.com', 'myvalleysubaru.com', 'openroadsubaru.com', 'bermansubaru.com', 'subarumorgantown.com', 'cavendersubaruofnorman.com', 'northendsubaru.com', 'autonationsubaruhuntvalley.com', 'fairwaysubarusc.com', 'michaelhohlsubaru.com', 'dougsmithsubaru.com', 'subarusuperstorewest.com', 'subaruorangecoast.com', 'wyattjohnsonsubaru.com', 'mcgovernsubaru.com', 'subarumelbourne.com', 'hanleessubaru.com', 'atsubaru.net', 'farrishsubaru.com', 'subaruofrochestermn.com', 'thomascumberlandsubaru.com', 'troncallisubaru.com', 'subaruofdayton.com', 'manassassubaru.com', 'stohlmansubaru.com', 'rksubaru.com', 'saintjsubaru.com', 'cypresscoastsubaru.com', 'wildesubaru.com', 'subarusouthcharlotte.com', 'libertyautocitysubaru.com', 'bertsmithsubaru.com', 'subaruofbend.com', 'kearnymesasubaru.com', 'subaruconcord.com', 'stuckeysubaru.com', 'bowsersubaru.com', 'northtownsubaru.com', 'lithiasubarureno.com', 'autonationsubarucarlsbad.com', 'byerssubarudublin.com', 'donmillersubarueast.com', 'autonationsubaruarapahoe.com', 'youngsubaru.com', 'sterlingsubaru.com', 'subarusouthpoint.com', 'waynesubaru.com', 'rentonsubaru.com', 'hymanbrossubaru.com', 'subaruofrichmond.com', 'rimrocksubaru.com', 'serramontesubaru.com', 'bryansubaru.com', 'baxtersubarulavista.com', 'mckennasubaru.com', 'timmonssubaru.com', 'sommerssubaru.com', 'baxtersubaru.com', 'subaruofgwinnett.com', 'downtownsubarunashville.com', 'subaruofspringfield.com', 'suburbansubaru.com', 'normreevessubarurockwall.com', 'autonationsubaruroseville.com', 'shopempiresubaru.com', 'buchanansubaru.com', 'ourismansubaruwaldorf.com', 'germainsubaruofcolumbus.com', 'austinsubaru.com', 'drivewaysubarumoon.com', 'rugessubaru.com', 'subaruofglendale.net', 'easthillssubaru.com', 'faulknersubarumechanicsburg.com', 'subaruofgallatin.com', 'delaneysubaru.com', 'dullessubaru.com', 'marinsubaru.net', 'mycolonialsubaru.com', 'hendricksubaruhoover.com', 'randymarionsubaru.com', 'santacruzsubaru.com', 'autonationsubaruwest.com', 'mikeshawsubaru.com', 'tomwoodsubaru.com', 'cioccasubaru.com', 'bergstromsubarugreenbay.com', 'augustasubarudealer.com', 'mcdanielssubaru.com', 'northparksubaru.net', 'subaruofoakland.com', 'capitolsubaru.com', 'subaruofpueblo.com', 'peltiersubaru.com', 'oregoncitysubaru.com', 'gregorissubaru.com', 'whitebearsubaru.com', 'winnersubaru.com', 'sierrasubaru.com', 'peoriasubaru.com', 'boisesubaru.com', 'citysidesubaru.com', 'flowsubarucharlottesville.com', 'granitesubaru.com', 'beyersubaru.com', 'schumachersubaruofdelray.com', 'subaru.fusz.com', 'theautobarnsubaru.com', 'tucsonsubaru.com', 'subaruofmorristown.com', 'subaruofsonora.com']

class Result:
    def __init__(self, dealer: str, price: Optional[float] = None, address: Optional[str] = None, 
                 status: str = "unknown", error: Optional[str] = None):
        self.dealer = dealer
        self.price = price
        self.address = address
        self.status = status
        self.error = error
        self.url = f"https://parts.{dealer}/productSearch.aspx?searchTerm="

    def __str__(self) -> str:
        if self.status == "success":
            addr_str = f" - {self.address}" if self.address else ""
            return f"{self.dealer}{addr_str} [${self.price}] [✓]"
        elif self.status == "out_of_stock":
            return f"{self.dealer} [!] out of stock"
        elif self.status == "blocked":
            return f"{self.dealer} [!] script blocked"
        else:
            return f"{self.dealer} [!] error: {self.error}"

def setup_argparse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto Parts Price Scraper")
    parser.add_argument("part_number", help="Part number to search for")
    parser.add_argument("-t", "--threads", type=int, default=DEFAULT_THREADS, 
                        help=f"Number of concurrent threads (default: {DEFAULT_THREADS})")
    parser.add_argument("-r", "--retries", type=int, default=DEFAULT_RETRIES, 
                        help=f"Maximum retries per dealer (default: {DEFAULT_RETRIES})")
    parser.add_argument("-p", "--proxy", required=True, help="SOCKS5 proxy in format user:pass@host:port")
    parser.add_argument("-b", "--brand", choices=["lexus", "subaru"], default="lexus",
                        help="Brand to search (lexus or subaru)")
    
    return parser.parse_args()

def get_proxies(proxy_string: str) -> Dict[str, str]:
    proxy_url = f"socks5://{proxy_string}"
    return {
        "http": proxy_url,
        "https": proxy_url
    }

def get_part_price(dealer: str, part_number: str, args: argparse.Namespace, max_retries: int = DEFAULT_RETRIES) -> Result:
    result = Result(dealer)
    retries = 0
    proxies = get_proxies(args.proxy)
    
    while retries <= max_retries:
        try:
            url = f"https://parts.{dealer}/productSearch.aspx?searchTerm={quote(part_number)}"
            response = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                proxies=proxies,
                timeout=DEFAULT_TIMEOUT
            )
            
            content = response.text.replace('\n', '')
            
            if response.status_code != 200:
                result.status = "error"
                result.error = f"HTTP {response.status_code}"
                return result
                
            if 'priceToDisplay' in content:
                price_str = None
                
                # Try Lexus format first: ,"price":33.71,"priceToDisplay"
                lex_match = re.search(',"price":(.*),"priceToDisplay"', content)
                if lex_match:
                    price_str = lex_match.group(1).split(',')[0].strip()
                
                # Try Subaru format: "priceToDisplay":"$ 232.28"
                if not price_str:
                    sub_match = re.search('"priceToDisplay":"([^"]*)"', content)
                    if sub_match:
                        price_str = sub_match.group(1)
                
                # If we found a price in either format
                if price_str:
                    # Clean up the price string and convert to float
                    clean_price = price_str.replace('"', '').replace('$', '').strip()
                    try:
                        result.price = float(clean_price)
                        result.status = "success"
                        
                        # Try to extract dealer address/zip
                        try:
                            address_match = re.search('<li class="dealerInfoAddress" role="listitem">(.*?)<li', content)
                            if address_match:
                                zip_match = re.search('(\d{5})', address_match.group(1))
                                if zip_match:
                                    result.address = zip_match.group(1)
                        except Exception:
                            pass
                            
                        return result
                    except ValueError:
                        result.status = "error"
                        result.error = f"Invalid price format: {price_str}"
                        return result
                else:
                    result.status = "error"
                    result.error = "Could not find price"
                    return result
                    
            elif 'Lexus Parts like' in content or 'Subaru Parts like' in content:
                result.status = "out_of_stock"
                return result
                
            elif 'verifyHuman' in content:
                result.status = "blocked"
                retries += 1
                if retries <= max_retries:
                    time.sleep(3)
                    continue
                return result
                
            else:
                result.status = "error"
                result.error = "Unknown response format"
                return result
                
        except requests.exceptions.Timeout:
            retries += 1
            result.status = "error"
            result.error = "Timeout"
            if retries <= max_retries:
                continue
                
        except Exception as e:
            retries += 1
            result.status = "error"
            result.error = str(e)
            if retries <= max_retries:
                continue
                
    return result

def process_dealer(dealer: str, part_number: str, args: argparse.Namespace) -> Tuple[str, Optional[float]]:
    result = get_part_price(dealer, part_number, args, args.retries)
    print(result)
    
    if result.status == "success":
        dealer_url = f"parts.{dealer}/productSearch.aspx?searchTerm={part_number}"
        if result.address:
            dealer_url += f" ... {result.address}"
        return (dealer_url, result.price)
    return (None, None)

def main():
    args = setup_argparse()
    part_number = args.part_number
    
    brand_name = args.brand.upper()
    
    if args.brand.lower() == "lexus":
        dealers = LEXUS_DEALERS
    elif args.brand.lower() == "subaru":
        dealers = SUBARU_DEALERS
        if not dealers:
            print(f"No {args.brand} dealers configured. Please add dealers to the SUBARU_DEALERS list.")
            sys.exit(1)
    else:
        print(f"Unknown brand: {args.brand}")
        sys.exit(1)
    
    print(f'\npriceScraper.py | made by github.com/se-t-h')
    print(f'\nbrand: {brand_name}\npart number: {part_number}\n')
    print(f'fetching prices using {args.threads} threads...')
    
    prices = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_dealer = {
            executor.submit(process_dealer, dealer, part_number, args): dealer 
            for dealer in dealers
        }
        
        for future in concurrent.futures.as_completed(future_to_dealer):
            dealer_url, price = future.result()
            if dealer_url is not None and price is not None:
                prices[dealer_url] = price
    
    print(f"\n=== {brand_name} Results (Sorted by Price) ===")
    sorted_prices = {k: v for k, v in sorted(prices.items(), key=lambda item: item[1])}
    
    if not sorted_prices:
        print(f"No prices found for this {args.brand} part number.")
        return
        
    for i, (dealer_url, price) in enumerate(sorted_prices.items(), 1):
        print(f'[{i}] {dealer_url} ... ${price}')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)