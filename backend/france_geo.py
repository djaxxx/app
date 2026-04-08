# French Geographic Data
# Régions, Départements et principales villes de France

REGIONS_FRANCE = {
    "ARA": {"name": "Auvergne-Rhône-Alpes", "departments": ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"]},
    "BFC": {"name": "Bourgogne-Franche-Comté", "departments": ["21", "25", "39", "58", "70", "71", "89", "90"]},
    "BRE": {"name": "Bretagne", "departments": ["22", "29", "35", "56"]},
    "CVL": {"name": "Centre-Val de Loire", "departments": ["18", "28", "36", "37", "41", "45"]},
    "COR": {"name": "Corse", "departments": ["2A", "2B"]},
    "GES": {"name": "Grand Est", "departments": ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"]},
    "HDF": {"name": "Hauts-de-France", "departments": ["02", "59", "60", "62", "80"]},
    "IDF": {"name": "Île-de-France", "departments": ["75", "77", "78", "91", "92", "93", "94", "95"]},
    "NOR": {"name": "Normandie", "departments": ["14", "27", "50", "61", "76"]},
    "NAQ": {"name": "Nouvelle-Aquitaine", "departments": ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"]},
    "OCC": {"name": "Occitanie", "departments": ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"]},
    "PDL": {"name": "Pays de la Loire", "departments": ["44", "49", "53", "72", "85"]},
    "PAC": {"name": "Provence-Alpes-Côte d'Azur", "departments": ["04", "05", "06", "13", "83", "84"]},
    "GUA": {"name": "Guadeloupe", "departments": ["971"]},
    "MTQ": {"name": "Martinique", "departments": ["972"]},
    "GUF": {"name": "Guyane", "departments": ["973"]},
    "REU": {"name": "La Réunion", "departments": ["974"]},
    "MAY": {"name": "Mayotte", "departments": ["976"]},
}

DEPARTMENTS_FRANCE = {
    "01": {"name": "Ain", "region": "ARA", "chef_lieu": "Bourg-en-Bresse", "lat": 46.2056, "lon": 5.2257},
    "02": {"name": "Aisne", "region": "HDF", "chef_lieu": "Laon", "lat": 49.5639, "lon": 3.6200},
    "03": {"name": "Allier", "region": "ARA", "chef_lieu": "Moulins", "lat": 46.5670, "lon": 3.3325},
    "04": {"name": "Alpes-de-Haute-Provence", "region": "PAC", "chef_lieu": "Digne-les-Bains", "lat": 44.0933, "lon": 6.2356},
    "05": {"name": "Hautes-Alpes", "region": "PAC", "chef_lieu": "Gap", "lat": 44.5594, "lon": 6.0786},
    "06": {"name": "Alpes-Maritimes", "region": "PAC", "chef_lieu": "Nice", "lat": 43.7102, "lon": 7.2620},
    "07": {"name": "Ardèche", "region": "ARA", "chef_lieu": "Privas", "lat": 44.7356, "lon": 4.5975},
    "08": {"name": "Ardennes", "region": "GES", "chef_lieu": "Charleville-Mézières", "lat": 49.7719, "lon": 4.7161},
    "09": {"name": "Ariège", "region": "OCC", "chef_lieu": "Foix", "lat": 42.9653, "lon": 1.6053},
    "10": {"name": "Aube", "region": "GES", "chef_lieu": "Troyes", "lat": 48.2972, "lon": 4.0744},
    "11": {"name": "Aude", "region": "OCC", "chef_lieu": "Carcassonne", "lat": 43.2130, "lon": 2.3491},
    "12": {"name": "Aveyron", "region": "OCC", "chef_lieu": "Rodez", "lat": 44.3517, "lon": 2.5756},
    "13": {"name": "Bouches-du-Rhône", "region": "PAC", "chef_lieu": "Marseille", "lat": 43.2965, "lon": 5.3698},
    "14": {"name": "Calvados", "region": "NOR", "chef_lieu": "Caen", "lat": 49.1829, "lon": -0.3707},
    "15": {"name": "Cantal", "region": "ARA", "chef_lieu": "Aurillac", "lat": 44.9261, "lon": 2.4406},
    "16": {"name": "Charente", "region": "NAQ", "chef_lieu": "Angoulême", "lat": 45.6500, "lon": 0.1600},
    "17": {"name": "Charente-Maritime", "region": "NAQ", "chef_lieu": "La Rochelle", "lat": 46.1603, "lon": -1.1511},
    "18": {"name": "Cher", "region": "CVL", "chef_lieu": "Bourges", "lat": 47.0833, "lon": 2.4000},
    "19": {"name": "Corrèze", "region": "NAQ", "chef_lieu": "Tulle", "lat": 45.2667, "lon": 1.7667},
    "21": {"name": "Côte-d'Or", "region": "BFC", "chef_lieu": "Dijon", "lat": 47.3220, "lon": 5.0415},
    "22": {"name": "Côtes-d'Armor", "region": "BRE", "chef_lieu": "Saint-Brieuc", "lat": 48.5141, "lon": -2.7600},
    "23": {"name": "Creuse", "region": "NAQ", "chef_lieu": "Guéret", "lat": 46.1711, "lon": 1.8700},
    "24": {"name": "Dordogne", "region": "NAQ", "chef_lieu": "Périgueux", "lat": 45.1847, "lon": 0.7211},
    "25": {"name": "Doubs", "region": "BFC", "chef_lieu": "Besançon", "lat": 47.2378, "lon": 6.0241},
    "26": {"name": "Drôme", "region": "ARA", "chef_lieu": "Valence", "lat": 44.9333, "lon": 4.8917},
    "27": {"name": "Eure", "region": "NOR", "chef_lieu": "Évreux", "lat": 49.0269, "lon": 1.1508},
    "28": {"name": "Eure-et-Loir", "region": "CVL", "chef_lieu": "Chartres", "lat": 48.4439, "lon": 1.4892},
    "29": {"name": "Finistère", "region": "BRE", "chef_lieu": "Quimper", "lat": 47.9961, "lon": -4.1028},
    "30": {"name": "Gard", "region": "OCC", "chef_lieu": "Nîmes", "lat": 43.8367, "lon": 4.3601},
    "31": {"name": "Haute-Garonne", "region": "OCC", "chef_lieu": "Toulouse", "lat": 43.6047, "lon": 1.4442},
    "32": {"name": "Gers", "region": "OCC", "chef_lieu": "Auch", "lat": 43.6461, "lon": 0.5856},
    "33": {"name": "Gironde", "region": "NAQ", "chef_lieu": "Bordeaux", "lat": 44.8378, "lon": -0.5792},
    "34": {"name": "Hérault", "region": "OCC", "chef_lieu": "Montpellier", "lat": 43.6108, "lon": 3.8767},
    "35": {"name": "Ille-et-Vilaine", "region": "BRE", "chef_lieu": "Rennes", "lat": 48.1173, "lon": -1.6778},
    "36": {"name": "Indre", "region": "CVL", "chef_lieu": "Châteauroux", "lat": 46.8103, "lon": 1.6911},
    "37": {"name": "Indre-et-Loire", "region": "CVL", "chef_lieu": "Tours", "lat": 47.3941, "lon": 0.6848},
    "38": {"name": "Isère", "region": "ARA", "chef_lieu": "Grenoble", "lat": 45.1885, "lon": 5.7245},
    "39": {"name": "Jura", "region": "BFC", "chef_lieu": "Lons-le-Saunier", "lat": 46.6753, "lon": 5.5506},
    "40": {"name": "Landes", "region": "NAQ", "chef_lieu": "Mont-de-Marsan", "lat": 43.8900, "lon": -0.5000},
    "41": {"name": "Loir-et-Cher", "region": "CVL", "chef_lieu": "Blois", "lat": 47.5861, "lon": 1.3359},
    "42": {"name": "Loire", "region": "ARA", "chef_lieu": "Saint-Étienne", "lat": 45.4397, "lon": 4.3872},
    "43": {"name": "Haute-Loire", "region": "ARA", "chef_lieu": "Le Puy-en-Velay", "lat": 45.0436, "lon": 3.8853},
    "44": {"name": "Loire-Atlantique", "region": "PDL", "chef_lieu": "Nantes", "lat": 47.2184, "lon": -1.5536},
    "45": {"name": "Loiret", "region": "CVL", "chef_lieu": "Orléans", "lat": 47.9029, "lon": 1.9093},
    "46": {"name": "Lot", "region": "OCC", "chef_lieu": "Cahors", "lat": 44.4475, "lon": 1.4400},
    "47": {"name": "Lot-et-Garonne", "region": "NAQ", "chef_lieu": "Agen", "lat": 44.2033, "lon": 0.6167},
    "48": {"name": "Lozère", "region": "OCC", "chef_lieu": "Mende", "lat": 44.5178, "lon": 3.5000},
    "49": {"name": "Maine-et-Loire", "region": "PDL", "chef_lieu": "Angers", "lat": 47.4784, "lon": -0.5632},
    "50": {"name": "Manche", "region": "NOR", "chef_lieu": "Saint-Lô", "lat": 49.1167, "lon": -1.0833},
    "51": {"name": "Marne", "region": "GES", "chef_lieu": "Châlons-en-Champagne", "lat": 48.9575, "lon": 4.3631},
    "52": {"name": "Haute-Marne", "region": "GES", "chef_lieu": "Chaumont", "lat": 48.1133, "lon": 5.1389},
    "53": {"name": "Mayenne", "region": "PDL", "chef_lieu": "Laval", "lat": 48.0700, "lon": -0.7700},
    "54": {"name": "Meurthe-et-Moselle", "region": "GES", "chef_lieu": "Nancy", "lat": 48.6921, "lon": 6.1844},
    "55": {"name": "Meuse", "region": "GES", "chef_lieu": "Bar-le-Duc", "lat": 48.7736, "lon": 5.1594},
    "56": {"name": "Morbihan", "region": "BRE", "chef_lieu": "Vannes", "lat": 47.6586, "lon": -2.7600},
    "57": {"name": "Moselle", "region": "GES", "chef_lieu": "Metz", "lat": 49.1193, "lon": 6.1757},
    "58": {"name": "Nièvre", "region": "BFC", "chef_lieu": "Nevers", "lat": 46.9897, "lon": 3.1592},
    "59": {"name": "Nord", "region": "HDF", "chef_lieu": "Lille", "lat": 50.6292, "lon": 3.0573},
    "60": {"name": "Oise", "region": "HDF", "chef_lieu": "Beauvais", "lat": 49.4294, "lon": 2.0844},
    "61": {"name": "Orne", "region": "NOR", "chef_lieu": "Alençon", "lat": 48.4300, "lon": 0.0900},
    "62": {"name": "Pas-de-Calais", "region": "HDF", "chef_lieu": "Arras", "lat": 50.2919, "lon": 2.7800},
    "63": {"name": "Puy-de-Dôme", "region": "ARA", "chef_lieu": "Clermont-Ferrand", "lat": 45.7772, "lon": 3.0870},
    "64": {"name": "Pyrénées-Atlantiques", "region": "NAQ", "chef_lieu": "Pau", "lat": 43.2951, "lon": -0.3708},
    "65": {"name": "Hautes-Pyrénées", "region": "OCC", "chef_lieu": "Tarbes", "lat": 43.2328, "lon": 0.0781},
    "66": {"name": "Pyrénées-Orientales", "region": "OCC", "chef_lieu": "Perpignan", "lat": 42.6987, "lon": 2.8956},
    "67": {"name": "Bas-Rhin", "region": "GES", "chef_lieu": "Strasbourg", "lat": 48.5734, "lon": 7.7521},
    "68": {"name": "Haut-Rhin", "region": "GES", "chef_lieu": "Colmar", "lat": 48.0794, "lon": 7.3558},
    "69": {"name": "Rhône", "region": "ARA", "chef_lieu": "Lyon", "lat": 45.7640, "lon": 4.8357},
    "70": {"name": "Haute-Saône", "region": "BFC", "chef_lieu": "Vesoul", "lat": 47.6189, "lon": 6.1567},
    "71": {"name": "Saône-et-Loire", "region": "BFC", "chef_lieu": "Mâcon", "lat": 46.3069, "lon": 4.8286},
    "72": {"name": "Sarthe", "region": "PDL", "chef_lieu": "Le Mans", "lat": 48.0061, "lon": 0.1996},
    "73": {"name": "Savoie", "region": "ARA", "chef_lieu": "Chambéry", "lat": 45.5646, "lon": 5.9178},
    "74": {"name": "Haute-Savoie", "region": "ARA", "chef_lieu": "Annecy", "lat": 45.8992, "lon": 6.1294},
    "75": {"name": "Paris", "region": "IDF", "chef_lieu": "Paris", "lat": 48.8566, "lon": 2.3522},
    "76": {"name": "Seine-Maritime", "region": "NOR", "chef_lieu": "Rouen", "lat": 49.4432, "lon": 1.0999},
    "77": {"name": "Seine-et-Marne", "region": "IDF", "chef_lieu": "Melun", "lat": 48.5392, "lon": 2.6597},
    "78": {"name": "Yvelines", "region": "IDF", "chef_lieu": "Versailles", "lat": 48.8014, "lon": 2.1301},
    "79": {"name": "Deux-Sèvres", "region": "NAQ", "chef_lieu": "Niort", "lat": 46.3239, "lon": -0.4600},
    "80": {"name": "Somme", "region": "HDF", "chef_lieu": "Amiens", "lat": 49.8942, "lon": 2.2958},
    "81": {"name": "Tarn", "region": "OCC", "chef_lieu": "Albi", "lat": 43.9283, "lon": 2.1483},
    "82": {"name": "Tarn-et-Garonne", "region": "OCC", "chef_lieu": "Montauban", "lat": 44.0175, "lon": 1.3547},
    "83": {"name": "Var", "region": "PAC", "chef_lieu": "Toulon", "lat": 43.1242, "lon": 5.9280},
    "84": {"name": "Vaucluse", "region": "PAC", "chef_lieu": "Avignon", "lat": 43.9493, "lon": 4.8055},
    "85": {"name": "Vendée", "region": "PDL", "chef_lieu": "La Roche-sur-Yon", "lat": 46.6706, "lon": -1.4269},
    "86": {"name": "Vienne", "region": "NAQ", "chef_lieu": "Poitiers", "lat": 46.5802, "lon": 0.3404},
    "87": {"name": "Haute-Vienne", "region": "NAQ", "chef_lieu": "Limoges", "lat": 45.8336, "lon": 1.2611},
    "88": {"name": "Vosges", "region": "GES", "chef_lieu": "Épinal", "lat": 48.1725, "lon": 6.4492},
    "89": {"name": "Yonne", "region": "BFC", "chef_lieu": "Auxerre", "lat": 47.7986, "lon": 3.5672},
    "90": {"name": "Territoire de Belfort", "region": "BFC", "chef_lieu": "Belfort", "lat": 47.6400, "lon": 6.8600},
    "91": {"name": "Essonne", "region": "IDF", "chef_lieu": "Évry-Courcouronnes", "lat": 48.6249, "lon": 2.4503},
    "92": {"name": "Hauts-de-Seine", "region": "IDF", "chef_lieu": "Nanterre", "lat": 48.8924, "lon": 2.2071},
    "93": {"name": "Seine-Saint-Denis", "region": "IDF", "chef_lieu": "Bobigny", "lat": 48.9096, "lon": 2.4400},
    "94": {"name": "Val-de-Marne", "region": "IDF", "chef_lieu": "Créteil", "lat": 48.7833, "lon": 2.4667},
    "95": {"name": "Val-d'Oise", "region": "IDF", "chef_lieu": "Cergy", "lat": 49.0361, "lon": 2.0631},
    "971": {"name": "Guadeloupe", "region": "GUA", "chef_lieu": "Basse-Terre", "lat": 16.0000, "lon": -61.7167},
    "972": {"name": "Martinique", "region": "MTQ", "chef_lieu": "Fort-de-France", "lat": 14.6000, "lon": -61.0833},
    "973": {"name": "Guyane", "region": "GUF", "chef_lieu": "Cayenne", "lat": 4.9333, "lon": -52.3333},
    "974": {"name": "La Réunion", "region": "REU", "chef_lieu": "Saint-Denis", "lat": -20.8823, "lon": 55.4504},
    "976": {"name": "Mayotte", "region": "MAY", "chef_lieu": "Mamoudzou", "lat": -12.7806, "lon": 45.2278},
}

# Major cities with coordinates (most populated cities in France)
MAJOR_CITIES_FRANCE = {
    "Paris": {"department": "75", "lat": 48.8566, "lon": 2.3522},
    "Marseille": {"department": "13", "lat": 43.2965, "lon": 5.3698},
    "Lyon": {"department": "69", "lat": 45.7640, "lon": 4.8357},
    "Toulouse": {"department": "31", "lat": 43.6047, "lon": 1.4442},
    "Nice": {"department": "06", "lat": 43.7102, "lon": 7.2620},
    "Nantes": {"department": "44", "lat": 47.2184, "lon": -1.5536},
    "Strasbourg": {"department": "67", "lat": 48.5734, "lon": 7.7521},
    "Montpellier": {"department": "34", "lat": 43.6108, "lon": 3.8767},
    "Bordeaux": {"department": "33", "lat": 44.8378, "lon": -0.5792},
    "Lille": {"department": "59", "lat": 50.6292, "lon": 3.0573},
    "Rennes": {"department": "35", "lat": 48.1173, "lon": -1.6778},
    "Reims": {"department": "51", "lat": 49.2583, "lon": 4.0317},
    "Le Havre": {"department": "76", "lat": 49.4944, "lon": 0.1079},
    "Saint-Étienne": {"department": "42", "lat": 45.4397, "lon": 4.3872},
    "Toulon": {"department": "83", "lat": 43.1242, "lon": 5.9280},
    "Grenoble": {"department": "38", "lat": 45.1885, "lon": 5.7245},
    "Dijon": {"department": "21", "lat": 47.3220, "lon": 5.0415},
    "Angers": {"department": "49", "lat": 47.4784, "lon": -0.5632},
    "Nîmes": {"department": "30", "lat": 43.8367, "lon": 4.3601},
    "Villeurbanne": {"department": "69", "lat": 45.7667, "lon": 4.8833},
    "Aix-en-Provence": {"department": "13", "lat": 43.5297, "lon": 5.4474},
    "Le Mans": {"department": "72", "lat": 48.0061, "lon": 0.1996},
    "Clermont-Ferrand": {"department": "63", "lat": 45.7772, "lon": 3.0870},
    "Brest": {"department": "29", "lat": 48.3904, "lon": -4.4861},
    "Tours": {"department": "37", "lat": 47.3941, "lon": 0.6848},
    "Amiens": {"department": "80", "lat": 49.8942, "lon": 2.2958},
    "Limoges": {"department": "87", "lat": 45.8336, "lon": 1.2611},
    "Annecy": {"department": "74", "lat": 45.8992, "lon": 6.1294},
    "Perpignan": {"department": "66", "lat": 42.6987, "lon": 2.8956},
    "Besançon": {"department": "25", "lat": 47.2378, "lon": 6.0241},
    "Orléans": {"department": "45", "lat": 47.9029, "lon": 1.9093},
    "Metz": {"department": "57", "lat": 49.1193, "lon": 6.1757},
    "Rouen": {"department": "76", "lat": 49.4432, "lon": 1.0999},
    "Mulhouse": {"department": "68", "lat": 47.7508, "lon": 7.3359},
    "Caen": {"department": "14", "lat": 49.1829, "lon": -0.3707},
    "Nancy": {"department": "54", "lat": 48.6921, "lon": 6.1844},
    "Avignon": {"department": "84", "lat": 43.9493, "lon": 4.8055},
    "Cannes": {"department": "06", "lat": 43.5528, "lon": 7.0174},
    "Antibes": {"department": "06", "lat": 43.5808, "lon": 7.1239},
    "La Rochelle": {"department": "17", "lat": 46.1603, "lon": -1.1511},
    "Pau": {"department": "64", "lat": 43.2951, "lon": -0.3708},
    "Versailles": {"department": "78", "lat": 48.8014, "lon": 2.1301},
    "Boulogne-Billancourt": {"department": "92", "lat": 48.8352, "lon": 2.2410},
    "Saint-Denis": {"department": "93", "lat": 48.9362, "lon": 2.3574},
    "Argenteuil": {"department": "95", "lat": 48.9472, "lon": 2.2467},
    "Montreuil": {"department": "93", "lat": 48.8638, "lon": 2.4483},
    "Roubaix": {"department": "59", "lat": 50.6942, "lon": 3.1746},
    "Tourcoing": {"department": "59", "lat": 50.7239, "lon": 3.1612},
    "Dunkerque": {"department": "59", "lat": 51.0343, "lon": 2.3768},
    "Nanterre": {"department": "92", "lat": 48.8924, "lon": 2.2071},
    "Créteil": {"department": "94", "lat": 48.7833, "lon": 2.4667},
    "Poitiers": {"department": "86", "lat": 46.5802, "lon": 0.3404},
    "Courbevoie": {"department": "92", "lat": 48.8967, "lon": 2.2567},
    "Vitry-sur-Seine": {"department": "94", "lat": 48.7872, "lon": 2.3927},
    "Colombes": {"department": "92", "lat": 48.9228, "lon": 2.2528},
    "Asnières-sur-Seine": {"department": "92", "lat": 48.9117, "lon": 2.2850},
    "Aulnay-sous-Bois": {"department": "93", "lat": 48.9386, "lon": 2.4908},
    "Rueil-Malmaison": {"department": "92", "lat": 48.8769, "lon": 2.1894},
    "Aubervilliers": {"department": "93", "lat": 48.9136, "lon": 2.3828},
    "Champigny-sur-Marne": {"department": "94", "lat": 48.8172, "lon": 2.5156},
    "Saint-Maur-des-Fossés": {"department": "94", "lat": 48.8000, "lon": 2.4833},
    "Drancy": {"department": "93", "lat": 48.9300, "lon": 2.4500},
    "Issy-les-Moulineaux": {"department": "92", "lat": 48.8244, "lon": 2.2700},
    "Levallois-Perret": {"department": "92", "lat": 48.8933, "lon": 2.2875},
    "Noisy-le-Grand": {"department": "93", "lat": 48.8489, "lon": 2.5528},
    "Cergy": {"department": "95", "lat": 49.0361, "lon": 2.0631},
    "Évry-Courcouronnes": {"department": "91", "lat": 48.6249, "lon": 2.4503},
    "Melun": {"department": "77", "lat": 48.5392, "lon": 2.6597},
}

import httpx
import unicodedata

# Helper to normalize accented strings for matching
def _normalize(text: str) -> str:
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().strip()

def get_department_for_city(city_name: str) -> dict | None:
    """Find department info for a city using local DB first, then French government API"""
    city_normalized = city_name.strip().title()
    
    # Check in major cities first (fast local lookup)
    if city_normalized in MAJOR_CITIES_FRANCE:
        city_info = MAJOR_CITIES_FRANCE[city_normalized]
        dept_code = city_info["department"]
        dept_info = DEPARTMENTS_FRANCE.get(dept_code)
        if dept_info:
            region_code = dept_info["region"]
            region_info = REGIONS_FRANCE.get(region_code)
            return {
                "city": city_normalized,
                "department_code": dept_code,
                "department_name": dept_info["name"],
                "region_code": region_code,
                "region_name": region_info["name"] if region_info else None,
                "lat": city_info["lat"],
                "lon": city_info["lon"]
            }
    
    # Check if it's a department chef-lieu
    for dept_code, dept_info in DEPARTMENTS_FRANCE.items():
        if _normalize(dept_info["chef_lieu"]) == _normalize(city_name):
            region_code = dept_info["region"]
            region_info = REGIONS_FRANCE.get(region_code)
            return {
                "city": dept_info["chef_lieu"],
                "department_code": dept_code,
                "department_name": dept_info["name"],
                "region_code": region_code,
                "region_name": region_info["name"] if region_info else None,
                "lat": dept_info["lat"],
                "lon": dept_info["lon"]
            }
    
    # Fallback: use French government API (covers ALL 36,000+ communes)
    try:
        response = httpx.get(
            "https://geo.api.gouv.fr/communes",
            params={"nom": city_name, "fields": "nom,code,codeDepartement,codeRegion,centre,population", "boost": "population", "limit": 5},
            timeout=5.0
        )
        if response.status_code == 200:
            results = response.json()
            if results:
                commune = results[0]
                dept_code = commune.get("codeDepartement", "")
                dept_info = DEPARTMENTS_FRANCE.get(dept_code)
                if dept_info:
                    region_code = dept_info["region"]
                    region_info = REGIONS_FRANCE.get(region_code)
                    centre = commune.get("centre", {}).get("coordinates", [0, 0])
                    return {
                        "city": commune.get("nom", city_name),
                        "department_code": dept_code,
                        "department_name": dept_info["name"],
                        "region_code": region_code,
                        "region_name": region_info["name"] if region_info else None,
                        "lat": centre[1] if len(centre) > 1 else dept_info["lat"],
                        "lon": centre[0] if len(centre) > 0 else dept_info["lon"]
                    }
    except Exception:
        pass
    
    return None

def get_all_regions() -> list:
    """Get all French regions"""
    return [{"code": code, "name": info["name"]} for code, info in REGIONS_FRANCE.items()]

def get_all_departments() -> list:
    """Get all French departments with their regions"""
    result = []
    for code, info in DEPARTMENTS_FRANCE.items():
        region_info = REGIONS_FRANCE.get(info["region"], {})
        result.append({
            "code": code,
            "name": info["name"],
            "region_code": info["region"],
            "region_name": region_info.get("name", ""),
            "lat": info["lat"],
            "lon": info["lon"]
        })
    return sorted(result, key=lambda x: x["name"])

def get_departments_by_region(region_code: str) -> list:
    """Get all departments in a region"""
    region = REGIONS_FRANCE.get(region_code)
    if not region:
        return []
    
    return [
        {
            "code": dept_code,
            "name": DEPARTMENTS_FRANCE[dept_code]["name"],
            "lat": DEPARTMENTS_FRANCE[dept_code]["lat"],
            "lon": DEPARTMENTS_FRANCE[dept_code]["lon"]
        }
        for dept_code in region["departments"]
        if dept_code in DEPARTMENTS_FRANCE
    ]

def find_region_by_name(name: str) -> dict | None:
    """Find a region by its name (case-insensitive, accent-insensitive)"""
    name_norm = _normalize(name)
    for code, info in REGIONS_FRANCE.items():
        if _normalize(info["name"]) == name_norm:
            return {"code": code, "name": info["name"]}
    # Partial match
    for code, info in REGIONS_FRANCE.items():
        if name_norm in _normalize(info["name"]) or _normalize(info["name"]) in name_norm:
            return {"code": code, "name": info["name"]}
    return None

def find_department_by_name(name: str) -> dict | None:
    """Find a department by its name (case-insensitive, accent-insensitive)"""
    name_norm = _normalize(name)
    for code, info in DEPARTMENTS_FRANCE.items():
        if _normalize(info["name"]) == name_norm:
            region_info = REGIONS_FRANCE.get(info["region"], {})
            return {
                "code": code,
                "name": info["name"],
                "region_code": info["region"],
                "region_name": region_info.get("name", "")
            }
    # Partial match
    for code, info in DEPARTMENTS_FRANCE.items():
        if name_norm in _normalize(info["name"]) or _normalize(info["name"]) in name_norm:
            region_info = REGIONS_FRANCE.get(info["region"], {})
            return {
                "code": code,
                "name": info["name"],
                "region_code": info["region"],
                "region_name": region_info.get("name", "")
            }
    return None
