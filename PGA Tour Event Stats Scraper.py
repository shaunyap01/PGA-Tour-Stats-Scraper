import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import re
import time

# === Ensure script works from its own directory ===
os.chdir(Path(__file__).resolve().parent)

# === CONFIG ===
X_API_KEY = "da2-gsrx5bibzbb4njvhl7t37wqyl4"
YEARS = [# Insert years to scrape below
        2025, 2024, 2023, 2022, 2021,
        2020, 2019, 2018, 2017, 2016,
        2015, 2014, 2013, 2012, 2011,
        2010, 2009, 2008, 2007, 2006,
        2005, 2004
        ]
BASE_DIR = Path("PGA Tour Event Stats")

# === UTILS ===
def clean_filename(text: str) -> str:
    text = re.sub(r'[\\/:"*?<>|]+', '', text)
    return text.strip()

def extract_tournament_date(last_processed: str, year: int) -> str:
    try:
        parts = last_processed.split(", ")
        if len(parts) < 2:
            return None
        raw_date = parts[1]
        parsed = datetime.strptime(f"{raw_date} {year}", "%b %d %Y")
        return parsed.strftime("%Y-%m-%d")
    except Exception:
        return None

def get_tournament_pills(year: int):
    payload = {
        "operationName": "StatDetails",
        "variables": {
            "tourCode": "R",
            "statId": "108",
            "year": year,
            "eventQuery": None
        },
        "query": """
        query StatDetails($tourCode: TourCode!, $statId: String!, $year: Int, $eventQuery: StatDetailEventQuery) {
          statDetails(
            tourCode: $tourCode,
            statId: $statId,
            year: $year,
            eventQuery: $eventQuery
          ) {
            tournamentPills {
              tournamentId
              displayName
            }
          }
        }
        """
    }

    res = requests.post("https://orchestrator.pgatour.com/graphql", json=payload, headers={"x-api-key": X_API_KEY})
    res.raise_for_status()
    return res.json()["data"]["statDetails"]["tournamentPills"]

def get_event_stat(stat_id: str, tournament_id: str, year: int):
    payload = {
        "operationName": "StatDetails",
        "variables": {
            "tourCode": "R",
            "statId": stat_id,
            "year": year,
            "eventQuery": {
                "queryType": "EVENT_ONLY",
                "tournamentId": tournament_id
            }
        },
        "query": """
        query StatDetails($tourCode: TourCode!, $statId: String!, $year: Int, $eventQuery: StatDetailEventQuery) {
          statDetails(
            tourCode: $tourCode,
            statId: $statId,
            year: $year,
            eventQuery: $eventQuery
          ) {
            statTitle
            lastProcessed
            rows {
              __typename
              ... on StatDetailsPlayer {
                rank
                playerName
                stats {
                  statName
                  statValue
                }
              }
            }
          }
        }
        """
    }

    res = requests.post("https://orchestrator.pgatour.com/graphql", json=payload, headers={"x-api-key": X_API_KEY})
    res.raise_for_status()
    return res.json()["data"]["statDetails"]

