# Simple in-memory relationship graph for hackathon prototype.
# Later this can be replaced by Neo4j / RedisGraph / a graph database.

entity_links = {
    "device_id": {},
    "ip_address": {},
    "card_fingerprint": {},
    "email_hash": {}
}


def _register_link(link_type, link_value, customer_id):
    """
    Register a customer-to-entity relationship
    and return the number of linked customers.
    """

    if not link_value:
        return 0

    store = entity_links[link_type]

    if link_value not in store:
        store[link_value] = set()

    store[link_value].add(customer_id)

    return len(store[link_value])


def _get_link_count(link_type, link_value):
    """
    Read the current number of linked customers
    without modifying graph state.
    """

    if not link_value:
        return 0

    store = entity_links[link_type]

    if link_value not in store:
        return 0

    return len(store[link_value])


def analyze_graph_risk(
    transaction,
    update_state=True
):
    """
    Detect suspicious relationship sharing across customers.

    update_state=True:
        Register the transaction in the live graph.

    update_state=False:
        Read existing graph relationships without
        modifying graph state. Used for simulations
        and counterfactual analysis.
    """

    graph_score = 0
    graph_signals = []

    customer_id = transaction.customer_id

    # Update live graph for real transactions
    if update_state:

        device_count = _register_link(
            "device_id",
            transaction.device_id,
            customer_id
        )

        ip_count = _register_link(
            "ip_address",
            transaction.ip_address,
            customer_id
        )

        card_count = _register_link(
            "card_fingerprint",
            transaction.card_fingerprint,
            customer_id
        )

        email_count = _register_link(
            "email_hash",
            transaction.email_hash,
            customer_id
        )

    # Read-only graph access for simulations
    else:

        device_count = _get_link_count(
            "device_id",
            transaction.device_id
        )

        ip_count = _get_link_count(
            "ip_address",
            transaction.ip_address
        )

        card_count = _get_link_count(
            "card_fingerprint",
            transaction.card_fingerprint
        )

        email_count = _get_link_count(
            "email_hash",
            transaction.email_hash
        )

    # Device-sharing risk
    if device_count >= 3:
        graph_score += 30
        graph_signals.append(
            f"Device is shared across {device_count} customer accounts"
        )

    elif device_count == 2:
        graph_score += 15
        graph_signals.append(
            "Device is shared across multiple customer accounts"
        )

    # IP-sharing risk
    if ip_count >= 5:
        graph_score += 25
        graph_signals.append(
            f"IP address is linked to {ip_count} customer accounts"
        )

    elif ip_count >= 3:
        graph_score += 12
        graph_signals.append(
            "IP address is shared across several customer accounts"
        )

    # Card-sharing risk
    if card_count >= 3:
        graph_score += 35
        graph_signals.append(
            f"Card fingerprint is linked to {card_count} customer accounts"
        )

    elif card_count == 2:
        graph_score += 20
        graph_signals.append(
            "Card fingerprint is shared across multiple customer accounts"
        )

    # Email-sharing risk
    if email_count >= 2:
        graph_score += 20
        graph_signals.append(
            "Email identity is linked to multiple customer accounts"
        )

    # Cap graph score
    graph_score = min(graph_score, 100)

    # Graph status
    if graph_score >= 70:
        graph_status = "ABUSE_RING_HIGH"

    elif graph_score >= 35:
        graph_status = "ABUSE_RING_SUSPECTED"

    elif graph_score > 0:
        graph_status = "RELATIONSHIP_ANOMALY"

    else:
        graph_status = "NO_GRAPH_RISK"

    return {
        "graph_risk_score": graph_score,
        "graph_status": graph_status,
        "graph_signals": graph_signals,
        "linked_account_counts": {
            "device": device_count,
            "ip": ip_count,
            "card": card_count,
            "email": email_count
        }
    }