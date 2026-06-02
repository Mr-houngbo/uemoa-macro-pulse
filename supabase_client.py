import os
import requests
import urllib3
from dotenv import load_dotenv

# Désactiver les avertissements SSL pour le développement
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Charger les variables d'environnement
load_dotenv()

class SupabaseClient:
    """
    Client Supabase simple utilisant requests (contournement SSL Windows).
    Singleton pattern pour assurer une seule instance.
    """
    _instance = None
    _url = None
    _key = None
    _headers = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        """Initialise le client Supabase avec les credentials du .env"""
        self._url = os.getenv("SUPABASE_URL")
        self._key = os.getenv("SUPABASE_KEY")

        if not self._url or not self._key:
            raise ValueError(
                "Variables d'environnement manquantes. "
                "Vérifiez que SUPABASE_URL et SUPABASE_KEY sont définis dans .env"
            )

        self._headers = {
            "apikey": self._key,
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json"
        }

    def table(self, table_name):
        """Retourne un objet Table pour interagir avec une table spécifique"""
        return Table(self._url, table_name, self._headers)

    def test_connection(self) -> bool:
        """Teste la connexion à Supabase"""
        try:
            response = requests.get(
                f"{self._url}/rest/v1/system_pings?select=id&limit=1",
                headers=self._headers,
                verify=False
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False


class Table:
    """Wrapper simple pour les opérations sur une table Supabase"""
    def __init__(self, base_url, table_name, headers):
        self.base_url = base_url
        self.table_name = table_name
        self.headers = headers

    def select(self, columns="*"):
        """Prépare une requête SELECT"""
        self._select_columns = columns
        return self

    def insert(self, data):
        """Insère des données dans la table"""
        response = requests.post(
            f"{self.base_url}/rest/v1/{self.table_name}?select=*",
            headers=self.headers,
            json=data,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            # Si la réponse est vide, retourner les données insérées (pour compatibilité)
            if not response.text.strip():
                return Response([data])
            return Response(response.json())
        else:
            raise Exception(f"Erreur insert: {response.status_code} - {response.text}")

    def limit(self, n):
        """Ajoute une limite à la requête"""
        self._limit = n
        return self

    def execute(self):
        """Exécute la requête SELECT"""
        url = f"{self.base_url}/rest/v1/{self.table_name}?select={getattr(self, '_select_columns', '*')}"
        if hasattr(self, '_limit'):
            url += f"&limit={self._limit}"
        
        response = requests.get(url, headers=self.headers, verify=False)
        if response.status_code == 200:
            return Response(response.json())
        else:
            raise Exception(f"Erreur select: {response.status_code} - {response.text}")


class Response:
    """Wrapper simple pour les réponses"""
    def __init__(self, data):
        self.data = data