# === DEFINE ALL STATS TO SCRAPE ===
STAT_MAP = {
    "Strokes Gained": {
        # 1 folder
        "Strokes Gained Leaders": {
            # 6 .csv files
            "02675": "SG Total",
            "02674": "SG Tee To Green",
            "02567": "SG Off The Tee",
            "02568": "SG Approach The Green",
            "02569": "SG Around The Green",
            "02564": "SG Putting"
        }
    },
    "Off The Tee": {
        # 6 folders
        "Driving Leaders": {
            # 6 .csv files
            "02674": "SG Tee To Green",
            "02567": "SG Off The Tee",
            "129": "Total Driving",
            "101": "Driving Distance",
            "102": "Driving Accuracy Percentage",
            "02402": "Ball Speed"
        },
        "Distance (All Drives)": {
            # 20 .csv files
            "159": "Longest Drives",
            "101": "Driving Distance",
            "496": "Driving Pct. 320+ (Measured)",
            "495": "Driving Pct. 300-320 (Measured)",
            "454": "Driving Pct. 300+ (Measured)",
            "455": "Driving Pct. 280-300 (Measured)",
            "456": "Driving Pct. 260-280 (Measured)",
            "457": "Driving Pct. 240-260 (Measured)",
            "458": "Driving Pct. Inside incl. 240 (Measured)",
            "317": "Driving Distance - All Drives",
            "02433": "Driving Pct. 320+ (All Drives)",
            "02432": "Driving Pct. 300-320 (All Drives)",
            "214": "Driving Pct. 300+ (All Drives)",
            "215": "Driving Pct. 280-300 (All Drives)",
            "216": "Driving Pct. 260-280 (All Drives)",
            "217": "Driving Pct. 240-260 (All Drives)",
            "218": "Driving Pct. Inside incl. 240 (All Drives)",
            "02341": "Percentage of Yardage covered by Tee Shots",
            "02342": "Percentage of Yardage covered by Tee Shots - Par 4's",
            "02343": "Percentage of Yardage covered by Tee Shots - Par 5's"
            },
        "Distance (Measured Drives)": {
            # 8 .csv files
            "101": "Driving Distance",
            "496": "Driving Pct. 320+ (Measured)",
            "495": "Driving Pct. 300-320 (Measured)",
            "454": "Driving Pct. 300+ (Measured)",
            "455": "Driving Pct. 280-300 (Measured)",
            "456": "Driving Pct. 260-280 (Measured)",
            "457": "Driving Pct. 240-260 (Measured)",
            "458": "Driving Pct. Inside incl. 240 (Measured)"           
        },
        "Accuracy": {
            # 14 .csv files
            "102": "Driving Accuracy Percentage",
            "02435": "Rough Tendency",
            "459": "Left Rough Tendency",
            "460": "Right Rough Tendency",
            "080": "Right Rough Tendency (RTP Score)",
            "081": "Left Rough Tendency (RTP Score)",
            "01008": "Fairway Bunker Tendency",
            "461": "Missed Fairway Percent - Other",
            "213": "Hit Fairway Percentage",
            "02420": "Distance from Edge of Fairway",
            "02421": "Distance from Center of Fairway",
            "02422": "Left Tendency",
            "02423": "Right Tendency",
            "02438": "Good Drive Percentage"
        },
        "Radar": {
            # 12 .csv files
            "02401": "Club Head Speed",
            "02402": "Ball Speed",
            "02403": "Smash Factor",
            "02404": "FLaunch Angle",
            "02405": "Spin Rate",
            "02406": "Distance to Apex",
            "02407": "Apex Height",
            "02408": "Hang Time",
            "02409": "Carry Distance",
            "02410": "Carry Efficiency",
            "02411": "Total Distance Efficiency",
            "02412": "Total Driving Efficiency"
        },
        "Scoring": {
            # 2 .csv files
            "080": "Right Rough Tendency (RTP Score)",
            "081": "Left Rough Tendency (RTP Score)"
        }
    },
    "Approach the Green": {
        # 7 folders
        "Approach Leaders": {
            # 6 .csv files
            "02568": "SG: Approach the Green",
            "158": "Ball Striking",
            "103": "Greens in Regulation Percentage",
            "331": "Proximity to Hole",
            "02331": "Approaches from Outside 100 yards",
            "02329": "Approaches from inside 100 yards"
        },
        "Greens in Regulation": {
            # 15 .csv files
            "103": "Greens in Regulation Percentage",
            "02437": "Greens or Fringe in Regulation",
            "326": "GIR Percentage - 200+ yards",
            "327": "GIR Percentage - 175-200 yards",
            "328": "GIR Percentage - 150-175 yards",
            "329": "GIR Percentage - 125-150 yards",
            "330": "GIR Percentage - Inside 125 yards",
            "077": "GIR Percentage - 100-125 yards",
            "02332": "GIR Percentage - 100+ yards",
            "02330": "GIR Percentage - Inside 100 yards",
            "078": "GIR Percentage - 75-100 yards",
            "079": "GIR Percentage - Inside 75 yards",
            "190": "GIR Percentage from Fairway",
            "02434": "GIR Pct. - Fairway Bunker",
            "199": "GIR Percentage from Other than Fairway" 
        },
        "Accuracy from Fairway": {
            # 16 .csv files
            "331": "Proximity to Hole",
            "02361": "Approaches from Outside 275 yards",
            "02360": "Approaches from 250-275 yards",
            "02359": "Approaches from 225-250 yards",
            "02358": "Approaches from 200-225 yards",
            "336": "Approaches from Outside 200 yards",
            "337": "Approaches from 175-200 yards",
            "338": "Approaches from 150-175 yards",
            "339": "Approaches from 125-150 yards",
            "340": "Approaches from 50-125 yards",
            "074": "Approaches from 100-125 yards",
            "075": "Approaches from 75-100 yards",
            "076": "Approaches from 50-75 yards",
            "02329": "Approaches from inside 100 yards",
            "02331": "Approaches from Outside 100 yards",
            "431": "Fairway Proximity"
        },
        "Accuracy from Rough": {
            # 17 .csv files
            "437": "Rough Proximity",
            "432": "Left Rough Proximity",
            "433": "Right Rough Proximity",
            "02375": "Approaches from Outside 275 yards (Rgh)",
            "02374": "Approaches from 250-275 yards (Rgh)",
            "02373": "Approaches from 225-250 yards (Rgh)",
            "02372": "Approaches from 200-225 yards (Rgh)",
            "02371": "Approaches from Outside 100 yards (Rgh)",
            "02370": "Approaches from inside 100 yards (Rgh)",
            "02369": "Approaches from Outside 200 yards (Rgh)",
            "02368": "Approaches from 175-200 yards (Rgh)",
            "02367": "Approaches from 150-175 yards (Rgh)",
            "02366": "Approaches from 125-150 yards (Rgh)",
            "02365": "Approaches from 50-125 yards (Rgh)",
            "02364": "Approaches from 100-125 yards (Rgh)",
            "02363": "Approaches from 75-100 yards (Rgh)",
            "02362": "Approaches from 50-75 yards (Rgh)"
        },
        "Scoring": {
            # 38 .csv files
            "02333": "Birdie or Better Percentage - Fairway",
            "02334": "Birdie or Better Percentage - Left Rough",
            "02335": "Birdie or Better Percentage - Right Rough",
            "02336": "Birdie or Better Percentage - Rough",
            "357": "Birdie or Better Percentage - 200+ yards",
            "358": "Birdie or Better Percentage - 175-200 yards",
            "359": "Birdie or Better Percentage - 150-175 yards",
            "360": "Birdie or Better Percentage - 125-150 yards",
            "361": "Birdie or Better Percentage - Inside 125 yards",
            "02379": "Approach Outside 275 yards (RTP)",
            "02378": "Approach 250-275 yards (RTP)",
            "02377": "Approach 225-250 yards (RTP)",
            "02376": "Approach 200-225 yards (RTP)",
            "480": "Approach Outside 200 yards (RTP Score)",
            "479": "Approach 175-200 yards (RTP Score)",
            "478": "Approach 150-175 yards (RTP Score)",
            "473": "Approach 125-150 yards (RTP Score)",
            "472": "Approach Inside 125 yards (RTP Score)",
            "028": "Approach 100-125 yards (RTP Score)",
            "029": "Approach 75-100 yards (RTP Score)",
            "030": "Approach 50-75 yards (RTP Score)",
            "02380": "Approaches 50-75 yards-Rgh (RTP)",
            "02381": "Approaches 75-100 yards-Rgh (RTP)",
            "02382": "Approaches 100-125 yards-Rgh (RTP)",
            "02383": "Approaches 50-125 yards-Rgh (RTP)",
            "02384": "Approaches 125-150 yards-Rgh (RTP)",
            "02385": "Approaches 150-175 yards-Rgh (RTP)",
            "02386": "Approaches 175-200 yards-Rgh (RTP)",
            "02387": "Approaches Outside 200 yards-Rgh (RTP)",
            "02388": "Approaches Inside 100 yards-Rgh (RTP)",
            "02389": "Approaches Outside 100 yards-Rgh (RTP)",
            "02390": "Approaches 200-225 yards-Rgh (RTP)",
            "02391": "Approaches 225-250 yards-Rgh (RTP)",
            "02392": "Approaches 250-275 yards-Rgh (RTP)",
            "02393": "Approaches Outside 275 yards-Rgh (RTP)",
            "469": "Approaches Left Rough (RTP Score)",
            "470": "Approaches Right Rough (RTP Score)",
            "471": "Fairway Approach (RTP Score)"
        },
        "Going for it": {
            # 6 .csv files
            "419": "Going for the Green",
            "486": "Going for the Green - Hit Green Pct.",
            "02357": "Going for the Green - Birdie or Better",
            "436": "Par 5 Going for the Green",
            "02426": "Average Going for it Shot Distance (in Yards)",
            "02431": "Average Distance after Going for it Shot"
        },
        "Holeouts Other": {
            # 7 .csv files
            "350": "Total Hole Outs",
            "351": "Longest Hole Outs (in yards)",
            "02325": "Average Approach Shot Distance",
            "02338": "Average Approach Distance - Birdie or Better",
            "02339": "Average Approach Distance - Par",
            "02340": "Average Approach Distance - Bogey or Worse",
            "02430": "Average Distance to Hole After Tee Shot"
        }
    },
    "Around the Green": {
        # 4 folders
        "Short Game Leaders": {
            # 6 .csv files
            "02569": "SG: Around-the-Green",
            "130": "Scrambling",
            "374": "Proximity to Hole (ARG)",
            "111": "Sand Save Percentage",
            "363": "Scrambling from the Rough",
            "366": "Scrambling from Outside 30 yards"
        },
        "Up and Down": {
            # 13 .csv files
            "130": "Scrambling",
            "362": "Scrambling from the Sand",
            "363": "Scrambling from the Rough",
            "365": "Scrambling from Other Locations",
            "366": "Scrambling from Outside 30 yards",
            "367": "Scrambling from 20-30 yards",
            "368": "Scrambling from 10-20 yards",
            "369": "Scrambling from Inside 10 yards",
            "111": "Sand Save Percentage",
            "370": "Sand Saves from 30+ yards",
            "371": "Sand Saves from 20-30 yards",
            "372": "Sand Saves from 10-20 yards",
            "373": "Sand Saves from Inside 10 yards"
        },
        "Accuracy": {
            # 9 .csv files
            "374": "Proximity to Hole (ARG)",
            "375": "Proximity to Hole from Sand",
            "376": "Proximity to Hole from Rough",
            "378": "Proximity to Hole from Other Locations",
            "379": "Proximity to Hole from 30+ yards",
            "380": "Proximity to Hole from 20-30 yards",
            "381": "Proximity to Hole from 10-20 yards",
            "382": "Proximity to Hole from Inside 10 yards",
            "481": "Scrambling Average Distance to Hole"
        },
        "Scoring": {
            # 4 .csv files
            "466": "Scrambling Outside 30 yds (RTP Score)",
            "467": "Scrambling 20-30 yds (RTP Score)",
            "468": "Scrambling 10-20 yds (RTP Score)",
            "464": "Scrambling Rough (RTP Score)"
        }
    },
    "Putting": {
        # 8 folders
        "Putting Leaders": {
            # 6 .csv files
            "02564": "SG: Putting",
            "104": "Putting Average",
            "119": "Putts Per Round",
            "413": "One-Putt Percentage",
            "426": "3-Putt Avoidance",
            "484": "Putting - Inside 10'",
            
        },
        "Putting Averages": {
            # 5 .csv files
            "02428": "Total Putting",
            "02439": "Bonus Putting",
            "104": "Putting Average",
            "402": "Overall Putting Average",
            "115": "Birdie or Better Conversion Percentage"
        },
        "Putts per Round": {
            # 9 .csv files
            "119": "Putts Per Round",
            "393": "Putts per Round - Round 1",
            "394": "Putts per Round - Round 2",
            "395": "Putts per Round - Round 3",
            "396": "Putts per Round - Round 4",
            "398": "1-Putts per Round",
            "399": "2-Putts per Round",
            "400": "3-Putts per Round",
            "401": "3+ Putts per Round"
        },
        "One-Putts": {
            # 13 .csv files
            "413": "One-Putt Percentage",
            "414": "One-Putt Percentage - Round 1",
            "415": "One-Putt Percentage - Round 2",
            "416": "One-Putt Percentage - Round 3",
            "417": "One-Putt Percentage - Round 4",
            "420": "Total 1 Putts - Inside 5'",
            "421": "Total 1 Putts - 5-10'",
            "422": "Total 1 Putts - 10-15'",
            "423": "Total 1 Putts - 15-20'",
            "424": "Total 1 Putts - 20-25'",
            "425": "Total 1 Putts - Outside 25'",
            "398": "1-Putts per Round",
            "498": "Longest Putts"
        },
        "Three-Putts": {
            # 19 .csv files
            "426": "3-Putt Avoidance",
            "427": "3-Putt Avoidance - Round 1",
            "428": "3-Putt Avoidance - Round 2",
            "429": "3-Putt Avoidance - Round 3",
            "430": "3-Putt Avoidance - Round 4",
            "068": "3-Putt Avoidance - Inside 5'",
            "069": "3-Putt Avoidance - 5-10'",
            "070": "3-Putt Avoidance - 10-15'",
            "145": "3-Putt Avoidance - 15-20'",
            "146": "3-Putt Avoidance - 20-25'",
            "147": "3-Putt Avoidance Outside 25'",
            "441": "Total 3 Putts - Inside 5'",
            "442": "Total 3 Putts - 5-10'",
            "443": "Total 3 Putts - 10-15'",
            "444": "Total 3 Putts - 15-20'",
            "445": "Total 3 Putts - 20-25'",
            "446": "Total 3 Putts - Outside 25'",
            "400": "3-Putts per Round",
            "401": "3+ Putts per Round"
        },
        "All Putts Made by Dist.": {
            # 23 .csv files
            "408": "Putting from Outside 25'",
            "02429": "Putting from - Outside 20'",
            "02329": "Putting from 15-25'",
            "407": "Putting from - 20-25'",
            "406": "Putting from - 15-20'",
            "02327": "Putting from 5-15'",
            "405": "Putting from - 10-15'",
            "484": "Putting - Inside 10'",
            "404": "Putting from 5-10'",
            "02427": "Putting from 3-5'",
            "403": "Putting from Inside 5'",
            "348": "Putting from 10'",
            "347": "Putting from 9'",
            "346": "Putting from 8'",
            "345": "Putting from 7'",
            "344": "Putting from 6'",
            "343": "Putting from 5'",
            "356": "Putting from - Outside 10'",
            "485": "Putting from 4-8'",
            "342": "Putting from 4'",
            "341": "Putting from 3'",
            "434": "Putts Made Per Event Over 10'",
            "435": "Putts Made Per Event Over 20'"
        },
        "Avg. Putting Dist.": {
            # 11 .csv files
            "438": "Average Distance of Putts made",
            "02440": "Average Distance of Birdie putts made",
            "02442": "Average Distance of Eagle putts made",
            "135": "Putts made Distance",
            "349": "Approach Putt Performance",
            "409": "Average Putting Distance - All 1 putts",
            "410": "Average Putting Distance - All 2 putts",
            "411": "Average Putting Distance - All 3 putts",
            "389": "Average Putting Distance - GIR 1 Putts",
            "390": "Average Putting Distance - GIR 2 Putts",
            "391": "Average Putting Distance - GIR 3 Putts"
        },
        "GIR Putts Made by Dist.": {
            # 7 .csv files
            "073": "GIR Putting Avg Outside 35'",
            "072": "GIR Putting Avg - 30-35'",
            "071": "GIR Putting Avg - 25-30'",
            "388": "GIR Putting - Outside 25'",
            "387": "GIR Putting - 20-25'",
            "386": "GIR Putting - 15-20'",
            "385": "GIR Putting - 10-15'"
        }
    },
    "Scoring": {
        # 12 folders
        "Scoring Leaders": {
            # 8 .csv files
            "02675": "SG: Total",
            "120": "Scoring Average",
            "156": "Birdie Average",
            "352": "Birdie or Better Percentage",
            "02414": "Bogey Avoidance",
            "142": "Par 3 Scoring Average",
            "143": "Par 4 Scoring Average",
            "144": "Par 5 Scoring Average"
        },
        "Scoring Overall": {
            # 5 .csv files
            "120": "Scoring Average",
            "108": "Scoring Average (Actual)",
            "116": "Scoring Average Before Cut",
            "02417": "Stroke Differential Field Average",
            "299": "Lowest Round",
            # "152": "Rounds in the 60s", # Doesn't have 'Tournament Only' data
            # "153": "Sub-Par Rounds" # Doesn't have 'Tournament Only' data
        },
        "Under Par Scoring": {
            # 22 .csv files
            "156": "Birdie Average",
            "107": "Total Birdies",
            "155": "Eagles (Holes per)",
            "106": "Total Eagles",
            "105": "Par Breakers",
            "160": "Bounce Back",
            "02415": "Birdie to Bogey Ratio",
            "112": "Par 3 Birdie or Better Leaders",
            "113": "Par 4 Birdie or Better Leaders",
            "114": "Par 5 Birdie or Better Leaders",
            "447": "Par 4 Eagle Leaders",
            "448": "Par 5 Eagle Leaders",
            "352": "Birdie or Better Percentage",
            "357": "Birdie or Better Percentage - 200+ yards",
            "358": "Birdie or Better Percentage - 175-200 yards",
            "359": "Birdie or Better Percentage - 150-175 yards",
            "360": "Birdie or Better Percentage - 125-150 yards",
            "361": "Birdie or Better Percentage - Inside 125 yards",
            "02333": "Birdie or Better Percentage - Fairway",
            "02334": "Birdie or Better Percentage - Left Rough",
            "02335": "Birdie or Better Percentage - Right Rough",
            "02336": "Birdie or Better Percentage - Rough"
        },
        "Over Par Scoring": {
            # 4 .csv files
            "02414": "Bogey Avoidance",
            "02415": "Birdie to Bogey Ratio",
            "02416": "Reverse Bounce Back",
            "02419": "Bogey Average"
        },
        "Scoring by Round": {
            # 17 .csv files
            "118": "Final Round Scoring Average",
            "219": "Final Round Performance",
            "220": "Top 10 Final Round Performance",
            "309": "Top 5 Final Round Performance",
            "310": "11-25 Final Round Performance",
            "311": "25+ Final Round Performance",
            "453": "6-10 Final Round Performance",
            "148": "Round 1 Scoring Average",
            "149": "Round 2 Scoring Average",
            "117": "Round 3 Scoring Average",
            "285": "Round 4 Scoring Average",
            "245": "Front 9 Round 1 Scoring Average",
            "246": "Back 9 Round 1 Scoring Average",
            "253": "Front 9 Round 2 Scoring Average",
            "254": "Back 9 Round 2 Scoring Average",
            "261": "Front 9 Round 3 Scoring Average",
            "269": "Front 9 Round 4 Scoring Average"
        },
        "Par 3 4 5 Scoring": {
            # 10 .csv files
            "171": "Par 3 Performance",
            "142": "Par 3 Scoring Average",
            "112": "Par 3 Birdie or Better Leaders",
            "172": "Par 4 Performance",
            "143": "Par 4 Scoring Average",
            "113": "Par 4 Birdie or Better Leaders",
            "173": "Par 5 Performance",
            "144": "Par 5 Scoring Average",
            "448": "Par 5 Eagle Leaders",
            "114": "Par 5 Birdie or Better Leaders"
        },
        "Front 9 Scoring": {
            # 6 .csv files
            "207": "Front 9 Scoring Average",
            "301": "Front 9 Lowest Round",
            "245": "Front 9 Round 1 Scoring Average",
            "253": "Front 9 Round 2 Scoring Average",
            "261": "Front 9 Round 3 Scoring Average",
            "269": "Front 9 Round 4 Scoring Average"
        },
        "Back 9 Scoring": {
            # 6 .csv files
            "208": "Back 9 Scoring Average",
            "302": "Back 9 Lowest Round",
            "246": "Back 9 Round 1 Scoring Average",
            "254": "Back 9 Round 2 Scoring Average",
            "262": "Back 9 Round 3 Scoring Average",
            "270": "Back 9 Round 4 Scoring Average"
        },
        "Early Scoring": {
            # 18 .csv files
            # Usually missing `266`, `274` due to no Tenth Tee starts on rounds 3 & 4 - no stats available
            "292": "Early Scoring Average",
            "303": "Early Lowest Round",
            "209": "First Tee Early Scoring Average",
            "210": "Tenth Tee Early Scoring Average",
            "247": "Early Round 1 Scoring Average",
            "255": "Early Round 2 Scoring Average",
            "263": "Early Round 3 Scoring Average",
            "271": "Early Round 4 Scoring Average",
            "249": "First Tee Early Round 1 Scoring Average",
            "250": "Tenth Tee Early Round 1 Scoring Average",
            "257": "First Tee Early Round 2 Scoring Average",
            "258": "Tenth Tee Early Round 2 Scoring Average",
            "265": "First Tee Early Round 3 Scoring Average",
            "266": "Tenth Tee Early Round 3 Scoring Average",
            "273": "First Tee Early Round 4 Scoring Average",
            "274": "Tenth Tee Early Round 4 Scoring Average",
            "305": "First Tee Early Lowest Round",
            "306": "Tenth Tee Early Lowest Round"
        },
        "Late Scoring": {
            # 18 .csv files
            # Usually missing `268`, `276` due to no Tenth Tee starts on rounds 3 & 4 - no stats available
            "293": "Late Scoring Average",
            "304": "Late Lowest Round",
            "248": "Late Round 1 Scoring Average",
            "256": "Late Round 2 Scoring Average",
            "264": "Late Round 3 Scoring Average",
            "272": "Late Round 4 Scoring Average",
            "211": "First Tee Late Scoring Average",
            "212": "Tenth Tee Late Scoring Average",
            "251": "First Tee Late Round 1 Scoring Average",
            "252": "Tenth Tee Late Round 1 Scoring Average",
            "259": "First Tee Late Round 2 Scoring Average",
            "260": "Tenth Tee Late Round 2 Scoring Average",
            "267": "First Tee Late Round 3 Scoring Average",
            "268": "Tenth Tee Late Round 3 Scoring Average",
            "275": "First Tee Late Round 4 Scoring Average",
            "276": "Tenth Tee Late Round 4 Scoring Average",
            "307": "First Tee Late Lowest Round",
            "308": "Tenth Tee Late Lowest Round"
        },
        "Scoring Off the 1st Tee": {
            # 12 .csv files
            "209": "First Tee Early Scoring Average",
            "211": "First Tee Late Scoring Average",
            "249": "First Tee Early Round 1 Scoring Average",
            "251": "First Tee Late Round 1 Scoring Average",
            "257": "First Tee Early Round 2 Scoring Average",
            "259": "First Tee Late Round 2 Scoring Average",
            "265": "First Tee Early Round 3 Scoring Average",
            "267": "First Tee Late Round 3 Scoring Average",
            "273": "First Tee Early Round 4 Scoring Average",
            "275": "First Tee Late Round 4 Scoring Average",
            "305": "First Tee Early Lowest Round",
            "307": "First Tee Late Lowest Round"
        },
        "Scoring Off the 10th Tee": {
            # 12 .csv files
            # Usually missing `266`, `274` due to no Tenth Tee starts on rounds 3 & 4 - no stats available
            "210": "Tenth Tee Early Scoring Average",
            "212": "Tenth Tee Late Scoring Average",
            "250": "Tenth Tee Early Round 1 Scoring Average",
            "252": "Tenth Tee Late Round 1 Scoring Average",
            "258": "Tenth Tee Early Round 2 Scoring Average",
            "260": "Tenth Tee Late Round 2 Scoring Average",
            "266": "Tenth Tee Early Round 3 Scoring Average",
            "268": "Tenth Tee Late Round 3 Scoring Average",
            "274": "Tenth Tee Early Round 4 Scoring Average",
            "276": "Tenth Tee Late Round 4 Scoring Average",
            "306": "Tenth Tee Early Lowest Round",
            "308": "Tenth Tee Late Lowest Round"
        }
    }
}

