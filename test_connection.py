"""
Script de test de connexion Supabase et insertion du premier ping.
Ce script valide que l'infrastructure de base fonctionne correctement.
"""

from datetime import datetime, timezone
from supabase_client import SupabaseClient

def test_connection_and_ping():
    """Teste la connexion et insère un ping dans system_pings"""
    
    print("🔌 Test de connexion à Supabase...")
    
    try:
        # Initialiser le client
        supabase_client = SupabaseClient()
        
        # Tester la connexion
        if supabase_client.test_connection():
            print("✅ Connexion réussie à Supabase!")
        else:
            print("❌ Échec de la connexion")
            return False
        
        # Insérer un ping de test
        print("\n📤 Insertion du premier ping dans system_pings...")
        
        ping_data = {
            "ping_time": datetime.now(timezone.utc).isoformat(),
            "status": "SUCCESS"
        }
        
        response = supabase_client.table("system_pings").insert(ping_data)
        
        # Vérifier si l'insertion a réussi (status 201)
        if response.data:
            print(f"✅ Ping inséré avec succès!")
            print(f"   Timestamp: {ping_data['ping_time']}")
            print(f"   Status: {ping_data['status']}")
            return True
        else:
            print("❌ Échec de l'insertion du ping")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DE CONNEXION SUPABASE - SPRINT 1")
    print("=" * 60)
    
    success = test_connection_and_ping()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCÈS! L'infrastructure est opérationnelle.")
        print("   Tu peux maintenant passer au Sprint 2 (DevOps Keep-Alive)")
    else:
        print("⚠️  ÉCHEC. Vérifie tes credentials et ta connexion internet.")
    print("=" * 60)
