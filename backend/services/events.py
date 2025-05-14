import json


def parse_location(location_data):
    """Парсит location из JSON строки или словаря в словарь Python"""
    if isinstance(location_data, str):
        try:
            return json.loads(location_data)
        except json.JSONDecodeError:
            return {}
    return location_data or {}


def format_location_string(location_dict):
    """Форматирует словарь с локацией в читаемую строку"""
    parts = [
        location_dict.get('country'),
        location_dict.get('city'),
        location_dict.get('street'),
        location_dict.get('house'),
        location_dict.get('flat')
    ]
    # Фильтруем None и пустые строки, объединяем через запятую
    return f"{location_dict.get('country')}, \
г.{location_dict.get('city')}, ул.{location_dict.get('street')}, \
д.{location_dict.get('house')}, кв.{location_dict.get('flat')}"


def prepare_event_data(event):
    """Подготавливает данные события для передачи в шаблон"""
    location_dict = parse_location(event.location)
    location_str = format_location_string(location_dict)
    print(f"{location_str}")
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "location": location_str,
        "date": event.date,
        "time": event.time,
        "max_participants": event.max_participants,
        "price": event.price,
        "image": event.image,
        "created_at": event.created_at,
        "organizer_id": event.organizer_id
    }