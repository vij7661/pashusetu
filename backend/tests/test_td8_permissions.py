from app.core.permissions import role_has_permission

def test_farmer_cannot_operate_scale():
    assert role_has_permission("FARMER","operator:weigh") is False

def test_operator_can_weigh():
    assert role_has_permission("OPERATOR","operator:weigh") is True

def test_admin_has_all_permissions():
    assert role_has_permission("ADMIN","anything:anywhere") is True