# === MAIN SCRAPER ===
def run_scraper():
    for year in YEARS:
        print(f"\n📆 Scraping Year: {year}")

        try:
            tournaments = get_tournament_pills(year)
        except Exception as e:
            print(f"❌ Failed to load tournaments for {year}: {e}")
            continue

        for tournament in tournaments:
            tournament_id = tournament["tournamentId"]
            tournament_name = clean_filename(tournament["displayName"])

            for category, subcats in STAT_MAP.items():
                for subcat, stats in subcats.items():
                    for stat_id, stat_title in stats.items():
                        try:
                            stat_data = get_event_stat(stat_id, tournament_id, year)
                            if not stat_data or not stat_data.get("rows"):
                                continue

                            last_processed = stat_data.get("lastProcessed")
                            date_str = extract_tournament_date(last_processed, year)
                            if not date_str:
                                continue

                            rows = []
                            for r in stat_data["rows"]:
                                if r.get("__typename") != "StatDetailsPlayer" or "stats" not in r:
                                    continue
                                row = {
                                    "rank": r.get("rank"),
                                    "player": r.get("playerName"),
                                    **{s["statName"]: s["statValue"] for s in r["stats"]}
                                }
                                rows.append(row)

                            if not rows:
                                continue

                            df = pd.DataFrame(rows)
                            folder = BASE_DIR / str(year) / f"{date_str}, {tournament_name}" / category / subcat
                            folder.mkdir(parents=True, exist_ok=True)

                            filename = f"{date_str}, {stat_title}.csv"
                            df.to_csv(folder / filename, index=False)
                            print(f"✅ Saved: {folder / filename}")

                            time.sleep(0.1)

                        except Exception as e:
                            print(f"❌ Failed for {tournament_name} | {stat_id}: {e}")
                            continue

# === RUN ===
if __name__ == "__main__":
    run_scraper()