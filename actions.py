import time

def delete_comment(comment_id):
    """Simuliert das Löschen eines Kommentars."""
    print(f"🗑️ Kommentar {comment_id} wurde gelöscht!")

def like_comment(comment_id):
    """Simuliert das Liken eines Kommentars mit Verzögerung."""
    time.sleep(2)  # 2 Sekunden Verzögerung (optional)
    print(f"❤️ Kommentar {comment_id} wurde geliked!")
