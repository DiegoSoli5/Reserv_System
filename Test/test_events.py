import pytest


@pytest.mark.parametrize("title, description, location, total_tickets", [
    ("title1", "desc1", "loc1", 15),
    ("title2", "desc2", None, 100),
    (None, "desc3", "loc3", 11)
    ])
def test_event_update(autAdmin, test_event, title, description, location, total_tickets):
    res = autAdmin.patch(f"/event/{test_event.id}", json={"title":title, "description":description, "location":location, "total_tickets":total_tickets})
    
    assert res.status_code == 200
    
    
def test_event_delete(autAdmin, test_event):
    res = autAdmin.delete(f"/event/{test_event.id}")
    
    assert res.status_code == 204