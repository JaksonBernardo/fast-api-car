"""
Car CRUD operation tests.
Tests for car creation, reading, updating, and deletion via API endpoints.
"""
from http import HTTPStatus
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from car_api.models import Car, Brand, User
from car_api.models.cars import FuelType, TransmissionType


class TestCreateCar:
    """Tests for POST /api/cars/"""

    def test_create_car_success(self, client: TestClient, auth_headers: dict, car_data: dict):
        """Test creating a new car successfully."""
        response = client.post('/api/cars/', json=car_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()

        assert data['model'] == car_data['model']
        assert data['plate'] == car_data['plate']
        assert data['fuel_type'] == car_data['fuel_type']
        assert data['transmission'] == car_data['transmission']
        assert data['is_available'] == car_data['is_available']
        assert 'id' in data
        assert 'brand' in data
        assert 'owner' in data

    def test_create_car_without_auth(self, client: TestClient, car_data: dict):
        """Test creating a car without authentication fails."""
        response = client.post('/api/cars/', json=car_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_car_invalid_token(self, client: TestClient, car_data: dict):
        """Test creating a car with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_xyz"}

        response = client.post('/api/cars/', json=car_data, headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_car_duplicate_plate(self, client: TestClient, auth_headers: dict, car: Car):
        """Test creating a car with duplicate plate fails."""
        duplicate_car = {
            'model': 'Different Model',
            'factory_year': 2022,
            'model_year': 2023,
            'color': 'Blue',
            'plate': car.plate,  # Same plate
            'fuel_type': FuelType.DIESEL.value,
            'transmission': TransmissionType.MANUAL.value,
            'price': Decimal('60000.00'),
            'description': 'Duplicate plate test',
            'is_available': True,
            'brand_id': car.brand_id,
            'owner_id': car.owner_id
        }

        response = client.post('/api/cars/', json=duplicate_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.CONFLICT
        data = response.json()
        assert data['detail'] == 'Esta placa já está inserida no sistema'

    def test_create_car_invalid_brand_id(self, client: TestClient, auth_headers: dict, car_data: dict):
        """Test creating a car with non-existent brand fails."""
        invalid_car = {**car_data, 'brand_id': 99999}

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND
        data = response.json()
        assert data['detail'] == 'Marca de carro não encontrada'

    def test_create_car_invalid_owner_id(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand):
        """Test creating a car with non-existent owner fails."""
        invalid_car = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': 99999
        }

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND
        data = response.json()
        assert data['detail'] == 'Proprietário não encontrado'

    def test_create_car_empty_model(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car with empty model fails."""
        invalid_car = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': user.id,
            'model': ''
        }

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_car_short_model(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car with model less than 2 characters fails."""
        invalid_car = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': user.id,
            'model': 'A'  # Less than 2 characters
        }

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_car_invalid_plate_length(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car with invalid plate length fails."""
        invalid_car = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': user.id,
            'plate': 'ABC123'  # Less than 7 characters
        }

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_car_invalid_year(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car with invalid year fails."""
        invalid_car = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': user.id,
            'factory_year': 1800  # Before 1900
        }

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_car_future_year(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car with future year fails."""
        invalid_car = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': user.id,
            'factory_year': 2031  # After 2030
        }

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_car_zero_price(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car with zero price fails."""
        invalid_car = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': user.id,
            'price': Decimal('0.00')
        }

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_car_negative_price(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car with negative price fails."""
        invalid_car = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': user.id,
            'price': Decimal('-100.00')
        }

        response = client.post('/api/cars/', json=invalid_car, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_car_without_description(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car without description succeeds (optional field)."""
        car_without_desc = {
            'model': 'No Description Car',
            'factory_year': 2022,
            'model_year': 2023,
            'color': 'White',
            'plate': 'NODESC1',
            'fuel_type': FuelType.GASOLINE.value,
            'transmission': TransmissionType.MANUAL.value,
            'price': Decimal('50000.00'),
            'is_available': True,
            'brand_id': brand.id,
            'owner_id': user.id
        }

        response = client.post('/api/cars/', json=car_without_desc, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['description'] is None

    def test_create_car_unavailable(self, client: TestClient, auth_headers: dict, car_data: dict, brand: Brand, user: User):
        """Test creating a car as unavailable."""
        car_data_unavailable = {
            **car_data,
            'brand_id': brand.id,
            'owner_id': user.id,
            'is_available': False
        }

        response = client.post('/api/cars/', json=car_data_unavailable, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['is_available'] is False


class TestGetCars:
    """Tests for GET /api/cars/"""

    def test_get_cars_success(self, client: TestClient, car: Car, second_car: Car):
        """Test listing cars successfully."""
        response = client.get('/api/cars/')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert 'cars' in data
        assert 'offset' in data
        assert 'limit' in data
        assert len(data['cars']) >= 2

    def test_get_cars_with_pagination(self, client: TestClient, car: Car, second_car: Car):
        """Test listing cars with pagination."""
        response = client.get('/api/cars/?offset=0&limit=1')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['cars']) == 1
        assert data['offset'] == 0
        assert data['limit'] == 1

    def test_get_cars_with_search_model(self, client: TestClient, car: Car):
        """Test listing cars with search by model."""
        response = client.get(f'/api/cars/?search={car.model}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['cars']) >= 1
        assert data['cars'][0]['model'] == car.model

    def test_get_cars_with_search_plate(self, client: TestClient, car: Car):
        """Test listing cars with search by plate."""
        response = client.get(f'/api/cars/?search={car.plate}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['cars']) >= 1
        assert data['cars'][0]['plate'] == car.plate

    def test_get_cars_with_search_no_results(self, client: TestClient):
        """Test listing cars with search that returns no results."""
        response = client.get('/api/cars/?search=nonexistent_car_xyz')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['cars']) == 0

    def test_get_cars_filter_by_brand_id(self, client: TestClient, car: Car, second_car: Car, brand: Brand):
        """Test listing cars filtered by brand ID."""
        response = client.get(f'/api/cars/?brand_id={brand.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['cars']) >= 1
        for c in data['cars']:
            assert c['brand_id'] == brand.id

    def test_get_cars_filter_by_owner_id(self, client: TestClient, car: Car, user: User):
        """Test listing cars filtered by owner ID."""
        response = client.get(f'/api/cars/?owner_id={user.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['cars']) >= 1
        for c in data['cars']:
            assert c['owner_id'] == user.id

    def test_get_cars_filter_by_fuel_type(self, client: TestClient, car: Car):
        """Test listing cars filtered by fuel type."""
        response = client.get(f'/api/cars/?fuel_type={car.fuel_type}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['cars']) >= 1
        for c in data['cars']:
            assert c['fuel_type'] == car.fuel_type

    def test_get_cars_filter_by_transmission(self, client: TestClient, car: Car):
        """Test listing cars filtered by transmission."""
        response = client.get(f'/api/cars/?transmission={car.transmission}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['cars']) >= 1
        for c in data['cars']:
            assert c['transmission'] == car.transmission

    def test_get_cars_invalid_limit(self, client: TestClient):
        """Test listing cars with invalid limit fails."""
        response = client.get('/api/cars/?limit=0')

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_cars_invalid_offset(self, client: TestClient):
        """Test listing cars with negative offset fails."""
        response = client.get('/api/cars/?offset=-1')

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_cars_limit_exceeds_max(self, client: TestClient):
        """Test listing cars with limit exceeding maximum fails."""
        response = client.get('/api/cars/?limit=101')

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestGetCarById:
    """Tests for GET /api/cars/{car_id}"""

    def test_get_car_by_id_success(self, client: TestClient, auth_headers: dict, car: Car):
        """Test getting a car by ID successfully."""
        response = client.get(f'/api/cars/{car.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['id'] == car.id
        assert data['model'] == car.model
        assert data['plate'] == car.plate
        assert 'brand' in data
        assert 'owner' in data

    def test_get_car_by_id_without_auth(self, client: TestClient, car: Car):
        """Test getting a car by ID without authentication fails."""
        response = client.get(f'/api/cars/{car.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_car_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting a non-existent car returns 404."""
        response = client.get('/api/cars/99999', headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND
        data = response.json()
        assert data['detail'] == 'Carro não encontrado'

    def test_get_car_by_id_invalid_id(self, client: TestClient, auth_headers: dict):
        """Test getting a car with invalid ID format fails."""
        response = client.get('/api/cars/invalid', headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_car_by_id_different_owner(self, client: TestClient, auth_headers: dict, car: Car, second_user: User, user_data: dict):
        """Test getting a car owned by different user."""
        # User can view cars they don't own (based on current implementation)
        response = client.get(f'/api/cars/{car.id}', headers=auth_headers)

        # Should succeed - users can view all cars
        assert response.status_code == HTTPStatus.OK


class TestUpdateCar:
    """Tests for PUT /api/cars/{car_id}"""

    def test_update_car_success(self, client: TestClient, auth_headers: dict, car: Car):
        """Test updating a car successfully."""
        update_data = {
            'model': 'Updated Model',
            'color': 'Updated Color',
            'price': Decimal('200000.00')
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['model'] == 'Updated Model'
        assert data['color'] == 'Updated Color'
        assert Decimal(data['price']) == Decimal('200000.00')

    def test_update_car_without_auth(self, client: TestClient, car: Car):
        """Test updating a car without authentication fails."""
        update_data = {
            'model': 'Updated Model'
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_car_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating a non-existent car returns 404."""
        update_data = {
            'model': 'Updated Model'
        }

        response = client.put('/api/cars/99999', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_car_duplicate_plate(self, client: TestClient, auth_headers: dict, car: Car, second_car: Car):
        """Test updating a car with another car's plate fails."""
        update_data = {
            'plate': second_car.plate  # Use second car's plate
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CONFLICT
        data = response.json()
        assert data['detail'] == 'Placa do veículo já existente'

    def test_update_car_zero_price(self, client: TestClient, auth_headers: dict, car: Car):
        """Test updating a car with zero price fails."""
        update_data = {
            'price': Decimal('0.00')
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CONFLICT
        data = response.json()
        assert data['detail'] == 'Preço do veículo tem que ser maior que zero'

    def test_update_car_empty_model(self, client: TestClient, auth_headers: dict, car: Car):
        """Test updating a car with empty model fails."""
        update_data = {
            'model': ''
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CONFLICT
        data = response.json()
        assert data['detail'] == 'Modelo do veículo inválido'

    def test_update_car_invalid_brand(self, client: TestClient, auth_headers: dict, car: Car):
        """Test updating a car with non-existent brand fails."""
        update_data = {
            'brand_id': 99999
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CONFLICT
        data = response.json()
        assert data['detail'] == 'Marca/Brand não encontrada'

    def test_update_car_invalid_owner(self, client: TestClient, auth_headers: dict, car: Car):
        """Test updating a car with non-existent owner fails."""
        update_data = {
            'owner_id': 99999
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CONFLICT
        data = response.json()
        assert data['detail'] == 'Proprietário do veículo não encontrado'

    def test_update_car_partial_update(self, client: TestClient, auth_headers: dict, car: Car):
        """Test partial update of car."""
        update_data = {
            'color': 'New Color'
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['color'] == 'New Color'
        assert data['model'] == car.model  # Should remain unchanged

    def test_update_car_availability(self, client: TestClient, auth_headers: dict, car: Car):
        """Test updating car availability."""
        update_data = {
            'is_available': False
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['is_available'] is False


class TestDeleteCar:
    """Tests for DELETE /api/cars/{car_id}"""

    def test_delete_car_success(self, client: TestClient, auth_headers: dict, car: Car):
        """Test deleting a car successfully."""
        response = client.delete(f'/api/cars/{car.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verify car is deleted
        get_response = client.get(f'/api/cars/{car.id}', headers=auth_headers)
        assert get_response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_car_without_auth(self, client: TestClient, car: Car):
        """Test deleting a car without authentication fails."""
        response = client.delete(f'/api/cars/{car.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_car_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting a non-existent car returns 404."""
        response = client.delete('/api/cars/99999', headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND


class TestCarOwnership:
    """Tests for car ownership verification."""

    def test_get_car_owner_permission(self, client: TestClient, auth_headers: dict, car: Car):
        """Test that owner can access their own car."""
        response = client.get(f'/api/cars/{car.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK

    def test_update_car_owner_permission(self, client: TestClient, auth_headers: dict, car: Car):
        """Test that owner can update their own car."""
        update_data = {
            'model': 'Owner Updated Model'
        }

        response = client.put(f'/api/cars/{car.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK

    def test_delete_car_owner_permission(self, client: TestClient, auth_headers: dict, car: Car):
        """Test that owner can delete their own car."""
        response = client.delete(f'/api/cars/{car.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.NO_CONTENT


class TestCarSchemaValidation:
    """Tests for car schema validation."""

    def test_car_schema_all_fuel_types(self, client: TestClient, auth_headers: dict, brand: Brand, user: User):
        """Test creating cars with all fuel types."""
        for fuel_type in FuelType:
            car_data = {
                'model': f'Test {fuel_type.value}',
                'factory_year': 2022,
                'model_year': 2023,
                'color': 'Black',
                'plate': f'FUEL{fuel_type.value[:3].upper()}1',
                'fuel_type': fuel_type.value,
                'transmission': TransmissionType.MANUAL.value,
                'price': Decimal('50000.00'),
                'brand_id': brand.id,
                'owner_id': user.id
            }

            response = client.post('/api/cars/', json=car_data, headers=auth_headers)

            assert response.status_code == HTTPStatus.CREATED, f"Failed for fuel type: {fuel_type.value}"

    def test_car_schema_all_transmission_types(self, client: TestClient, auth_headers: dict, brand: Brand, user: User):
        """Test creating cars with all transmission types."""
        for transmission in TransmissionType:
            car_data = {
                'model': f'Test {transmission.value}',
                'factory_year': 2022,
                'model_year': 2023,
                'color': 'White',
                'plate': f'TRANS{transmission.value[:3].upper()}1',
                'fuel_type': FuelType.GASOLINE.value,
                'transmission': transmission.value,
                'price': Decimal('50000.00'),
                'brand_id': brand.id,
                'owner_id': user.id
            }

            response = client.post('/api/cars/', json=car_data, headers=auth_headers)

            assert response.status_code == HTTPStatus.CREATED, f"Failed for transmission: {transmission.value}"

    def test_car_schema_plate_uppercase_conversion(self, client: TestClient, auth_headers: dict, brand: Brand, user: User):
        """Test that plate is converted to uppercase."""
        car_data = {
            'model': 'Lowercase Plate Car',
            'factory_year': 2022,
            'model_year': 2023,
            'color': 'Silver',
            'plate': 'abc1234',  # Lowercase
            'fuel_type': FuelType.GASOLINE.value,
            'transmission': TransmissionType.MANUAL.value,
            'price': Decimal('50000.00'),
            'brand_id': brand.id,
            'owner_id': user.id
        }

        response = client.post('/api/cars/', json=car_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['plate'] == 'ABC1234'  # Should be uppercase

    def test_car_schema_mercosul_plate(self, client: TestClient, auth_headers: dict, brand: Brand, user: User):
        """Test creating a car with Mercosul plate format."""
        car_data = {
            'model': 'Mercosul Car',
            'factory_year': 2022,
            'model_year': 2023,
            'color': 'Gray',
            'plate': 'ABC1D23',  # Mercosul format
            'fuel_type': FuelType.FLEX.value,
            'transmission': TransmissionType.AUTOMATIC.value,
            'price': Decimal('75000.00'),
            'brand_id': brand.id,
            'owner_id': user.id
        }

        response = client.post('/api/cars/', json=car_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED

    def test_car_schema_long_description(self, client: TestClient, auth_headers: dict, brand: Brand, user: User):
        """Test creating a car with long description."""
        car_data = {
            'model': 'Long Description Car',
            'factory_year': 2022,
            'model_year': 2023,
            'color': 'Blue',
            'plate': 'LONGDESC1',
            'fuel_type': FuelType.GASOLINE.value,
            'transmission': TransmissionType.MANUAL.value,
            'price': Decimal('50000.00'),
            'description': 'A' * 1000,  # 1000 characters
            'brand_id': brand.id,
            'owner_id': user.id
        }

        response = client.post('/api/cars/', json=car_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
