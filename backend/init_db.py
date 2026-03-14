import sqlite3
import pandas as pd
import os

def init_database():
    """
    Initialize the database with sample BMW vehicle inventory data.
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Create connection
    conn = sqlite3.connect('data.db')
    
    # Sample BMW vehicle inventory data
    sample_data = {
        'VehicleID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        'Make': ['BMW'] * 15,
        'Model': ['3 Series', '5 Series', 'X3', 'X5', 'M3', 'X1', 'Z4', 'iX', '7 Series', 'X6', '2 Series', '4 Series', 'i3', 'X2', '8 Series'],
        'Year': [2022, 2021, 2023, 2022, 2023, 2021, 2022, 2023, 2022, 2023, 2021, 2022, 2020, 2023, 2022],
        'FuelType': ['Gasoline', 'Gasoline', 'Hybrid', 'Diesel', 'Gasoline', 'Gasoline', 'Gasoline', 'Electric', 'Gasoline', 'Hybrid', 'Gasoline', 'Gasoline', 'Electric', 'Gasoline', 'Gasoline'],
        'Price': [45000.0, 55000.0, 52000.0, 65000.0, 85000.0, 40000.0, 50000.0, 75000.0, 80000.0, 70000.0, 38000.0, 48000.0, 42000.0