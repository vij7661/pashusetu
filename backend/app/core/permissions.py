from app.core.enums import Role

PERMISSIONS = {
    Role.FARMER.value: {
        "farmer:profile",
        "livestock:write",
        "listing:write",
        "bidding:view",
        "agreement:confirm",
        "transaction:view",
        "dispute:open",
    },
    Role.BUYER.value: {
        "buyer:profile",
        "marketplace:view",
        "bidding:write",
        "agreement:confirm",
        "transaction:view",
        "delivery:verify",
        "dispute:open",
    },
    Role.OPERATOR.value: {
        "operator:weigh",
        "operator:pickup",
        "operator:reweigh",
        "transaction:view",
    },
    Role.ADMIN.value: {
        "*",
    },
}


def role_has_permission(role: str, permission: str) -> bool:
    permissions = PERMISSIONS.get(role, set())
    return "*" in permissions or permission in permissions
