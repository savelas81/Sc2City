from typing import TYPE_CHECKING

from sc2.unit import Unit
from sc2.units import Units

if TYPE_CHECKING:
    from Sc2City import Sc2City


class SCVManager:
    def __init__(self, bot: "Sc2City"):
        self.bot = bot
        self.mineral_collector_dict: dict[int, int] = {}
        self.vespene_collector_dict: dict[int, int] = {}

    def worker_split_frame_zero(self) -> None:
        mineral_fields = self.bot.mineral_field.closer_than(
            distance=10, position=self.bot.start_location
        )
        workers = Units(self.bot.workers, self.bot)
        for mineral_field in mineral_fields:
            worker = workers.closest_to(mineral_field)
            self.__assign_worker_to_mineral_field(worker, mineral_field)
            workers.remove(worker)

        for worker in workers:
            mineral_field = mineral_fields.closest_to(worker)
            self.__assign_worker_to_mineral_field(worker, mineral_field)

    def __assign_worker_to_mineral_field(
        self, worker: Unit, mineral_field: Unit
    ) -> None:
        worker.gather(mineral_field)
        self.mineral_collector_dict[worker.tag] = mineral_field.tag
