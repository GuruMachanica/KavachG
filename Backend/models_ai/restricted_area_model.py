# restricted_area_model.py - Virtual Perimeter Polygon Intrusion Detection

# Global list of active danger zone polygons: list of [{"name": str, "points": [[x,y], ...]}]
_active_zones = []
restricted_model = True



def detect_restricted_area(img):
    """Detects persons entering active danger perimeter polygons."""
    from ppe_model import detect_ppe
    person_detections = [d for d in detect_ppe(img) if d.get("label", "").lower() == "person"]
    intrusions = check_zone_intrusions(person_detections)
    return intrusions



def set_active_zones(zones: list):
    global _active_zones
    _active_zones = zones


def get_active_zones() -> list:
    return _active_zones


def is_point_inside_polygon(point, polygon):
    """Ray-casting algorithm to test if point (x,y) is within polygon vertices."""
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def check_zone_intrusions(person_boxes: list, zones: list = None) -> list:
    """Checks if any worker foot-point or bounding box center enters restricted polygon zones."""
    if zones is None:
        zones = _active_zones

    violations = []
    for person in person_boxes:
        bbox = person.get("bbox")
        if not bbox or len(bbox) < 4:
            continue

        x1, y1, x2, y2 = bbox
        # Test worker ground position (bottom center of bounding box)
        foot_point = ((x1 + x2) / 2.0, y2)

        for zone in zones:
            pts = zone.get("points", [])
            if len(pts) < 3:
                continue

            if is_point_inside_polygon(foot_point, pts):
                violations.append(
                    {
                        "zone_name": zone.get("name", "Restricted Area"),
                        "worker_bbox": bbox,
                        "foot_point": [int(foot_point[0]), int(foot_point[1])],
                        "confidence": person.get("confidence", 0.9),
                    }
                )
    return violations

