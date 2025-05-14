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

    # Рассчитываем свободные места
    registrations_count = len(event.registrations) if event.registrations else 0
    free_spots = None
    if event.max_participants is not None:
        free_spots = max(0, event.max_participants - registrations_count)

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "location": location_str,
        "date": event.date,
        "time": event.time,
        "max_participants": event.max_participants,
        "free_spots": free_spots,  # Добавляем количество свободных мест
        "registrations_count": registrations_count,  # Добавляем общее количество регистраций
        "price": event.price,
        "image": event.image,
        "created_at": event.created_at,
        "organizer_id": event.organizer_id
    }