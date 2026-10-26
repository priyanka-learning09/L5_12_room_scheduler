"""Conference room and equipment scheduler.

Books rooms for time slots, allocates shared equipment, logs double
bookings and exports the schedule to JSON.
"""
import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

SLOT_PATTERN = re.compile(r"^(\d{2})-(\d{2})$")
DEFAULT_EQUIPMENT = {"projector": 2, "microphone": 4, "webcam": 1}


def parse_slot(time_slot):
    """Return (start, end) hours for a 'HH-HH' slot, or raise ValueError."""
    if not isinstance(time_slot, str):
        raise ValueError(f"Slot must be text like '09-11', got {time_slot!r}")
    match = SLOT_PATTERN.match(time_slot)
    if not match:
        raise ValueError(f"Slot must look like '09-11', got {time_slot!r}")
    start, end = int(match.group(1)), int(match.group(2))
    if not 0 <= start < end <= 24:
        raise ValueError(
            f"Slot must start before it ends within 00-24, got {time_slot!r}"
        )
    return start, end


def slot_hours(time_slot):
    """Return the length of a slot in hours."""
    start, end = parse_slot(time_slot)
    return end - start


class RoomScheduler:
    """Holds reservations, the equipment pool and logged conflicts."""

    def __init__(self, equipment=None):
        self.reservations = {}
        self.equipment_pool = dict(equipment or DEFAULT_EQUIPMENT)
        self.conflicts = []
        self._next_id = 1

    def schedule_room(self, room_id, time_slot, equipment_list=None):
        """Book a room. Returns the reservation id, or None on a conflict.

        Raises ValueError for a bad slot, unknown equipment, or equipment
        that is not available. Nothing is changed if an error is raised.
        """
        parse_slot(time_slot)
        wanted = list(equipment_list or [])
        self._check_equipment(wanted)

        for existing in self.reservations.values():
            if existing["room"] == room_id and existing["slot"] == time_slot:
                self.conflicts.append(
                    f"{room_id} double-booked at {time_slot}"
                )
                return None

        for item in wanted:
            self.equipment_pool[item] -= 1
        reservation_id = self._next_id
        self._next_id += 1
        self.reservations[reservation_id] = {
            "room": room_id,
            "slot": time_slot,
            "equipment": wanted,
        }
        return reservation_id

    def _check_equipment(self, wanted):
        """Raise ValueError if the request cannot be satisfied."""
        for item in set(wanted):
            if item not in self.equipment_pool:
                raise ValueError(f"Unknown equipment: {item!r}")
            if wanted.count(item) > self.equipment_pool[item]:
                raise ValueError(f"Not enough {item} available")

    def cancel_reservation(self, reservation_id):
        """Cancel a reservation and return its equipment. True if found."""
        reservation = self.reservations.pop(reservation_id, None)
        if reservation is None:
            logger.warning(
                "No reservation with id %s to cancel", reservation_id
            )
            return False
        for item in reservation["equipment"]:
            self.equipment_pool[item] += 1
        return True

    def export_schedule(self, file="schedule.json"):
        """Write all reservations to a JSON file."""
        with open(file, "w", encoding="utf-8") as handle:
            json.dump(self.reservations, handle)

    def log_conflicts(self, file="conflicts.log"):
        """Append conflicts to a log file and print the log."""
        with open(file, "a", encoding="utf-8") as handle:
            for conflict in self.conflicts:
                handle.write(f"{datetime.now()} {conflict}\n")
        self.conflicts.clear()
        with open(file, "r", encoding="utf-8") as handle:
            print(handle.read(), end="")


def main():
    """Run the demo scenario."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    scheduler = RoomScheduler()

    scheduler.schedule_room("Board-1", "09-11")
    scheduler.schedule_room("Board-1", "09-11")  # logged as a conflict
    huddle = scheduler.schedule_room("Huddle-3", "14-16")
    print("Slot length for Huddle-3:", slot_hours(
        scheduler.reservations[huddle]["slot"]))

    for bad_slot in ("14-12", 1530):
        try:
            scheduler.schedule_room("Huddle-3", bad_slot)
        except ValueError as error:
            logger.error("Rejected booking: %s", error)

    scheduler.cancel_reservation(77)

    slot = input("Slot for Board-2, like 10-12 (Enter for 10-12): ") or "10-12"
    try:
        scheduler.schedule_room(
            "Board-2", slot.strip(), ["projector", "webcam"]
        )
    except ValueError as error:
        logger.error("Could not book Board-2: %s", error)

    scheduler.export_schedule()
    scheduler.log_conflicts()
    print("Equipment left:", scheduler.equipment_pool)
    print("Reservations:", scheduler.reservations)


if __name__ == "__main__":
    main()
