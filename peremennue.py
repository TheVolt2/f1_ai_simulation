# peremennue.py

TIRE_TYPES = ['Soft', 'Medium', 'Hard', 'Intermediate', 'Wet']
TIRE_WEAR_RATE = {
    'Soft': 8.0,
    'Medium': 6.5,
    'Hard': 2.5,
    'Intermediate': 5.0,
    'Wet': 3.0
}
TIRE_LIFESPAN = {
    'Soft': (100 / 8.0) * 1.5,
    'Medium': (100 / 6.5) * 1.5,
    'Hard': (100 / 2.5) * 1.5,
    'Intermediate': (100 / 5.0) * 1.5,
    'Wet': (100 / 3.0) * 1.5
}
TIRE_MISMATCH_PENALTY = {
    # Сухая трасса
    ('dry', 'Intermediate'): 4.5,
    ('dry', 'Wet'): 25.0,

    # Легкий дождь (оптимально - Intermediate)
    ('light_rain', 'Hard'): 10.0,
    ('light_rain', 'Medium'): 8.0,
    ('light_rain', 'Soft'): 12.0,
    ('light_rain', 'Wet'): 1.5,

    # Средний дождь (оптимально - Wet)
    ('medium_rain', 'Hard'): 15.0,
    ('medium_rain', 'Medium'): 12.0,
    ('medium_rain', 'Soft'): 18.0,
    ('medium_rain', 'Intermediate'): 2.5,

    # Сильный дождь (оптимально - Wet)
    ('heavy_rain', 'Hard'): 20.0,
    ('heavy_rain', 'Medium'): 18.0,
    ('heavy_rain', 'Soft'): 22.0,
    ('heavy_rain', 'Intermediate'): 7.0
}