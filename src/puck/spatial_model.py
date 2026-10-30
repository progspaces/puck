from dataclasses import dataclass
import chorus
import importlib

from .geometry import Polygon 


@dataclass
class PaperRecord:
    encoding: int 
    tags: list[Polygon]

def load_program_names(filename: str) -> list[str]:
    """Loads and returns a list of the names of existing programs.

    This list is ordered such that a program can be indexed by its encoding.

    Args:
        filename: Filename to load from.
    """
    with open(filename) as f:
        programs = json.load(f)
    assert type(programs) is list
    assert all(type(p) is str for p in programs)
    return programs

program_lookup = load_program_names(program_lookup_file)


@dataclass 
class SpatialModel:
    encoding_to_paper_record: dict[int, PaperRecord] = {}
    actor_id_to_paper_record: dict[chorus.ActorID, PaperRecord] = {}
    encoding_to_actor_id: dict[int, chorus.ActorID] = {}
    
    def update(self, visible_papers:list[PaperRecord]):
        actor_id_to_seen: dict[chorus.ActorID, bool] = {aid:False for aid in self.actor_id_to_paper_record}
        for paper in visible_papers:
            if paper.encoding not in self.encoding_to_paper_record:
                module_name = "puck.programs." + program_lookup[paper.encoding]
                module = importlib.import_module(module_name)
                aid = chorus.spawn(target=module.run)
                self.actor_id_to_paper_record[aid] = paper
                self.encoding_to_paper_record[paper.encoding] = paper
                self.encoding_to_actor_id[paper.encoding] = aid
                actor_id_to_seen[aid] = True
            else:
                aid= self.encoding_to_actor_id[paper.encoding]
                actor_id_to_seen[aid] = True
        for aid in [aid for aid, seen in actor_id_to_seen.items() if not seen]:
            #aid.kill #something we havent' implemented yet
            print(f"Die, {aid}")

            
            




