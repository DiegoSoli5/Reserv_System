from app import schemas

def test_cancell_booking(autClient, test_booking):
    res = autClient.delete(f"/booking/{test_booking.id}")
    
    assert res.status_code == 204

    booking_res = autClient.get(f"/booking/{test_booking.id}")
    assert booking_res.status_code == 200
    assert booking_res.json()["status"] == "CANCELLED"
    
    