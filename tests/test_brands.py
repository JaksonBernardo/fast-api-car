"""
Brand CRUD operation tests.
Tests for brand creation, reading, updating, and deletion via API endpoints.
"""
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from car_api.models import Brand, User


class TestCreateBrand:
    """Tests for POST /api/brands/"""

    def test_create_brand_success(self, client: TestClient, auth_headers: dict, brand_data: dict):
        """Test creating a new brand successfully."""
        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()

        assert data['name'] == brand_data['name']
        assert data['description'] == brand_data['description']
        assert data['is_active'] == brand_data['is_active']
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_create_brand_without_auth(self, client: TestClient, brand_data: dict):
        """Test creating a brand without authentication fails."""
        response = client.post('/api/brands/', json=brand_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_brand_invalid_token(self, client: TestClient, brand_data: dict):
        """Test creating a brand with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_xyz"}

        response = client.post('/api/brands/', json=brand_data, headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_brand_duplicate_name(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test creating a brand with duplicate name fails."""
        duplicate_brand = {
            'name': brand.name,
            'description': 'Different description',
            'is_active': True
        }

        response = client.post('/api/brands/', json=duplicate_brand, headers=auth_headers)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.json()
        assert data['detail'] == 'Brand já existe'

    def test_create_brand_empty_name(self, client: TestClient, auth_headers: dict):
        """Test creating a brand with empty name fails."""
        invalid_brand = {
            'name': '',
            'description': 'Test description',
            'is_active': True
        }

        response = client.post('/api/brands/', json=invalid_brand, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_brand_short_name(self, client: TestClient, auth_headers: dict):
        """Test creating a brand with name less than 2 characters fails."""
        invalid_brand = {
            'name': 'A',  # Less than 2 characters
            'description': 'Test description',
            'is_active': True
        }

        response = client.post('/api/brands/', json=invalid_brand, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_brand_without_description(self, client: TestClient, auth_headers: dict):
        """Test creating a brand without description succeeds (optional field)."""
        brand_data = {
            'name': 'No Description Brand',
            'is_active': True
        }

        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['name'] == 'No Description Brand'
        assert data['description'] is None

    def test_create_brand_inactive(self, client: TestClient, auth_headers: dict):
        """Test creating an inactive brand."""
        brand_data = {
            'name': 'Inactive Brand',
            'description': 'Initially inactive',
            'is_active': False
        }

        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['is_active'] is False

    def test_create_brand_whitespace_name(self, client: TestClient, auth_headers: dict):
        """Test creating a brand with whitespace-only name fails."""
        invalid_brand = {
            'name': '   ',  # Whitespace only
            'description': 'Test description',
            'is_active': True
        }

        response = client.post('/api/brands/', json=invalid_brand, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_brand_long_name(self, client: TestClient, auth_headers: dict):
        """Test creating a brand with long name."""
        brand_data = {
            'name': 'A' * 100,  # 100 characters
            'description': 'Long name brand',
            'is_active': True
        }

        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED


class TestGetBrands:
    """Tests for GET /api/brands/"""

    def test_get_brands_success(self, client: TestClient, auth_headers: dict, brand: Brand, second_brand: Brand):
        """Test listing brands successfully."""
        response = client.get('/api/brands/', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert 'brands' in data
        assert 'offset' in data
        assert 'limit' in data
        assert len(data['brands']) >= 2

    def test_get_brands_without_auth(self, client: TestClient):
        """Test listing brands without authentication fails."""
        response = client.get('/api/brands/')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_brands_with_pagination(self, client: TestClient, auth_headers: dict, brand: Brand, second_brand: Brand):
        """Test listing brands with pagination."""
        response = client.get('/api/brands/?offset=0&limit=1', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['brands']) == 1
        assert data['offset'] == 0
        assert data['limit'] == 1

    def test_get_brands_with_search_name(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test listing brands with search by name."""
        response = client.get(f'/api/brands/?search={brand.name}', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['brands']) >= 1
        assert data['brands'][0]['name'] == brand.name

    def test_get_brands_with_search_description(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test listing brands with search by description."""
        response = client.get(f'/api/brands/?search={brand.description}', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['brands']) >= 1

    def test_get_brands_with_search_no_results(self, client: TestClient, auth_headers: dict):
        """Test listing brands with search that returns no results."""
        response = client.get('/api/brands/?search=nonexistent_brand_xyz', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['brands']) == 0

    def test_get_brands_filter_by_active(self, client: TestClient, auth_headers: dict, brand: Brand, inactive_brand: Brand):
        """Test listing brands filtered by active status."""
        response = client.get('/api/brands/?is_active=true', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Should include active brands but not inactive
        assert len(data['brands']) >= 1
        for b in data['brands']:
            assert b['is_active'] is True

    def test_get_brands_filter_by_inactive(self, client: TestClient, auth_headers: dict, brand: Brand, inactive_brand: Brand):
        """Test listing brands filtered by inactive status."""
        response = client.get('/api/brands/?is_active=false', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Should include only inactive brands
        for b in data['brands']:
            assert b['is_active'] is False

    def test_get_brands_invalid_limit(self, client: TestClient, auth_headers: dict):
        """Test listing brands with invalid limit fails."""
        response = client.get('/api/brands/?limit=0', headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_brands_invalid_offset(self, client: TestClient, auth_headers: dict):
        """Test listing brands with negative offset fails."""
        response = client.get('/api/brands/?offset=-1', headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_brands_limit_exceeds_max(self, client: TestClient, auth_headers: dict):
        """Test listing brands with limit exceeding maximum fails."""
        response = client.get('/api/brands/?limit=11', headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestGetBrandById:
    """Tests for GET /api/brands/{brand_id}"""

    def test_get_brand_by_id_success(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test getting a brand by ID successfully."""
        response = client.get(f'/api/brands/{brand.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['id'] == brand.id
        assert data['name'] == brand.name
        assert data['description'] == brand.description
        assert data['is_active'] == brand.is_active

    def test_get_brand_by_id_without_auth(self, client: TestClient, brand: Brand):
        """Test getting a brand by ID without authentication fails."""
        response = client.get(f'/api/brands/{brand.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_brand_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting a non-existent brand returns 404."""
        response = client.get('/api/brands/99999', headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND
        data = response.json()
        assert data['detail'] == 'Essa brand não existe'

    def test_get_brand_by_id_invalid_id(self, client: TestClient, auth_headers: dict):
        """Test getting a brand with invalid ID format fails."""
        response = client.get('/api/brands/invalid', headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestUpdateBrand:
    """Tests for PUT /api/brands/{brand_id}"""

    def test_update_brand_success(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test updating a brand successfully."""
        update_data = {
            'name': 'Updated Brand Name',
            'description': 'Updated description',
            'is_active': False
        }

        response = client.put(f'/api/brands/{brand.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['name'] == 'Updated Brand Name'
        assert data['description'] == 'Updated description'
        assert data['is_active'] is False

    def test_update_brand_without_auth(self, client: TestClient, brand: Brand):
        """Test updating a brand without authentication fails."""
        update_data = {
            'name': 'Updated Brand'
        }

        response = client.put(f'/api/brands/{brand.id}', json=update_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_brand_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating a non-existent brand returns 404."""
        update_data = {
            'name': 'Updated Brand'
        }

        response = client.put('/api/brands/99999', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_brand_duplicate_name(self, client: TestClient, auth_headers: dict, brand: Brand, second_brand: Brand):
        """Test updating a brand with another brand's name fails."""
        update_data = {
            'name': second_brand.name  # Use second brand's name
        }

        response = client.put(f'/api/brands/{brand.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CONFLICT
        data = response.json()
        assert data['detail'] == 'Nome da marca já existente'

    def test_update_brand_partial_update(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test partial update of brand."""
        update_data = {
            'name': 'Partial Update Brand'
        }

        response = client.put(f'/api/brands/{brand.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['name'] == 'Partial Update Brand'
        assert data['description'] == brand.description  # Should remain unchanged

    def test_update_brand_empty_name(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test updating a brand with empty name fails."""
        update_data = {
            'name': ''
        }

        response = client.put(f'/api/brands/{brand.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_update_brand_short_name(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test updating a brand with short name fails."""
        update_data = {
            'name': 'A'  # Less than 2 characters
        }

        response = client.put(f'/api/brands/{brand.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_update_brand_activate(self, client: TestClient, auth_headers: dict, inactive_brand: Brand):
        """Test activating an inactive brand."""
        update_data = {
            'is_active': True
        }

        response = client.put(f'/api/brands/{inactive_brand.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['is_active'] is True

    def test_update_brand_deactivate(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test deactivating an active brand."""
        update_data = {
            'is_active': False
        }

        response = client.put(f'/api/brands/{brand.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['is_active'] is False


class TestDeleteBrand:
    """Tests for DELETE /api/brands/{brand_id}"""

    def test_delete_brand_success(self, client: TestClient, auth_headers: dict, brand: Brand):
        """Test deleting a brand successfully."""
        response = client.delete(f'/api/brands/{brand.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verify brand is deleted
        get_response = client.get(f'/api/brands/{brand.id}', headers=auth_headers)
        assert get_response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_brand_without_auth(self, client: TestClient, brand: Brand):
        """Test deleting a brand without authentication fails."""
        response = client.delete(f'/api/brands/{brand.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_brand_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting a non-existent brand returns 404."""
        response = client.delete('/api/brands/99999', headers=auth_headers)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.json()
        assert data['detail'] == 'Essa brand não existe'

    def test_delete_brand_with_cars_associated(self, client: TestClient, auth_headers: dict, brand: Brand, car):
        """Test deleting a brand with associated cars fails."""
        response = client.delete(f'/api/brands/{brand.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.FORBIDDEN
        data = response.json()
        assert data['detail'] == 'Essa brand tem carros associados, não pode ser deletada'


class TestBrandSchemaValidation:
    """Tests for brand schema validation."""

    def test_brand_schema_name_with_special_chars(self, client: TestClient, auth_headers: dict):
        """Test creating a brand with special characters in name."""
        brand_data = {
            'name': 'Brand & Co.',
            'description': 'Special characters',
            'is_active': True
        }

        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED

    def test_brand_schema_name_with_numbers(self, client: TestClient, auth_headers: dict):
        """Test creating a brand with numbers in name."""
        brand_data = {
            'name': 'Brand 123',
            'description': 'Numbers in name',
            'is_active': True
        }

        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED

    def test_brand_schema_unicode_name(self, client: TestClient, auth_headers: dict):
        """Test creating a brand with unicode characters in name."""
        brand_data = {
            'name': 'Bränd Üñíçödé',
            'description': 'Unicode test',
            'is_active': True
        }

        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED

    def test_brand_schema_long_description(self, client: TestClient, auth_headers: dict):
        """Test creating a brand with long description."""
        brand_data = {
            'name': 'Long Description Brand',
            'description': 'A' * 1000,  # 1000 characters
            'is_active': True
        }

        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
