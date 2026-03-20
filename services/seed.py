"""
Seed PSX stocks into the database.
Safe to run multiple times — uses upsert logic.
"""
from sqlalchemy.orm import Session
from models.stock import StockCache


PSX_STOCKS = [
    # Banking
    ("HBL",    "Habib Bank Limited",              "Banking"),
    ("MCB",    "MCB Bank Limited",                "Banking"),
    ("UBL",    "United Bank Limited",             "Banking"),
    ("BAHL",   "Bank Al-Habib Limited",           "Banking"),
    ("MEBL",   "Meezan Bank Limited",             "Banking"),
    ("NBP",    "National Bank of Pakistan",       "Banking"),
    ("ABL",    "Allied Bank Limited",             "Banking"),
    ("BAFL",   "Bank Alfalah Limited",            "Banking"),
    ("AKBL",   "Askari Bank Limited",             "Banking"),
    ("SCBPL",  "Standard Chartered Bank Pakistan","Banking"),
    ("SILK",   "Silkbank Limited",                "Banking"),
    ("SNBL",   "Soneri Bank Limited",             "Banking"),
    ("BOP",    "Bank of Punjab",                  "Banking"),
    ("JSBL",   "JS Bank Limited",                 "Banking"),
    ("FABL",   "Faysal Bank Limited",             "Banking"),
    # Energy
    ("OGDC",   "Oil & Gas Development Company",   "Energy"),
    ("PPL",    "Pakistan Petroleum Limited",      "Energy"),
    ("PSO",    "Pakistan State Oil",              "Energy"),
    ("MARI",   "Mari Petroleum Company",          "Energy"),
    ("POL",    "Pakistan Oilfields Limited",      "Energy"),
    ("SNGP",   "Sui Northern Gas Pipelines",      "Energy"),
    ("SSGC",   "Sui Southern Gas Company",        "Energy"),
    ("APL",    "Attock Petroleum Limited",        "Energy"),
    ("ATRL",   "Attock Refinery Limited",         "Energy"),
    ("NRL",    "National Refinery Limited",       "Energy"),
    # Cement
    ("LUCK",   "Lucky Cement Limited",            "Cement"),
    ("DGKC",   "D.G. Khan Cement Company",        "Cement"),
    ("MLCF",   "Maple Leaf Cement Factory",       "Cement"),
    ("CHCC",   "Cherat Cement Company",           "Cement"),
    ("PIOC",   "Pioneer Cement Limited",          "Cement"),
    ("KOHC",   "Kohat Cement Company",            "Cement"),
    ("FECTC",  "Fecto Cement Limited",            "Cement"),
    ("GWLC",   "Gharibwal Cement Limited",        "Cement"),
    ("ACPL",   "Attock Cement Pakistan",          "Cement"),
    ("POWER",  "Power Cement Limited",            "Cement"),
    # Fertilizer
    ("ENGRO",  "Engro Corporation Limited",       "Fertilizer"),
    ("EFERT",  "Engro Fertilizers Limited",       "Fertilizer"),
    ("FFC",    "Fauji Fertilizer Company",        "Fertilizer"),
    ("FATIMA", "Fatima Fertilizer Company",       "Fertilizer"),
    ("FFBL",   "Fauji Fertilizer Bin Qasim",      "Fertilizer"),
    # Power
    ("HUBC",   "Hub Power Company Limited",       "Power"),
    ("KAPCO",  "Kot Addu Power Company",          "Power"),
    ("NCPL",   "Nishat Chunian Power",            "Power"),
    ("KEL",    "K-Electric Limited",              "Power"),
    ("PKGP",   "Pakistan Gum & Chemicals",        "Power"),
    ("JPGL",   "Jhangir Power Generation",        "Power"),
    ("LPHEL",  "Laraib Energy Limited",           "Power"),
    # Technology
    ("SYS",    "Systems Limited",                 "Technology"),
    ("TRG",    "TRG Pakistan Limited",            "Technology"),
    ("NETSOL", "NetSol Technologies",             "Technology"),
    ("AVN",    "Avanceon Limited",                "Technology"),
    ("HUMNL",  "Human Interface Limited",         "Technology"),
    ("TELE",   "Telecard Limited",                "Technology"),
    ("WTL",    "WorldCall Telecom Limited",       "Technology"),
    # Pharma
    ("SEARL",  "The Searle Company Limited",      "Pharma"),
    ("HINOON", "Highnoon Laboratories",           "Pharma"),
    ("FEROZ",  "Ferozsons Laboratories",          "Pharma"),
    ("GLAXO",  "GlaxoSmithKline Pakistan",        "Pharma"),
    ("AGP",    "AGP Limited",                     "Pharma"),
    ("INIL",   "International Industries",        "Pharma"),
    ("ABBOTT", "Abbott Laboratories Pakistan",    "Pharma"),
    # Textile
    ("NCL",    "Nishat (Chunian) Limited",        "Textile"),
    ("GATM",   "Gul Ahmed Textile Mills",         "Textile"),
    ("KTML",   "Kohinoor Textile Mills",          "Textile"),
    ("GADT",   "Gadoon Textile Mills",            "Textile"),
    ("CRTM",   "Crescent Textile Mills",          "Textile"),
    ("AMTEX",  "Amtex Limited",                   "Textile"),
    ("IDYM",   "Indus Dyeing & Manufacturing",    "Textile"),
    ("ADMM",   "Adam Sugar Mills",                "Textile"),
    ("CLCPS",  "Chenab Limited",                  "Textile"),
    # Consumer / FMCG
    ("NESTLE", "Nestle Pakistan Limited",         "Consumer"),
    ("COLG",   "Colgate-Palmolive Pakistan",      "Consumer"),
    ("UNITY",  "Unity Foods Limited",             "Consumer"),
    ("QUICE",  "Quice Food Industries",           "Consumer"),
    ("ULEVER", "Unilever Pakistan",               "Consumer"),
    ("TREET",  "Treet Corporation Limited",       "Consumer"),
    ("WAVE",   "Wave Industries Limited",         "Consumer"),
    # Auto / Engineering
    ("PSMC",   "Pak Suzuki Motor Company",        "Automobile"),
    ("HCAR",   "Honda Atlas Cars Pakistan",       "Automobile"),
    ("INDU",   "Indus Motor Company",             "Automobile"),
    ("MTL",    "Millat Tractors Limited",         "Automobile"),
    ("ATLH",   "Atlas Honda Limited",             "Automobile"),
    ("GHNL",   "Ghani Global Holdings",           "Automobile"),
    # Steel / Industrial
    ("ISL",    "International Steels Limited",    "Steel"),
    ("ASTL",   "Amreli Steels Limited",           "Steel"),
    ("MUGHAL", "Mughal Iron & Steel",             "Steel"),
    ("INIL",   "International Industries Ltd",    "Steel"),
    # Real Estate / Misc
    ("PAEL",   "Pak Elektron Limited",            "Electronics"),
    ("HGFA",   "Husein Global Funding",           "Finance"),
    ("JLICL",  "Jubilee Life Insurance",          "Insurance"),
    ("AICL",   "Adamjee Insurance Company",       "Insurance"),
    ("NICL",   "National Insurance Company",      "Insurance"),
    ("EFU",    "EFU General Insurance",           "Insurance"),
    ("JGIDC",  "Jubilee General Insurance",       "Insurance"),
    # Sugar
    ("CSML",   "Crescent Sugar Mills",            "Sugar"),
    ("MSOT",   "Mirpurkhas Sugar Mills",          "Sugar"),
    ("AABS",   "Al-Abbas Sugar Mills",            "Sugar"),
    ("FRSM",   "Faran Sugar Mills",               "Sugar"),
    # Paper & Board
    ("PAKC",   "Packages Limited",                "Paper"),
    ("CEPB",   "Century Paper & Board Mills",     "Paper"),
    ("TPPL",   "Tri-Pack Films Limited",          "Paper"),
]


def seed_stocks(db: Session) -> int:
    """
    Insert all PSX stocks into stocks_cache.
    Skips duplicates. Returns count of newly inserted records.
    """
    inserted = 0
    existing_symbols = {
        row.symbol for row in db.query(StockCache.symbol).all()
    }

    for symbol, name, sector in PSX_STOCKS:
        if symbol in existing_symbols:
            continue
        stock = StockCache(
            symbol=symbol,
            name=name,
            sector=sector,
            is_active=1,
        )
        db.add(stock)
        inserted += 1

    if inserted > 0:
        try:
            db.commit()
            print(f"[seed] Inserted {inserted} stocks into stocks_cache")
        except Exception as e:
            db.rollback()
            print(f"[seed] Error: {e}")

    return inserted