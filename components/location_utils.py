"""
Location utilities for cascading dropdowns (District -> City/Suburb).
Comprehensive mapping of all 25 Sri Lankan districts with their major cities,
towns, and suburbs sourced from divisional secretariat data.
"""

DISTRICT_CITY_MAP = {
    # ── Western Province ──────────────────────────────────────────────────────
    "Colombo": [
        # Colombo Municipal numbered zones
        "Colombo 1", "Colombo 2", "Colombo 3", "Colombo 4", "Colombo 5",
        "Colombo 6", "Colombo 7", "Colombo 8", "Colombo 9", "Colombo 10",
        "Colombo 11", "Colombo 12", "Colombo 13", "Colombo 14", "Colombo 15",
        # Southern suburbs
        "Dehiwala", "Mount Lavinia", "Moratuwa", "Rathmalana", "Ratmalana",
        "Kohuwala", "Nugegoda", "Maharagama", "Pannipitiya", "Kottawa",
        "Homagama", "Piliyandala", "Kesbewa", "Boralesgamuwa",
        # Eastern suburbs
        "Pelawatte", "Battaramulla", "Thalawathugoda", "Malabe", "Athurugiriya",
        "Kaduwela", "Rajagiriya", "Nawala", "Kotte", "Pitakotte",
        "Wellampitiya", "Kolonnawa", "Angoda", "Mulleriyawa",
        # Northern/Central suburbs
        "Padukka", "Hanwella", "Avissawella", "Hokandara", "Koswatta",
        "Madiwela", "Meegoda", "Godagama", "Mattegoda", "Polgasowita",
        "Papiliyana", "Depanama", "Makumbura", "Diyagama", "Attidiya",
        "Gothatuwa", "Ethul Kotte", "Bokundara", "Kahathuduwa",
    ],

    "Gampaha": [
        "Gampaha", "Negombo", "Wattala", "Ja-Ela", "Kelaniya", "Peliyagoda",
        "Kadawatha", "Kiribathgoda", "Ragama", "Ganemulla", "Kandana",
        "Katunayake", "Minuwangoda", "Mirigama", "Veyangoda", "Nittambuwa",
        "Divulapitiya", "Dankotuwa", "Mawatagama", "Attanagalla",
        "Biyagama", "Dompe", "Gampaha Town", "Hendala", "Ekala",
        "Mahara", "Kotugoda", "Seeduwa", "Liyanagemulla", "Pamunugama",
        "Udugampola", "Yakkala", "Delgoda", "Pugoda", "Mabole",
        "Hunupitiya", "Miriswatte", "Hapugoda", "Thalahena",
    ],

    "Kalutara": [
        "Kalutara", "Panadura", "Beruwala", "Horana", "Bandaragama",
        "Aluthgama", "Matugama", "Agalawatta", "Dodangoda", "Ingiriya",
        "Palindanuwara", "Bulathsinhala", "Millaniya", "Walallavita",
        "Madurawala", "Bombuwala", "Neboda", "Payagala", "Wadduwa",
        "Baduraliya", "Poruwadanda", "Katukurunda", "Dharga Town",
        "Maggona", "Kalutara North", "Kalutara South",
    ],

    # ── Central Province ──────────────────────────────────────────────────────
    "Kandy": [
        "Kandy", "Peradeniya", "Katugastota", "Digana", "Kundasale",
        "Lewella", "Ampitiya", "Gampola", "Nawalapitiya", "Hatton",
        "Teldeniya", "Akurana", "Pallekele", "Wattegama", "Daulagala",
        "Doluwa", "Gangawata Korale", "Harispattuwa", "Udunuwara",
        "Poojapitiya", "Medadumbara", "Yatinuwara", "Udapalatha",
        "Pathadumbara", "Thalathuoya", "Kadugannawa", "Pilimathalawa",
        "Gelioya", "Nuwara Eliya Road", "Peradeniya Road",
    ],

    "Matale": [
        "Matale", "Dambulla", "Sigiriya", "Rattota", "Ukuwela",
        "Pallepola", "Galewela", "Nalanda", "Laggala", "Wilgamuwa",
        "Yatawatta", "Ambanganga Korale", "Palapathwela", "Wahacotte",
        "Raththota", "Elkaduwa", "Naula", "Kiwul Ela",
    ],

    "Nuwara Eliya": [
        "Nuwara Eliya", "Hatton", "Talawakele", "Maskeliya", "Ragala",
        "Walapane", "Ambagamuwa", "Kotmale", "Hanguranketha", "Udapussellawa",
        "Lindula", "Bogawanthalawa", "Dickoya", "Kotagala", "Ginigathena",
        "Norwood", "Norton Bridge",
    ],

    # ── Southern Province ─────────────────────────────────────────────────────
    "Galle": [
        "Galle", "Hikkaduwa", "Ambalangoda", "Elpitiya", "Bentota",
        "Balapitiya", "Karandeniya", "Habaraduwa", "Akmeemana", "Baddegama",
        "Imaduwa", "Gonapinuwala", "Neluwa", "Niyagama", "Nagoda",
        "Welivitiya Divithura", "Yakkalamulla", "Thawalama", "Wanduramba",
        "Meirigama", "Agaliya", "Rathgama", "Koggala", "Unawatuna",
        "Closenburg", "Weligama Road",
    ],

    "Matara": [
        "Matara", "Weligama", "Dikwella", "Akuressa", "Hakmana",
        "Kamburupitiya", "Mulatiyana", "Malimbada", "Pasgoda", "Pitabeddara",
        "Thihagoda", "Welipitiya", "Athuraliya", "Devinuwara", "Mirissa",
        "Polhena", "Dampahala", "Kotapola", "Kirinda Puhulwella",
    ],

    "Hambantota": [
        "Hambantota", "Tangalle", "Tissamaharama", "Beliatta", "Weeraketiya",
        "Ambalantota", "Lunugamvehera", "Katuwana", "Okewela", "Hungama",
        "Angunakolapelessa", "Walasmulla", "Suriyawewa", "Sooriyawewa",
        "Kirama", "Chunnakam", "Magama",
    ],

    # ── Northern Province ─────────────────────────────────────────────────────
    "Jaffna": [
        "Jaffna", "Nallur", "Chavakachcheri", "Point Pedro", "Jaffna Town",
        "Manipay", "Kopay", "Nelliady", "Karainagar", "Velanai",
        "Kayts", "Islands",  "Sandilipay", "Uduvil", "Vaddukoddai",
        "Chankanai", "Delft", "Nainativu",
    ],

    "Kilinochchi": [
        "Kilinochchi", "Palai", "Poonakary", "Karachchi",
        "Pachchilaipalli", "Kandavalai",
    ],

    "Mannar": [
        "Mannar", "Nanatan", "Musali", "Madhu", "Manthai West",
        "Madu", "Pesalai",
    ],

    "Vavuniya": [
        "Vavuniya", "Vavuniya North", "Vavuniya South", "Vengalacheddikulam",
        "Cheddikulam", "Pappamoddai",
    ],

    "Mullaitivu": [
        "Mullaitivu", "Manthai East", "Maritimepattu", "Oddusuddan",
        "Puthukkudiyiruppu", "Thunukkai", "Welioya",
    ],

    # ── Eastern Province ──────────────────────────────────────────────────────
    "Batticaloa": [
        "Batticaloa", "Kattankudy", "Eravur", "Valaichchenai", "Chenkaladi",
        "Koralaipattu", "Manmunai North", "Manmunai South and Eruvil Pattu",
        "Manmunai West", "Porativu Pattu", "Paddippalai", "Vavunathivu",
    ],

    "Ampara": [
        "Ampara", "Kalmunai", "Sainthamaruthu", "Pottuvil", "Akkaraipattu",
        "Ninthavur", "Addalaichenai", "Sammanthurai", "Mahaoya",
        "Uhana", "Damana", "Dehiattakandiya", "Padiyathalawa",
        "Navithanveli", "Thirukkovil",
    ],

    "Trincomalee": [
        "Trincomalee", "Kinniya", "Kantale", "Muttur", "Seruvila",
        "Morawewa", "Gomarankadawala", "Kuchchaveli", "Thambalagamuwa",
        "Padavi Sripura", "China Bay",
    ],

    # ── North Western Province ────────────────────────────────────────────────
    "Kurunegala": [
        "Kurunegala", "Kuliyapitiya", "Nikaweratiya", "Mawathagama",
        "Narammala", "Pannala", "Alawwa", "Hettipola", "Wariyapola",
        "Galgamuwa", "Ibbagamuwa", "Kotavehera", "Polpithigama",
        "Ridigama", "Mahawa", "Yapahuwa", "Polgahawela", "Bingiriya",
        "Dodangaslanda", "Ehetuwewa", "Ganewatta", "Rasnayakapura",
        "Ududumbara",
    ],

    "Puttalam": [
        "Puttalam", "Chilaw", "Wennappuwa", "Marawila", "Nattandiya",
        "Anamaduwa", "Nawagattegama", "Mundel", "Dankotuwa", "Arachchikattuwa",
        "Kalpitiya", "Pallama", "Karuwalagaswewa", "Mahakumbukkadawala",
    ],

    # ── North Central Province ────────────────────────────────────────────────
    "Anuradhapura": [
        "Anuradhapura", "Kekirawa", "Medawachchiya", "Eppawala",
        "Tambuttegama", "Nochchiyagama", "Nuwaragam Palatha",
        "Kahatagasdigiliya", "Horowpothana", "Ipalogama",
        "Padaviya", "Rajanganaya", "Thirappane", "Galenbindunuwewa",
        "Mahavilachchiya", "Thalawa", "Mihintale",
    ],

    "Polonnaruwa": [
        "Polonnaruwa", "Kaduruwela", "Hingurakgoda", "Medirigiriya",
        "Lankapura", "Dimbulagala", "Elahera",
        "Thamankaduwa", "Habarana", "Welikanda",
    ],

    # ── Uva Province ─────────────────────────────────────────────────────────
    "Badulla": [
        "Badulla", "Bandarawela", "Haputale", "Welimada", "Mahiyanganaya",
        "Passara", "Hali-Ela", "Ella", "Diyatalawa", "Uva Paranagama",
        "Soranathota", "Meegahakiula", "Lunugala", "Kandaketiya",
        "Ridimaliyadda", "Rideemaliyadda",
    ],

    "Monaragala": [
        "Monaragala", "Bibile", "Wellawaya", "Buttala", "Medagama",
        "Kataragama", "Thanamalwila", "Badalkumbura", "Sewanagala",
        "Madulla", "Siyambalanduwa",
    ],

    # ── Sabaragamuwa Province ─────────────────────────────────────────────────
    "Ratnapura": [
        "Ratnapura", "Embilipitiya", "Balangoda", "Pelmadulla",
        "Eheliyagoda", "Kuruwita", "Godakawela", "Imbulpe",
        "Kahawatta", "Kolonne", "Kiriella", "Ayagama",
        "Nivitigala", "Weligepola",
    ],

    "Kegalle": [
        "Kegalle", "Mawanella", "Warakapola", "Aranayaka", "Rambukkana",
        "Ruwanwella", "Dehiowita", "Yatiyanthota", "Galigamuwa",
        "Deraniyagala", "Bulathkohupitiya", "Kitulgala",
    ],
}


def get_cities_for_district(district: str) -> list[str]:
    """Return sorted list of cities for a given district. Fallback to ['Unknown'] if missing."""
    cities = DISTRICT_CITY_MAP.get(district, ["Unknown"])
    # Ensure uniqueness, sort alphabetically, 'Unknown' always at the end
    unique_cities = sorted(list(set(c for c in cities if c != "Unknown")))
    unique_cities.append("Unknown")
    return unique_cities


def get_all_cities() -> list[str]:
    """Return a flat sorted list of all cities/suburbs across all districts."""
    all_cities = set()
    for cities in DISTRICT_CITY_MAP.values():
        for city in cities:
            if city != "Unknown":
                all_cities.add(city)
    return sorted(list(all_cities))
