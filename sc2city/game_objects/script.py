from sc2.position import Point2


class Script:
    id: str  # TODO: Create a list of scripts and connect this to the options
    target: Point2
    status: str  # TODO: Enumerate the possible values (possibly: "pending", "running", "completed")
    comment: str
