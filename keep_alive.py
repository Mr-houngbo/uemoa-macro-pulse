"""
Script de maintenance automatique (Keep-Alive).
Exécuté périodiquement par GitHub Actions pour éviter la mise en veille de Supabase.
"""
from datetime import datetime, timezone
from supabase_client import SupabaseClient

def run_maintenance_ping():
    print(f"⏰ Démarrage du Ping de maintenance : {datetime.now(timezone.utc)}")
    try:
        supabase_client = SupabaseClient()
        
        ping_data = {
            "ping_time": datetime.now(timezone.utc).isoformat(),
            "status": "AUTOPILOT"
        }
        
        # On insère le ping avec le statut AUTOPILOT pour le différencier des tests manuels
        response = supabase_client.table("system_pings").insert(ping_data)
        
        if response.data:
            print(f"✅ [KEEPALIVE SUCCESS] Ping enregistré avec statut AUTOPILOT")
            print(f"   Timestamp: {ping_data['ping_time']}")
            return True
        else:
            print("❌ [KEEPALIVE FAILED] Aucune donnée retournée.")
            return False
            
    except Exception as e:
        print(f"❌ [CRITICAL ERROR] Échec de la maintenance : {e}")
        return False

if __name__ == "__main__":
    success = run_maintenance_ping()
    exit(0 if success else 1)
