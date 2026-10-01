import time
import pg8000

def db_connection(cfg):
    for _ in range(cfg.RECONNECT_ATTEMPTS):
        try:
            return pg8000.connect(
                user=cfg.DB_USER, password=cfg.DB_PASSWORD,
                host=cfg.IP_ADDRESS, port=cfg.PORT_NUMBER,
                database=cfg.DB_NAME
            )
        except Exception:
            time.sleep(cfg.RECONNECT_INTERVAL)
    return None